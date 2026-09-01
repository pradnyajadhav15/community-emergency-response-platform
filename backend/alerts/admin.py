from django.contrib import admin

from .models import AlertNotification, SOSAlert


class NotificationInline(admin.TabularInline):
    model = AlertNotification
    extra = 0
    readonly_fields = ("audience", "channel", "recipient_label", "status", "sent_at")
    can_delete = False


@admin.register(SOSAlert)
class SOSAlertAdmin(admin.ModelAdmin):
    list_display = ("id", "resident", "category", "status", "escalation_level",
                    "society", "responder", "created_at")
    list_filter = ("status", "category", "escalation_level", "society")
    search_fields = ("resident__username", "message")
    readonly_fields = ("created_at", "acknowledged_at", "escalated_at", "resolved_at", "closed_at")
    inlines = [NotificationInline]


@admin.register(AlertNotification)
class AlertNotificationAdmin(admin.ModelAdmin):
    list_display = ("alert", "recipient_label", "audience", "channel", "status", "sent_at")
    list_filter = ("audience", "channel", "status")
