from django.contrib import admin

from .models import IncidentMessage, ResponderAssignment


@admin.register(IncidentMessage)
class IncidentMessageAdmin(admin.ModelAdmin):
    list_display = ("alert", "sender", "body", "is_system", "created_at")
    list_filter = ("is_system",)


@admin.register(ResponderAssignment)
class ResponderAssignmentAdmin(admin.ModelAdmin):
    list_display = ("alert", "responder", "status", "updated_at")
    list_filter = ("status",)
