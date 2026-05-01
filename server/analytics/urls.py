from django.urls import path

from .views import (
    AdminOverviewView,
    AppointmentsByStatusView,
    AppointmentsByMonthView,
    TopSpecializationsView,
    DoctorPerformanceView,
)


urlpatterns = [
    path("admin-overview/", AdminOverviewView.as_view(), name="analytics-admin-overview"),
    path("appointments-by-status/", AppointmentsByStatusView.as_view(), name="analytics-appointments-by-status"),
    path("appointments-by-month/", AppointmentsByMonthView.as_view(), name="analytics-appointments-by-month"),
    path("top-specializations/", TopSpecializationsView.as_view(), name="analytics-top-specializations"),
    path("doctor-performance/", DoctorPerformanceView.as_view(), name="analytics-doctor-performance"),
]