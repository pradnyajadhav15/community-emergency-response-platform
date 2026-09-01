from django.db.models import Avg, Count, F, Q
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import AlertNotification, SOSAlert


class DashboardStatsView(APIView):
    """Reporting and analytics for the admin portal."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = SOSAlert.objects.all()
        if not (request.user.is_staff or request.user.role == "ADMIN"):
            qs = qs.filter(society_id=request.user.society_id)

        resolved = qs.filter(resolved_at__isnull=False)
        avg_response = resolved.annotate(
            duration=F("resolved_at") - F("created_at")
        ).aggregate(avg=Avg("duration"))["avg"]

        return Response({
            "total_alerts": qs.count(),
            "active_alerts": qs.exclude(
                status__in=[SOSAlert.Status.RESOLVED,
                            SOSAlert.Status.CLOSED,
                            SOSAlert.Status.CANCELLED]
            ).count(),
            "resolved_alerts": resolved.count(),
            "escalated_alerts": qs.filter(escalation_level__gt=1).count(),
            "avg_resolution_seconds": avg_response.total_seconds() if avg_response else None,
            "by_category": list(
                qs.values("category").annotate(count=Count("id")).order_by("-count")
            ),
            "by_status": list(
                qs.values("status").annotate(count=Count("id")).order_by("-count")
            ),
            "notifications": {
                "total": AlertNotification.objects.filter(alert__in=qs).count(),
                "sent": AlertNotification.objects.filter(
                    alert__in=qs, status=AlertNotification.Status.SENT
                ).count(),
                "failed": AlertNotification.objects.filter(
                    alert__in=qs, status=AlertNotification.Status.FAILED
                ).count(),
            },
        })
