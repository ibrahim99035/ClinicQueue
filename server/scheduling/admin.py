from django.contrib import admin
from scheduling.models import WeeklySchedule, ScheduleException, TimeSlot
# Register your models here.

admin.site.register(WeeklySchedule)
admin.site.register(ScheduleException)
admin.site.register(TimeSlot)

class WeeklyScheduleAdmin(admin.ModelAdmin):
    ordering = ("doctor_id", "day_of_week", "start_time")
    list_display = ("id", "doctor_id", "day_of_week", "start_time", "end_time", "is_active",)
    search_fields = ("doctor_id__user__email", "doctor_id__user__first_name", "doctor_id__user__last_name",)
    list_filter = ("day_of_week", "is_active")
    autocomplete_fields = ("doctor_id",)
    list_select_related = ("doctor_id__user",)
    
    
class ScheduleExceptionAdmin(admin.ModelAdmin):
    ordering = ("-exception_date", "-id")
    list_display = ("id", "doctor_id", "exception_date", "type", "note",)
    search_fields = ("doctor_id__user__email", "doctor_id__user__first_name", "doctor_id__user__last_name", "type", "note",)
    list_filter = ("type", "exception_date")
    autocomplete_fields = ("doctor_id",)
    list_select_related = ("doctor_id__user",)
    

class TimeSlotAdmin(admin.ModelAdmin):
    ordering = ("doctor_id", "start_datetime")
    list_display = ("id", "doctor_id", "start_datetime", "end_datetime", "is_available",)
    search_fields = ("doctor_id__user__email", "doctor_id__user__first_name", "doctor_id__user__last_name",)
    list_filter = ("is_available", "start_datetime",)
    autocomplete_fields = ("doctor_id",)
    list_select_related = ("doctor_id__user",)
    
    
