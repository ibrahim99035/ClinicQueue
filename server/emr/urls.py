from django.urls import path
from .views import (
    CanCreateViewOfConsultationRecord,
    DoctorPatientViewConsultationRecord,
    ConsultationRecordUpdateView,
)
urlpatterns = [
    path("consultations/", CanCreateViewOfConsultationRecord.as_view(), name="consultation-create"),
    path("consultations/by-appointment/<int:appointment_id>/", DoctorPatientViewConsultationRecord.as_view(), name="consultation-detail-by-appointment"),
    path("consultations/<int:pk>/", ConsultationRecordUpdateView.as_view(), name="consultation-update"),
]
