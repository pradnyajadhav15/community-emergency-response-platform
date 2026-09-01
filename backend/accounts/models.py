from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        RESIDENT = "RESIDENT", "Resident"
        GUARDIAN = "GUARDIAN", "Guardian"
        VOLUNTEER = "VOLUNTEER", "Volunteer"
        SECURITY = "SECURITY", "Security Personnel"
        ADMIN = "ADMIN", "Society Admin"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.RESIDENT)
    society = models.ForeignKey(
        "societies.Society",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="members",
        help_text="Society this user belongs to. Drives alert routing.",
    )
    phone = models.CharField(max_length=15, blank=True)
    is_phone_verified = models.BooleanField(default=False)
    expo_push_token = models.CharField(max_length=255, blank=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class EmergencyContact(models.Model):
    class Level(models.IntegerChoices):
        PRIMARY_GUARDIAN = 1, "Primary Guardian"
        SECONDARY_GUARDIAN = 2, "Secondary Guardian"
        EMERGENCY_CONTACT = 3, "Emergency Contact"

    resident = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="emergency_contacts",
    )
    linked_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="guarding",
        help_text="Set if this contact is also a registered app user.",
    )
    full_name = models.CharField(max_length=120)
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True)
    relationship = models.CharField(max_length=50, blank=True)
    escalation_level = models.PositiveSmallIntegerField(
        choices=Level.choices, default=Level.PRIMARY_GUARDIAN
    )
    order = models.PositiveIntegerField(default=1)
    is_verified = models.BooleanField(default=False)
    verification_code = models.CharField(max_length=6, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["escalation_level", "order"]
        constraints = [
            models.UniqueConstraint(
                fields=["resident", "escalation_level", "order"],
                name="uniq_contact_slot",
            )
        ]

    def __str__(self):
        return f"{self.full_name} -> {self.resident.username}"
