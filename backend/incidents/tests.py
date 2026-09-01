from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from alerts.models import SOSAlert
from societies.models import Society

from .models import IncidentMessage, ResponderAssignment

User = get_user_model()


class IncidentThreadTests(APITestCase):
    def setUp(self):
        self.society = Society.objects.create(name="Test Society", code="TS001")
        self.resident = User.objects.create_user(
            username="res", password="Cerp@2026Pass", role="RESIDENT", society=self.society
        )
        self.volunteer = User.objects.create_user(
            username="vol", password="Cerp@2026Pass", role="VOLUNTEER", society=self.society
        )
        self.alert = SOSAlert.objects.create(resident=self.resident, society=self.society)

    def test_post_and_read_message(self):
        self.client.force_authenticate(self.volunteer)
        post = self.client.post("/api/incidents/messages/", {
            "alert": self.alert.pk, "body": "On my way",
        }, format="json")
        self.assertEqual(post.status_code, status.HTTP_201_CREATED)
        self.assertEqual(post.data["sender_name"], "vol")

        self.client.force_authenticate(self.resident)
        thread = self.client.get(f"/api/incidents/messages/?alert={self.alert.pk}")
        self.assertEqual(thread.data["count"], 1)

    def test_stranger_cannot_read_thread(self):
        IncidentMessage.objects.create(
            alert=self.alert, sender=self.resident, body="Private"
        )
        stranger = User.objects.create_user(
            username="stranger", password="Cerp@2026Pass", role="RESIDENT"
        )
        self.client.force_authenticate(stranger)
        response = self.client.get(f"/api/incidents/messages/?alert={self.alert.pk}")
        self.assertEqual(response.data["count"], 0)

    def test_on_site_status_posts_system_message(self):
        assignment = ResponderAssignment.objects.create(
            alert=self.alert, responder=self.volunteer
        )
        self.client.force_authenticate(self.volunteer)
        response = self.client.post(
            f"/api/incidents/assignments/{assignment.pk}/set-status/",
            {"status": "ON_SITE"}, format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            IncidentMessage.objects.filter(alert=self.alert, is_system=True).exists()
        )

    def test_invalid_status_rejected(self):
        assignment = ResponderAssignment.objects.create(
            alert=self.alert, responder=self.volunteer
        )
        self.client.force_authenticate(self.volunteer)
        response = self.client.post(
            f"/api/incidents/assignments/{assignment.pk}/set-status/",
            {"status": "NONSENSE"}, format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
