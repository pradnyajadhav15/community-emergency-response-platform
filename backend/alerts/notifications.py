"""Notification delivery. Push is real; SMS is a console stub until Twilio is wired in."""
import json

import requests
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from .models import AlertNotification


def _mark(notification, ok, error=""):
    notification.status = (
        AlertNotification.Status.SENT if ok else AlertNotification.Status.FAILED
    )
    notification.error = error[:500]
    notification.sent_at = timezone.now()
    notification.save(update_fields=["status", "error", "sent_at"])


def send_push(notification, token):
    if not token:
        _mark(notification, False, "No push token on file.")
        return
    payload = {
        "to": token,
        "sound": "default",
        "title": notification.title,
        "body": notification.body,
        "priority": "high",
        "data": {"alert_id": notification.alert_id},
    }
    try:
        response = requests.post(
            settings.EXPO_PUSH_URL,
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"},
            timeout=10,
        )
        _mark(notification, response.status_code == 200, response.text)
    except Exception as exc:
        _mark(notification, False, str(exc))


def send_sms(notification, phone):
    if not phone:
        _mark(notification, False, "No phone number on file.")
        return
    print(f"[SMS] to {phone}: {notification.title} - {notification.body}")
    _mark(notification, True)


def send_email(notification, email):
    if not email:
        _mark(notification, False, "No email on file.")
        return
    try:
        send_mail(
            notification.title,
            notification.body,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
        _mark(notification, True)
    except Exception as exc:
        _mark(notification, False, str(exc))


def deliver(notification):
    user = notification.recipient_user
    contact = notification.recipient_contact
    channel = notification.channel

    if channel == AlertNotification.Channel.IN_APP:
        _mark(notification, True)
    elif channel == AlertNotification.Channel.PUSH:
        send_push(notification, user.expo_push_token if user else "")
    elif channel == AlertNotification.Channel.SMS:
        send_sms(notification, user.phone if user else (contact.phone if contact else ""))
    elif channel == AlertNotification.Channel.EMAIL:
        send_email(notification, user.email if user else (contact.email if contact else ""))
