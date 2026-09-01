from rest_framework import serializers

from .models import AlertNotification, SOSAlert


class AlertNotificationSerializer(serializers.ModelSerializer):
    audience_display = serializers.CharField(source="get_audience_display", read_only=True)

    class Meta:
        model = AlertNotification
        fields = [
            "id", "alert", "recipient_label", "audience", "audience_display",
            "channel", "title", "body", "status", "error",
            "created_at", "sent_at", "read_at",
        ]
        read_only_fields = fields


class SOSAlertSerializer(serializers.ModelSerializer):
    resident_name = serializers.CharField(source="resident.username", read_only=True)
    resident_phone = serializers.CharField(source="resident.phone", read_only=True)
    category_display = serializers.CharField(source="get_category_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    flat_label = serializers.SerializerMethodField()
    responder_name = serializers.CharField(source="responder.username", read_only=True)
    notification_count = serializers.IntegerField(source="notifications.count", read_only=True)

    class Meta:
        model = SOSAlert
        fields = [
            "id", "resident", "resident_name", "resident_phone",
            "society", "flat", "flat_label",
            "category", "category_display", "message",
            "latitude", "longitude", "address",
            "status", "status_display", "escalation_level",
            "responder", "responder_name", "notification_count",
            "created_at", "acknowledged_at", "escalated_at",
            "resolved_at", "closed_at", "resolution_notes",
        ]
        read_only_fields = [
            "id", "resident", "society", "flat", "status", "escalation_level",
            "responder", "created_at", "acknowledged_at", "escalated_at",
            "resolved_at", "closed_at",
        ]


class SOSCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SOSAlert
        fields = ["category", "message", "latitude", "longitude", "address"]

def _flat_label(self, obj):
    return str(obj.flat) if obj.flat else ""

SOSAlertSerializer.get_flat_label = _flat_label
