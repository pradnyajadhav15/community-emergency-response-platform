"""Security tests: authentication, authorization, input handling, concurrency rules."""
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from incidents.models import IncidentMessage, ResponderAssignment
from societies.models import Society

from .models import SOSAlert

User = get_user_model()
PASSWORD = "Cerp@2026Pass"


class SecurityTests(APITestCase):
    def setUp(self):
        self.home = Society.objects.create(name="Home", code="HOME1")
        self.other = Society.objects.create(name="Other", code="OTHER1")

        def make(name, role, society):
            return User.objects.create_user(
                username=name, password=PASSWORD, role=role, society=society
            )

        self.resident = make("res", "RESIDENT", self.home)
        self.stranger = make("stranger", "RESIDENT", self.other)
        self.volunteer = make("vol", "VOLUNTEER", self.home)
        self.volunteer2 = make("vol2", "VOLUNTEER", self.home)
        self.outsider = make("outvol", "VOLUNTEER", self.other)
        self.security = make("sec", "SECURITY", self.home)
        self.alert = SOSAlert.objects.create(resident=self.resident, society=self.home)

    def url(self, action=""):
        suffix = f"{action}/" if action else ""
        return f"/api/sos/{self.alert.pk}/{suffix}"

    def as_user(self, user):
        self.client.force_authenticate(user)

    # --- Authentication -------------------------------------------------

    def test_protected_endpoints_require_authentication(self):
        for path in [
            "/api/auth/me/", "/api/auth/emergency-contacts/", "/api/auth/users/",
            "/api/societies/", "/api/sos/", "/api/notifications/",
            "/api/incidents/messages/", "/api/dashboard/stats/",
        ]:
            self.assertEqual(self.client.get(path).status_code, 401, path)

    def test_forged_token_rejected(self):
        self.client.credentials(HTTP_AUTHORIZATION="Bearer not.a.real.token")
        self.assertEqual(self.client.get("/api/auth/me/").status_code, 401)

    # --- Registration ---------------------------------------------------

    def test_cannot_self_register_as_admin(self):
        response = self.client.post("/api/auth/register/", {
            "username": "sneaky", "password": PASSWORD, "password2": PASSWORD, "role": "ADMIN",
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(username="sneaky").exists())

    def test_weak_password_rejected(self):
        response = self.client.post("/api/auth/register/", {
            "username": "weak", "password": "12345678", "password2": "12345678", "role": "RESIDENT",
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # --- Authorization --------------------------------------------------

    def test_other_society_volunteer_cannot_see_alert(self):
        self.as_user(self.outsider)
        self.assertEqual(self.client.get(self.url()).status_code, 404)

    def test_stranger_cannot_post_into_foreign_thread(self):
        self.as_user(self.stranger)
        response = self.client.post(
            "/api/incidents/messages/", {"alert": self.alert.pk, "body": "hi"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(IncidentMessage.objects.filter(body="hi").exists())

    def test_resident_cannot_accept_own_alert(self):
        self.as_user(self.resident)
        self.assertEqual(self.client.post(self.url("accept")).status_code, 400)

    def test_uninvolved_volunteer_cannot_resolve(self):
        self.as_user(self.volunteer)
        self.client.post(self.url("accept"))
        self.as_user(self.volunteer2)
        self.assertEqual(self.client.post(self.url("resolve")).status_code, 403)

    def test_resident_cannot_escalate_or_close(self):
        self.as_user(self.resident)
        self.assertEqual(self.client.post(self.url("escalate")).status_code, 403)
        self.assertEqual(self.client.post(self.url("close")).status_code, 403)

    def test_security_can_escalate(self):
        self.as_user(self.security)
        response = self.client.post(self.url("escalate"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["escalation_level"], 2)

    def test_cannot_close_unresolved_incident(self):
        self.as_user(self.security)
        self.assertEqual(self.client.post(self.url("close")).status_code, 400)

    def test_only_assigned_responder_updates_assignment(self):
        self.as_user(self.volunteer)
        self.client.post(self.url("accept"))
        assignment = ResponderAssignment.objects.get(alert=self.alert)
        self.as_user(self.volunteer2)
        response = self.client.post(
            f"/api/incidents/assignments/{assignment.pk}/set-status/",
            {"status": "COMPLETED"}, format="json",
        )
        self.assertEqual(response.status_code, 403)

    # --- Workflow integrity ---------------------------------------------

    def test_accept_records_assignment_and_system_message(self):
        self.as_user(self.volunteer)
        self.client.post(self.url("accept"))
        self.assertTrue(ResponderAssignment.objects.filter(
            alert=self.alert, responder=self.volunteer, status="ACCEPTED"
        ).exists())
        self.assertTrue(IncidentMessage.objects.filter(alert=self.alert, is_system=True).exists())

    def test_resolve_completes_assignment(self):
        self.as_user(self.volunteer)
        self.client.post(self.url("accept"))
        self.client.post(self.url("resolve"), {"resolution_notes": "done"}, format="json")
        self.assertEqual(
            ResponderAssignment.objects.get(alert=self.alert).status, "COMPLETED"
        )

    # --- Input handling -------------------------------------------------

    def test_malformed_filters_do_not_crash(self):
        self.as_user(self.security)
        for path in [
            "/api/blocks/?society=1%20OR%201=1",
            "/api/flats/?block=abc",
            "/api/incidents/messages/?alert=../../etc",
        ]:
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200, path)
            self.assertEqual(response.data["count"], 0, path)