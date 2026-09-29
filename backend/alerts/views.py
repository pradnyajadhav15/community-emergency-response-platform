from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.models import EmergencyContact
from incidents.models import IncidentMessage, ResponderAssignment

from .models import AlertNotification, SOSAlert
from .serializers import (
    AlertNotificationSerializer,
    SOSAlertSerializer,
    SOSCreateSerializer,
)
from .services import dispatch_initial, escalate

FINISHED = (SOSAlert.Status.RESOLVED, SOSAlert.Status.CLOSED, SOSAlert.Status.CANCELLED)


def is_admin(user):
    return user.is_staff or user.role == "ADMIN"


def is_coordinator(user):
    """Security staff and administrators coordinate every incident in their scope."""
    return is_admin(user) or user.role == "SECURITY"


def reject(message, code=status.HTTP_403_FORBIDDEN):
    return Response({"detail": message}, status=code)


class SOSAlertViewSet(viewsets.ModelViewSet):
    serializer_class = SOSAlertSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "head", "options"]

    def get_serializer_class(self):
        return SOSCreateSerializer if self.action == "create" else SOSAlertSerializer

    def get_queryset(self):
        user = self.request.user
        qs = SOSAlert.objects.select_related("resident", "society", "flat", "responder")

        if is_admin(user):
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
        if alert.resident_id == request.user.id:
            return reject("Responders acknowledge alerts, not the resident who raised them.")
        if alert.status in FINISHED:
            return reject("This incident is already finished.", status.HTTP_400_BAD_REQUEST)
        if alert.status == SOSAlert.Status.OPEN:
            alert.status = SOSAlert.Status.ACKNOWLEDGED
        alert.acknowledged_at = alert.acknowledged_at or timezone.now()
        alert.save(update_fields=["status", "acknowledged_at"])
        return Response(SOSAlertSerializer(alert).data)

    @action(detail=True, methods=["post"])
    def accept(self, request, pk=None):
        alert = self.get_object()
        if alert.resident_id == request.user.id:
            return reject("You cannot respond to your own alert.", status.HTTP_400_BAD_REQUEST)
        if alert.status in FINISHED:
            return reject("This incident is already finished.", status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            # Row lock: two simultaneous accepts cannot both succeed.
            alert = SOSAlert.objects.select_for_update().get(pk=alert.pk)
            if alert.responder_id and alert.responder_id != request.user.id:
                return reject(
                    f"Already accepted by {alert.responder.username}.", status.HTTP_409_CONFLICT
                )
            alert.responder = request.user
            alert.status = SOSAlert.Status.IN_PROGRESS
            alert.acknowledged_at = alert.acknowledged_at or timezone.now()
            alert.save(update_fields=["responder", "status", "acknowledged_at"])

            ResponderAssignment.objects.update_or_create(
                alert=alert, responder=request.user,
                defaults={"status": ResponderAssignment.Status.ACCEPTED},
            )
            IncidentMessage.objects.create(
                alert=alert, sender=request.user, is_system=True,
                body=f"{request.user.username} accepted and is responding.",
            )
        return Response(SOSAlertSerializer(alert).data)

    @action(detail=True, methods=["post"])
    def escalate(self, request, pk=None):
        alert = self.get_object()
        if not is_coordinator(request.user):
            return reject("Only security staff or administrators can escalate.")
        if alert.status in FINISHED:
            return reject("This incident is already finished.", status.HTTP_400_BAD_REQUEST)
        sent = escalate(alert)
        data = SOSAlertSerializer(alert).data
        data["notifications_sent"] = len(sent)
        return Response(data)

    @action(detail=True, methods=["post"])
    def resolve(self, request, pk=None):
        alert = self.get_object()
        user = request.user
        involved = user.id in (alert.resident_id, alert.responder_id) or is_coordinator(user)
        if not involved:
            return reject("Only the resident, the responder, or coordinators can resolve.")
        if alert.status in FINISHED:
            return reject("This incident is already finished.", status.HTTP_400_BAD_REQUEST)

        alert.status = SOSAlert.Status.RESOLVED
        alert.resolved_at = timezone.now()
        alert.resolution_notes = str(request.data.get("resolution_notes", ""))[:2000]
        alert.save(update_fields=["status", "resolved_at", "resolution_notes"])
        ResponderAssignment.objects.filter(alert=alert, responder_id=alert.responder_id).update(
            status=ResponderAssignment.Status.COMPLETED
        )
        return Response(SOSAlertSerializer(alert).data)

    @action(detail=True, methods=["post"])
    def close(self, request, pk=None):
        alert = self.get_object()
        if not is_coordinator(request.user):
            return reject("Only security staff or administrators can close incidents.")
        if alert.status != SOSAlert.Status.RESOLVED:
            return reject("Resolve the incident before closing it.", status.HTTP_400_BAD_REQUEST)
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
        qs = self.get_queryset().exclude(status__in=FINISHED)
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