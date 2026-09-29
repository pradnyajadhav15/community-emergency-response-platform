"""Endpoint an external scheduler calls to run escalations without shell access."""
import io

from django.conf import settings
from django.core.management import call_command
from django.utils.crypto import constant_time_compare
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def run_escalations(request):
    expected = getattr(settings, "CRON_TOKEN", "")
    supplied = request.headers.get("X-Cron-Token", "")
    if not expected:
        return Response({"detail": "Scheduler is not configured."},
                        status=status.HTTP_503_SERVICE_UNAVAILABLE)
    if not constant_time_compare(supplied, expected):
        return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)

    output = io.StringIO()
    call_command("run_escalations", stdout=output)
    return Response({"detail": "ok", "log": output.getvalue().splitlines()})