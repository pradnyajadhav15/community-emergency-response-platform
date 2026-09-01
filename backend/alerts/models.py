from django.conf import settings
from django.db import models


class SOSAlert(models.Model):
    class Category(models.TextChoices):
        MEDICAL = "MEDICAL", "Medical Emergency"
        FIRE = "FIRE", "Fire"
        SECURITY = "SECURITY", "Security Threat"
        ACCIDENT = "ACCIDENT", "Accident"
        FALL = "FALL", "Fall Detected"
        OTHER = "OTHER", "Other"

    class Status(models.TextChoices):
        OPEN = "OPEN", "Open"
        ACKNOWLEDGED = "ACKNOWLEDGED", "Acknowledged"
        IN_PROGRESS = "IN_PROGRESS", "Response In Progress"
        ESCALATED = "ESCALATED", "Escalated"
        RESOLVED = "RESOLVED", "Resolved"
        CLOSED = "CLOSED", "Closed"
        CANCELLED = "CANCELLED", "Cancelled"

    resident = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sos_alerts"
    )
    society = models.ForeignKey(
        "societies.Society", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="sos_alerts",
    )
    flat = models.ForeignKey(
        "societies.Flat", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="sos_alerts",
    )
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.MEDICAL)
    message = models.TextField(blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    address = models.CharField(max_length=255, blank=True)

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    escalation_level = models.PositiveSmallIntegerField(default=1)
    responder = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="responding_to",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    escalated_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"SOS #{self.pk} {self.resident.username} [{self.status}]"

    @property
    def is_active(self):
        return self.status not in (self.Status.RESOLVED, self.Status.CLOSED, self.Status.CANCELLED)


class AlertNotification(models.Model):
    class Channel(models.TextChoices):
        PUSH = "PUSH", "Push"
        SMS = "SMS", "SMS"
        EMAIL = "EMAIL", "Email"
        IN_APP = "IN_APP", "In-App"

    class Audience(models.TextChoices):
        PRIMARY_GUARDIAN = "PRIMARY_GUARDIAN", "Primary Guardian"
        SECONDARY_GUARDIAN = "SECONDARY_GUARDIAN", "Secondary Guardian"
        EMERGENCY_CONTACT = "EMERGENCY_CONTACT", "Emergency Contact"
        SECURITY = "SECURITY", "Security Personnel"
        VOLUNTEER = "VOLUNTEER", "Volunteer"
        COMMUNITY = "COMMUNITY", "Community Broadcast"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        SENT = "SENT", "Sent"
        FAILED = "FAILED", "Failed"
        READ = "READ", "Read"

    alert = models.ForeignKey(SOSAlert, on_delete=models.CASCADE, related_name="notifications")
    recipient_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True,
        related_name="alert_notifications",
    )
    recipient_contact = models.ForeignKey(
        "accounts.EmergencyContact", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="alert_notifications",
    )
    recipient_label = models.CharField(max_length=150, blank=True)
    audience = models.CharField(max_length=25, choices=Audience.choices)
    channel = models.CharField(max_length=10, choices=Channel.choices)
    title = models.CharField(max_length=150)
    body = models.TextField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    error = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.channel} -> {self.recipient_label} ({self.status})"
