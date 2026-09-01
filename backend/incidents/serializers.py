from rest_framework import serializers

from .models import IncidentMessage, ResponderAssignment


class IncidentMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source="sender.username", read_only=True)
    sender_role = serializers.CharField(source="sender.role", read_only=True)

    class Meta:
        model = IncidentMessage
        fields = ["id", "alert", "sender", "sender_name", "sender_role",
                  "body", "is_system", "created_at"]
        read_only_fields = ["id", "sender", "is_system", "created_at"]


class ResponderAssignmentSerializer(serializers.ModelSerializer):
    responder_name = serializers.CharField(source="responder.username", read_only=True)
    responder_role = serializers.CharField(source="responder.role", read_only=True)
    responder_phone = serializers.CharField(source="responder.phone", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = ResponderAssignment
        fields = ["id", "alert", "responder", "responder_name", "responder_role",
                  "responder_phone", "status", "status_display", "notes",
                  "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]
