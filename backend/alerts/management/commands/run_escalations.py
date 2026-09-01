"""Escalate unacknowledged alerts. Run on a schedule, e.g. every minute."""
from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils import timezone

from alerts.models import SOSAlert
from alerts.services import escalate


class Command(BaseCommand):
    help = "Escalate SOS alerts with no response inside the configured window."

    def add_arguments(self, parser):
        parser.add_argument("--minutes", type=int, default=None)

    def handle(self, *args, **options):
        window = options["minutes"] if options["minutes"] is not None else settings.ESCALATION_WINDOW_MINUTES
        cutoff = timezone.now() - timedelta(minutes=window)

        stale = SOSAlert.objects.filter(
            status__in=[SOSAlert.Status.OPEN, SOSAlert.Status.ESCALATED],
            responder__isnull=True,
            escalation_level__lt=3,
        ).filter(
            Q(escalated_at__lte=cutoff)
            | Q(escalated_at__isnull=True, created_at__lte=cutoff)
        )

        count = 0
        for alert in stale:
            sent = escalate(alert)
            count += 1
            self.stdout.write(
                self.style.WARNING(
                    f"Escalated SOS #{alert.pk} to level {alert.escalation_level} "
                    f"({len(sent)} notifications)"
                )
            )
        self.stdout.write(self.style.SUCCESS(f"Done. {count} alert(s) escalated."))
