from django.contrib import admin
from emr.models import ConsultationRecord, PrescriptionItem, RequestedTest

admin.site.register(ConsultationRecord)
admin.site.register(PrescriptionItem)
admin.site.register(RequestedTest)