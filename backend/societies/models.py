from django.conf import settings
from django.db import models


class Society(models.Model):
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=20, unique=True, help_text="Join code residents use.")
    address = models.TextField(blank=True)
    city = models.CharField(max_length=80, blank=True)
    state = models.CharField(max_length=80, blank=True)
    pincode = models.CharField(max_length=10, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Societies"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Block(models.Model):
    society = models.ForeignKey(Society, on_delete=models.CASCADE, related_name="blocks")
    name = models.CharField(max_length=50, help_text="Block or tower name, e.g. A Wing.")
    total_floors = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["society", "name"]
        constraints = [
            models.UniqueConstraint(fields=["society", "name"], name="uniq_block_per_society")
        ]

    def __str__(self):
        return f"{self.society.name} - {self.name}"


class Flat(models.Model):
    block = models.ForeignKey(Block, on_delete=models.CASCADE, related_name="flats")
    flat_number = models.CharField(max_length=20)
    floor = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["block", "flat_number"]
        constraints = [
            models.UniqueConstraint(fields=["block", "flat_number"], name="uniq_flat_per_block")
        ]

    def __str__(self):
        return f"{self.block} - {self.flat_number}"


class ResidentProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="resident_profile"
    )
    flat = models.ForeignKey(
        Flat, on_delete=models.SET_NULL, null=True, blank=True, related_name="residents"
    )
    is_owner = models.BooleanField(default=True)
    is_senior_citizen = models.BooleanField(default=False)
    notes = models.TextField(blank=True, help_text="Access notes for responders.")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} @ {self.flat or 'unassigned'}"

    @property
    def society(self):
        return self.flat.block.society if self.flat else None
