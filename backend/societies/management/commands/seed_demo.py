"""Seed demo data for the CERP project demo."""
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from accounts.models import EmergencyContact
from societies.models import Block, Flat, ResidentProfile, Society

User = get_user_model()


class Command(BaseCommand):
    help = "Create a demo society with residents, guardians, security and volunteers."

    def handle(self, *args, **options):
        society, _ = Society.objects.get_or_create(
            code="GVR001",
            defaults={"name": "Green Valley Residency", "city": "Pune",
                      "state": "Maharashtra", "pincode": "411001",
                      "latitude": 18.5204, "longitude": 73.8567},
        )
        block, _ = Block.objects.get_or_create(
            society=society, name="A Wing", defaults={"total_floors": 5}
        )
        flat, _ = Flat.objects.get_or_create(
            block=block, flat_number="A-101", defaults={"floor": 1}
        )
        Flat.objects.get_or_create(block=block, flat_number="A-102", defaults={"floor": 1})

        people = [
            ("resident1", "RESIDENT", "9876543210", "Asha"),
            ("guard1", "GUARDIAN", "9000000001", "Vikram"),
            ("secure1", "SECURITY", "9000000002", "Sunil"),
            ("volun1", "VOLUNTEER", "9000000003", "Meera"),
        ]
        users = {}
        for username, role, phone, first in people:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={"email": f"{username}@test.com", "role": role,
                          "phone": phone, "first_name": first},
            )
            if created:
                user.set_password("Cerp@2026Pass")
            user.role = role
            user.society = society
            user.phone = phone
            user.save()
            users[username] = user

        profile, _ = ResidentProfile.objects.get_or_create(user=users["resident1"])
        profile.flat = flat
        profile.is_senior_citizen = True
        profile.save()

        EmergencyContact.objects.get_or_create(
            resident=users["resident1"], escalation_level=1, order=1,
            defaults={"full_name": "Vikram Jadhav", "phone": "9000000001",
                      "email": "guard1@test.com", "relationship": "Son",
                      "linked_user": users["guard1"], "is_verified": True},
        )
        EmergencyContact.objects.get_or_create(
            resident=users["resident1"], escalation_level=2, order=1,
            defaults={"full_name": "Sneha Jadhav", "phone": "9000000004",
                      "email": "sneha@test.com", "relationship": "Daughter",
                      "is_verified": True},
        )
        EmergencyContact.objects.get_or_create(
            resident=users["resident1"], escalation_level=3, order=1,
            defaults={"full_name": "Neighbour Rao", "phone": "9000000005",
                      "relationship": "Neighbour", "is_verified": True},
        )

        self.stdout.write(self.style.SUCCESS(
            "Demo data ready. Passwords: resident1 = Resident@2026 (if new: Cerp@2026Pass), "
            "others = Cerp@2026Pass"
        ))
