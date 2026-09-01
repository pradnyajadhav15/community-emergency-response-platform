"""Builds the recipient list for an alert and fans notifications out."""
from django.contrib.auth import get_user_model
from django.utils import timezone

from accounts.models import EmergencyContact

from .models import AlertNotification, SOSAlert
from .notifications import deliver

User = get_user_model()

LEVEL_TO_AUDIENCE = {
    1: AlertNotification.Audience.PRIMARY_GUARDIAN,
    2: AlertNotification.Audience.SECONDARY_GUARDIAN,
    3: AlertNotification.Audience.EMERGENCY_CONTACT,
}


def _text(alert):
    who = alert.resident.get_full_name() or alert.resident.username
    where = str(alert.flat) if alert.flat else (alert.address or "location not shared")
    title = f"SOS: {alert.get_category_display()}"
    body = f"{who} needs help at {where}. {alert.message}".strip()
    return title, body


def _create(alert, audience, channel, user=None, contact=None, label=""):
    title, body = _text(alert)
    notification = AlertNotification.objects.create(
        alert=alert,
        recipient_user=user,
        recipient_contact=contact,
        recipient_label=label or (user.username if user else (contact.full_name if contact else "")),
        audience=audience,
        channel=channel,
        title=title,
        body=body,
    )
    deliver(notification)
    return notification


def notify_contacts(alert, level):
    """Notify guardians / emergency contacts at one escalation level."""
    audience = LEVEL_TO_AUDIENCE.get(level, AlertNotification.Audience.EMERGENCY_CONTACT)
    created = []
    contacts = EmergencyContact.objects.filter(
        resident=alert.resident, escalation_level=level
    ).select_related("linked_user")

    for contact in contacts:
        if contact.linked_user:
            created.append(_create(alert, audience, AlertNotification.Channel.PUSH,
                                   user=contact.linked_user, label=contact.full_name))
            created.append(_create(alert, audience, AlertNotification.Channel.IN_APP,
                                   user=contact.linked_user, label=contact.full_name))
        created.append(_create(alert, audience, AlertNotification.Channel.SMS,
                               contact=contact, label=contact.full_name))
        if contact.email:
            created.append(_create(alert, audience, AlertNotification.Channel.EMAIL,
                                   contact=contact, label=contact.full_name))
    return created


def notify_society(alert):
    """Security, then available volunteers, then a community broadcast."""
    created = []
    if not alert.society_id:
        return created

    groups = [
        (User.Role.SECURITY, AlertNotification.Audience.SECURITY, False),
        (User.Role.VOLUNTEER, AlertNotification.Audience.VOLUNTEER, True),
        (User.Role.RESIDENT, AlertNotification.Audience.COMMUNITY, False),
    ]

    for role, audience, only_available in groups:
        qs = User.objects.filter(society_id=alert.society_id, role=role, is_active=True)
        if only_available:
            qs = qs.filter(is_available=True)
        for user in qs.exclude(pk=alert.resident_id):
            created.append(_create(alert, audience, AlertNotification.Channel.PUSH, user=user))
            created.append(_create(alert, audience, AlertNotification.Channel.IN_APP, user=user))
    return created


def dispatch_initial(alert):
    """Full fan-out when an SOS is first raised."""
    sent = notify_contacts(alert, level=1)
    sent += notify_society(alert)
    return sent


def escalate(alert):
    """Move the alert to the next escalation level and notify that tier."""
    if alert.escalation_level >= 3:
        return []
    alert.escalation_level += 1
    alert.status = SOSAlert.Status.ESCALATED
    alert.escalated_at = timezone.now()
    alert.save(update_fields=["escalation_level", "status", "escalated_at"])
    return notify_contacts(alert, level=alert.escalation_level)
