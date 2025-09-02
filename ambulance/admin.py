from django.contrib import admin

# Register your models here.
from .models import Ambulance

@admin.register(Ambulance)
class AmbulanceAdmin(admin.ModelAdmin):
    list_display = ("ambulanceid", "vehicle_number", "equipment_level", "current_status")
    list_filter = ("equipment_level", "current_status")
    search_fields = ("vehicle_number",)