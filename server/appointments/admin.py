from django.contrib import admin
from appointments.models import Appointment, RescheduleHistory, WaitingList, Payment
# Register your models here.

admin.site.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    ordering = ("-created_at", "-id")
    list_display = ("id", "patient_id", "doctor_id", "slot_id", "status", "type", "created_at", "confirmed_at", "checked_in_at", "completed_at")
    search_fields = ("patient_id__user__email",
                     "patient_id__user__first_name",
                     "patient_id__user__last_name",
                     "doctor_id__user__email",
                     "doctor_id__user__first_name",
                     "doctor_id__user__last_name",
                     "reason",
                     "type")
    list_filter = ("status", "type", "created_at")
    readonly_fields = ("created_at", "confirmed_at", "checked_in_at", "completed_at")
    autocomplete_fields = ("patient_id", "doctor_id", "slot_id")
    list_select_related = ("patient_id__user","doctor_id__user","slot_id",)
    
    
admin.site.register(RescheduleHistory)
class RescheduleHistoryAdmin(admin.ModelAdmin):
    ordering = ("-timestamp")
    list_display = ("id", "appointment_id", "old_slot_id", "new_slot_id", "changed_by", "timestamp")
    search_fields = (
        "appointment_id__patient_id__user__email",
        "appointment_id__doctor_id__user__email",
        "changed_by__email",
        "reason",
    )
    list_filter = ("timestamp",)
    readonly_fields = ("timestamp",)
    autocomplete_fields = ("appointment_id", "old_slot_id", "new_slot_id", "changed_by",)
    
    
admin.site.register(WaitingList)
class WaitingListAdmin(admin.ModelAdmin):
    ordering = ("-created_at")
    list_display = ("id", "patient_id", "doctor_id", "preferred_date", "hold_expires_at", "created_at")
    search_fields = ("patient_id__user__email", "doctor_id__user__email",)
    list_filter = ("preferred_date", "created_at",)
    readonly_fields = ("created_at",)
    autocomplete_fields = ("patient_id", "doctor_id")
    
    
admin.site.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    ordering = ("-paid_at",)
    list_display = ("id", "appointment_id", "amount", "status", "paid_at", "refunded_at",)
    search_fields = ("appointment_id__patient_id__user__email", "appointment_id__doctor_id__user__email",)
    list_filter = ("status", "paid_at", "refunded_at",)
    readonly_fields = ("paid_at",)
    autocomplete_fields = ("appointment_id",)