from django.contrib import admin

# Register your models here.
from .models import Ambulance, EmergencyRequest, ChatMessage, NotificationLog

@admin.register(Ambulance)
class AmbulanceAdmin(admin.ModelAdmin):
    list_display = ("ambulanceid", "vehicle_number", "equipment_level", "current_status")
    list_filter = ("equipment_level", "current_status")
    search_fields = ("vehicle_number",)

@admin.register(EmergencyRequest)
class EmergencyRequestAdmin(admin.ModelAdmin):
    list_display = ("hospital_name", "hospital_address", "user", "status", "created_at")
    list_filter = ("status", "request_type", "created_at")
    search_fields = ("hospital_name", "customer_mobile", "pickup_address")

    actions = ["mark_as_approved", "mark_as_dispatched", "mark_as_rejected"]

    def mark_as_approved(self, request, queryset):
        queryset.update(status="Approved")
    mark_as_approved.short_description = "Mark selected requests as Approved"

    def mark_as_dispatched(self, request, queryset):
        queryset.update(status="Dispatched")
    mark_as_dispatched.short_description = "Mark selected requests as Dispatched"

    def mark_as_rejected(self, request, queryset):
        queryset.update(status="Rejected")
    mark_as_rejected.short_description = "Mark selected requests as Rejected"

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ("id", "request", "sender", "message", "timestamp")
    search_fields = ("message", "sender__firstname")

@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ("id", "request", "type", "message", "sent_at")
    list_filter = ("type",)