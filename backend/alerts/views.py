from django.db.models import Q
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.models import EmergencyContact

from .models import AlertNotification, SOSAlert
from .serializers import (
    AlertNotificationSerializer,
    SOSAlertSerializer,
    SOSCreateSerializer,
)
from .services import dispatch_initial, escalate


class SOSAlertViewSet(viewsets.ModelViewSet):
    serializer_class = SOSAlertSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        return SOSCreateSerializer if self.action == "create" else SOSAlertSerializer

    def get_queryset(self):
        user = self.request.user
        qs = SOSAlert.objects.select_related("resident", "society", "flat", "responder")

        if user.is_staff or user.role == "ADMIN":
            return qs
        if user.role in ("SECURITY", "VOLUNTEER"):
            return qs.filter(society_id=user.society_id)

        guarded_ids = EmergencyContact.objects.filter(
            linked_user=user
        ).values_list("resident_id", flat=True)
        return qs.filter(Q(resident=user) | Q(resident_id__in=guarded_ids))

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        profile = getattr(request.user, "resident_profile", None)
        flat = profile.flat if profile else None
        society = flat.block.society if flat else request.user.society

        alert = SOSAlert.objects.create(
            resident=request.user, flat=flat, society=society, **serializer.validated_data
        )
        sent = dispatch_initial(alert)
        data = SOSAlertSerializer(alert).data
        data["notifications_sent"] = len(sent)
        return Response(data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def acknowledge(self, request, pk=None):
        alert = self.get_object()
        alert.status = SOSAlert.Status.ACKNOWLEDGED
        alert.acknowledged_at = timezone.now()
        alert.save(update_fields=["status", "acknowledged_at"])
        return Response(SOSAlertSerializer(alert).data)

    @action(detail=True, methods=["post"])
    def accept(self, request, pk=None):
        alert = self.get_object()
        if alert.responder_id and alert.responder_id != request.user.id:
            return Response(
                {"detail": f"Already accepted by {alert.responder.username}."},
                status=status.HTTP_409_CONFLICT,
            )
        alert.responder = request.user
        alert.status = SOSAlert.Status.IN_PROGRESS
        if not alert.acknowledged_at:
            alert.acknowledged_at = timezone.now()
        alert.save(update_fields=["responder", "status", "acknowledged_at"])
        return Response(SOSAlertSerializer(alert).data)

    @action(detail=True, methods=["post"])
    def escalate(self, request, pk=None):
        alert = self.get_object()
        sent = escalate(alert)
        data = SOSAlertSerializer(alert).data
        data["notifications_sent"] = len(sent)
        return Response(data)

    @action(detail=True, methods=["post"])
    def resolve(self, request, pk=None):
        alert = self.get_object()
        alert.status = SOSAlert.Status.RESOLVED
        alert.resolved_at = timezone.now()
        alert.resolution_notes = request.data.get("resolution_notes", "")
        alert.save(update_fields=["status", "resolved_at", "resolution_notes"])
        return Response(SOSAlertSerializer(alert).data)

    @action(detail=True, methods=["post"])
    def close(self, request, pk=None):
        alert = self.get_object()
        alert.status = SOSAlert.Status.CLOSED
        alert.closed_at = timezone.now()
        alert.save(update_fields=["status", "closed_at"])
        return Response(SOSAlertSerializer(alert).data)

    @action(detail=True, methods=["get"], url_path="notifications")
    def notification_log(self, request, pk=None):
        alert = self.get_object()
        return Response(
            AlertNotificationSerializer(alert.notifications.all(), many=True).data
        )

    @action(detail=False, methods=["get"])
    def active(self, request):
        qs = self.get_queryset().exclude(
            status__in=[
                SOSAlert.Status.RESOLVED,
                SOSAlert.Status.CLOSED,
                SOSAlert.Status.CANCELLED,
            ]
        )
        return Response(SOSAlertSerializer(qs, many=True).data)


class MyNotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AlertNotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return AlertNotification.objects.filter(
            recipient_user=self.request.user, channel=AlertNotification.Channel.IN_APP
        ).select_related("alert")

    @action(detail=True, methods=["post"], url_path="mark-read")
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.status = AlertNotification.Status.READ
        notification.read_at = timezone.now()
        notification.save(update_fields=["status", "read_at"])
        return Response(AlertNotificationSerializer(notification).data)
