from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import EmergencyContact
from societies.models import Block, Flat, ResidentProfile, Society

from .models import AlertNotification, SOSAlert
from .services import escalate

User = get_user_model()


class SOSWorkflowTests(APITestCase):
    def setUp(self):
        self.society = Society.objects.create(name="Test Society", code="TS001")
        block = Block.objects.create(society=self.society, name="A Wing")
        self.flat = Flat.objects.create(block=block, flat_number="A-101")

        self.resident = User.objects.create_user(
            username="res", password="Cerp@2026Pass", role="RESIDENT",
            society=self.society, phone="9111111111",
        )
        ResidentProfile.objects.create(user=self.resident, flat=self.flat)

        self.guardian = User.objects.create_user(
            username="guard", password="Cerp@2026Pass", role="GUARDIAN",
            society=self.society,
        )
        self.volunteer = User.objects.create_user(
            username="vol", password="Cerp@2026Pass", role="VOLUNTEER",
            society=self.society,
        )

        EmergencyContact.objects.create(
            resident=self.resident, full_name="Primary G", phone="9222222222",
            escalation_level=1, order=1, linked_user=self.guardian,
        )
        EmergencyContact.objects.create(
            resident=self.resident, full_name="Secondary G", phone="9333333333",
            escalation_level=2, order=1,
        )

    def _raise_sos(self):
        self.client.force_authenticate(self.resident)
        return self.client.post("/api/sos/", {
            "category": "MEDICAL", "message": "Need help",
            "latitude": 18.52, "longitude": 73.85,
        }, format="json")

    def test_sos_creation_attaches_flat_and_society(self):
        response = self._raise_sos()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        alert = SOSAlert.objects.get(pk=response.data["id"])
        self.assertEqual(alert.society, self.society)
        self.assertEqual(alert.flat, self.flat)
        self.assertEqual(alert.status, SOSAlert.Status.OPEN)

    def test_sos_notifies_guardian_and_volunteer(self):
        response = self._raise_sos()
        audiences = set(
            AlertNotification.objects.filter(alert_id=response.data["id"])
            .values_list("audience", flat=True)
        )
        self.assertIn(AlertNotification.Audience.PRIMARY_GUARDIAN, audiences)
        self.assertIn(AlertNotification.Audience.VOLUNTEER, audiences)

    def test_volunteer_accept_assigns_responder(self):
        alert_id = self._raise_sos().data["id"]
        self.client.force_authenticate(self.volunteer)
        response = self.client.post(f"/api/sos/{alert_id}/accept/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], SOSAlert.Status.IN_PROGRESS)
        self.assertEqual(response.data["responder_name"], "vol")

    def test_second_responder_gets_conflict(self):
        alert_id = self._raise_sos().data["id"]
        self.client.force_authenticate(self.volunteer)
        self.client.post(f"/api/sos/{alert_id}/accept/")
        self.client.force_authenticate(self.guardian)
        response = self.client.post(f"/api/sos/{alert_id}/accept/")
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_escalation_moves_to_next_tier(self):
        alert = SOSAlert.objects.create(
            resident=self.resident, society=self.society, flat=self.flat,
            category=SOSAlert.Category.FALL,
        )
        escalate(alert)
        alert.refresh_from_db()
        self.assertEqual(alert.escalation_level, 2)
        self.assertEqual(alert.status, SOSAlert.Status.ESCALATED)
        self.assertTrue(
            AlertNotification.objects.filter(
                alert=alert, audience=AlertNotification.Audience.SECONDARY_GUARDIAN
            ).exists()
        )

    def test_escalation_stops_at_level_three(self):
        alert = SOSAlert.objects.create(
            resident=self.resident, society=self.society, escalation_level=3
        )
        self.assertEqual(escalate(alert), [])

    def test_resolve_sets_timestamp(self):
        alert_id = self._raise_sos().data["id"]
        response = self.client.post(
            f"/api/sos/{alert_id}/resolve/",
            {"resolution_notes": "Handled"}, format="json",
        )
        self.assertEqual(response.data["status"], SOSAlert.Status.RESOLVED)
        self.assertIsNotNone(response.data["resolved_at"])

    def test_resident_cannot_see_other_residents_alerts(self):
        self._raise_sos()
        stranger = User.objects.create_user(
            username="stranger", password="Cerp@2026Pass", role="RESIDENT"
        )
        self.client.force_authenticate(stranger)
        self.assertEqual(self.client.get("/api/sos/").data["count"], 0)

    def test_dashboard_stats_returns_counts(self):
        self._raise_sos()
        response = self.client.get("/api/dashboard/stats/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_alerts"], 1)
        self.assertEqual(response.data["active_alerts"], 1)
