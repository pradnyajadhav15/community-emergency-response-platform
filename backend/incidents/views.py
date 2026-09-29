from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from alerts.views import SOSAlertViewSet, is_coordinator

from .models import IncidentMessage, ResponderAssignment
from .serializers import IncidentMessageSerializer, ResponderAssignmentSerializer


def visible_alert_ids(request):
    """Reuse the alert visibility rules so incident data never leaks past them."""
    view = SOSAlertViewSet()
    view.request = request
    view.action = "list"
    return set(view.get_queryset().values_list("id", flat=True))


def filter_by_alert(qs, request):
    alert = request.query_params.get("alert")
    if alert is None:
        return qs
    return qs.filter(alert_id=int(alert)) if alert.isdigit() else qs.none()


class IncidentMessageViewSet(viewsets.ModelViewSet):
    serializer_class = IncidentMessageSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "head", "options"]  # messages are an audit trail

    def get_queryset(self):
        qs = IncidentMessage.objects.filter(
            alert_id__in=visible_alert_ids(self.request)
        ).select_related("sender", "alert")
        return filter_by_alert(qs, self.request)

    def perform_create(self, serializer):
        alert = serializer.validated_data["alert"]
        if alert.id not in visible_alert_ids(self.request):
            raise PermissionDenied("You are not part of this incident.")
        serializer.save(sender=self.request.user)


class ResponderAssignmentViewSet(viewsets.ModelViewSet):
    serializer_class = ResponderAssignmentSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "head", "options"]

    def get_queryset(self):
        qs = ResponderAssignment.objects.filter(
            alert_id__in=visible_alert_ids(self.request)
        ).select_related("responder", "alert")
        return filter_by_alert(qs, self.request)

    def perform_create(self, serializer):
        user = self.request.user
        alert = serializer.validated_data["alert"]
        responder = serializer.validated_data["responder"]
        if alert.id not in visible_alert_ids(self.request):
            raise PermissionDenied("You are not part of this incident.")
        if responder != user and not is_coordinator(user):
            raise PermissionDenied("Only coordinators can assign other people.")
        serializer.save()

    @action(detail=True, methods=["post"], url_path="set-status")
    def set_status(self, request, pk=None):
        assignment = self.get_object()
        if assignment.responder_id != request.user.id and not is_coordinator(request.user):
            raise PermissionDenied("Only the assigned responder can update this assignment.")

        new_status = str(request.data.get("status", "")).upper()
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