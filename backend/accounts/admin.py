from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import EmergencyContact, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "role", "phone", "is_available", "is_active")
    list_filter = ("role", "is_active", "is_available")
    fieldsets = UserAdmin.fieldsets + (
        ("Emergency Platform", {
            "fields": ("role", "phone", "is_phone_verified", "is_available", "expo_push_token")
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Emergency Platform", {"fields": ("role", "phone")}),
    )


@admin.register(EmergencyContact)
class EmergencyContactAdmin(admin.ModelAdmin):
    list_display = ("full_name", "resident", "escalation_level", "order", "phone", "is_verified")
    list_filter = ("escalation_level", "is_verified")
    search_fields = ("full_name", "phone", "resident__username")
