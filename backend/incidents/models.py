from django.conf import settings
from django.db import models


class IncidentMessage(models.Model):
    alert = models.ForeignKey(
        "alerts.SOSAlert", on_delete=models.CASCADE, related_name="messages"
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="incident_messages"
    )
    body = models.TextField()
    is_system = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"#{self.alert_id} {self.sender.username}: {self.body[:40]}"


class ResponderAssignment(models.Model):
    class Status(models.TextChoices):
        INVITED = "INVITED", "Invited"
        ACCEPTED = "ACCEPTED", "Accepted"
        DECLINED = "DECLINED", "Declined"
        ON_SITE = "ON_SITE", "On Site"
        COMPLETED = "COMPLETED", "Completed"

    alert = models.ForeignKey(
        "alerts.SOSAlert", on_delete=models.CASCADE, related_name="assignments"
    )
    responder = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="assignments"
    )
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.INVITED)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["alert", "responder"], name="uniq_assignment")
        ]

    def __str__(self):
        return f"#{self.alert_id} {self.responder.username} [{self.status}]"
