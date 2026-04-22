from django.contrib import admin
from emr.models import ConsultationRecord, PrescriptionItem, RequestedTest
# Register your models here.
admin.site.register(ConsultationRecord)
admin.site.register(PrescriptionItem)
admin.site.register(RequestedTest)

class PrescriptionItemInline(admin.TabularInline):
    model = PrescriptionItem
    extra = 1


class RequestedTestInline(admin.TabularInline):
    model = RequestedTest
    extra = 1
    
class ConsultationRecordAdmin(admin.ModelAdmin):
    ordering = ("-created_at",)
    list_display = ("id", "appointment_id", "created_by", "diagnosis", "created_at", "updated_at",)
    search_fields = ( "appointment_id__patient_id__user__email", "appointment_id__doctor_id__user__email", "diagnosis", "notes", "created_by__email", )
    list_filter = ("created_at", "updated_at",)
    readonly_fields = ("created_at", "updated_at")
    inlines = [PrescriptionItemInline, RequestedTestInline]
    autocomplete_fields = ("appointment_id", "created_by")
    

class PrescriptionItemAdmin(admin.ModelAdmin):
    ordering = ("id",)
    list_display = ("id", "consultation_id", "drug_name", "dose", "duration",)
    search_fields = ("consultation_id__appointment_id__patient_id__user__email", "drug_name", "dose", "duration",)
    autocomplete_fields = ("consultation_id",)


class RequestedTestAdmin(admin.ModelAdmin):
    ordering = ("id",)
    list_display = ("id", "consultation_id", "test_name", "notes",)
    search_fields = (
        "consultation_id__appointment_id__patient_id__user__email",
        "consultation_id__appointment_id__doctor_id__user__email",
        "test_name",
        "notes",
    )
    autocomplete_fields = ("consultation_id",)
    