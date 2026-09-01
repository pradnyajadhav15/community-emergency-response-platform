from django.contrib import admin

from .models import Block, Flat, ResidentProfile, Society


class BlockInline(admin.TabularInline):
    model = Block
    extra = 1


class FlatInline(admin.TabularInline):
    model = Flat
    extra = 3


@admin.register(Society)
class SocietyAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "city", "created_at")
    search_fields = ("name", "code", "city")
    inlines = [BlockInline]


@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    list_display = ("name", "society", "total_floors")
    list_filter = ("society",)
    inlines = [FlatInline]


@admin.register(Flat)
class FlatAdmin(admin.ModelAdmin):
    list_display = ("flat_number", "block", "floor")
    list_filter = ("block__society", "block")
    search_fields = ("flat_number",)


@admin.register(ResidentProfile)
class ResidentProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "flat", "is_owner", "is_senior_citizen")
    list_filter = ("is_owner", "is_senior_citizen")
    search_fields = ("user__username",)
