from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from societies.models import Block, Flat, ResidentProfile, Society

User = get_user_model()


class SocietyStructureTests(APITestCase):
    def setUp(self):
        self.society = Society.objects.create(name="Test Society", code="TS001")
        self.block = Block.objects.create(society=self.society, name="A Wing")
        self.flat = Flat.objects.create(block=self.block, flat_number="A-101", floor=1)

    def test_flat_string_shows_full_path(self):
        self.assertEqual(str(self.flat), "Test Society - A Wing - A-101")

    def test_resident_profile_resolves_society(self):
        user = User.objects.create_user(username="res", password="Cerp@2026Pass")
        profile = ResidentProfile.objects.create(user=user, flat=self.flat)
        self.assertEqual(profile.society, self.society)

    def test_profile_without_flat_has_no_society(self):
        user = User.objects.create_user(username="res2", password="Cerp@2026Pass")
        self.assertIsNone(ResidentProfile.objects.create(user=user).society)

    def test_non_admin_cannot_create_society(self):
        user = User.objects.create_user(
            username="plain", password="Cerp@2026Pass", role="RESIDENT"
        )
        self.client.force_authenticate(user)
        response = self.client.post(
            "/api/societies/", {"name": "Sneaky", "code": "SN001"}, format="json"
        )
        self.assertEqual(response.status_code, 403)
