from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from .models import EmergencyContact

User = get_user_model()


class AuthTests(APITestCase):
    def test_register_creates_user_with_role(self):
        response = self.client.post("/api/auth/register/", {
            "username": "newresident", "email": "n@test.com",
            "password": "Cerp@2026Pass", "password2": "Cerp@2026Pass",
            "role": "RESIDENT", "phone": "9111111111",
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.get(username="newresident").role, "RESIDENT")

    def test_register_rejects_password_mismatch(self):
        response = self.client.post("/api/auth/register/", {
            "username": "baduser", "password": "Cerp@2026Pass",
            "password2": "Different@2026", "role": "RESIDENT",
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_returns_token_with_role(self):
        User.objects.create_user(username="loginuser", password="Cerp@2026Pass", role="VOLUNTEER")
        response = self.client.post("/api/auth/login/", {
            "username": "loginuser", "password": "Cerp@2026Pass",
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertEqual(response.data["user"]["role"], "VOLUNTEER")

    def test_me_requires_authentication(self):
        self.assertEqual(self.client.get("/api/auth/me/").status_code, status.HTTP_401_UNAUTHORIZED)


class EmergencyContactTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="res", password="Cerp@2026Pass", role="RESIDENT"
        )
        self.client.force_authenticate(self.user)

    def test_create_and_list_contact(self):
        response = self.client.post("/api/auth/emergency-contacts/", {
            "full_name": "Guardian One", "phone": "9222222222",
            "escalation_level": 1, "order": 1,
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.client.get("/api/auth/emergency-contacts/").data["count"], 1)

    def test_duplicate_slot_rejected(self):
        payload = {"full_name": "A", "phone": "9333333333", "escalation_level": 1, "order": 1}
        self.client.post("/api/auth/emergency-contacts/", payload, format="json")
        second = self.client.post("/api/auth/emergency-contacts/", payload, format="json")
        self.assertEqual(second.status_code, status.HTTP_400_BAD_REQUEST)

    def test_contacts_are_private_to_owner(self):
        EmergencyContact.objects.create(
            resident=self.user, full_name="Mine", phone="9444444444"
        )
        other = User.objects.create_user(username="other", password="Cerp@2026Pass")
        self.client.force_authenticate(other)
        self.assertEqual(self.client.get("/api/auth/emergency-contacts/").data["count"], 0)

    def test_availability_toggle(self):
        response = self.client.post(
            "/api/auth/availability/", {"is_available": False}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_available)
