from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from alerts.models import SOSAlert
from alerts.views import SOSAlertViewSet

from .models import IncidentMessage, ResponderAssignment
from .serializers import IncidentMessageSerializer, ResponderAssignmentSerializer


def _visible_alert_ids(request):
    view = SOSAlertViewSet()
    view.request = request
    view.action = "list"
    return view.get_queryset().values_list("id", flat=True)


class IncidentMessageViewSet(viewsets.ModelViewSet):
    serializer_class = IncidentMessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = IncidentMessage.objects.filter(
            alert_id__in=_visible_alert_ids(self.request)
        ).select_related("sender", "alert")
        alert = self.request.query_params.get("alert")
        return qs.filter(alert_id=alert) if alert else qs

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)


class ResponderAssignmentViewSet(viewsets.ModelViewSet):
    serializer_class = ResponderAssignmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = ResponderAssignment.objects.filter(
            alert_id__in=_visible_alert_ids(self.request)
        ).select_related("responder", "alert")
        alert = self.request.query_params.get("alert")
        return qs.filter(alert_id=alert) if alert else qs

    @action(detail=True, methods=["post"], url_path="set-status")
    def set_status(self, request, pk=None):
        assignment = self.get_object()
        new_status = request.data.get("status", "").upper()
        valid = [c[0] for c in ResponderAssignment.Status.choices]
        if new_status not in valid:
            return Response(
                {"detail": f"Status must be one of {valid}."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        assignment.status = new_status
        assignment.notes = request.data.get("notes", assignment.notes)
        assignment.save(update_fields=["status", "notes", "updated_at"])

        if new_status == ResponderAssignment.Status.ON_SITE:
            IncidentMessage.objects.create(
                alert=assignment.alert,
                sender=request.user,
                body=f"{request.user.username} has arrived on site.",
                is_system=True,
            )
        return Response(ResponderAssignmentSerializer(assignment).data)
