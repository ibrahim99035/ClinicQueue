import csv
from django.http import HttpResponse
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
# Create your views here.
from .services import (
    get_admin_overview,
    get_appointments_by_status,
    get_appointments_by_month,
    get_top_specializations,
    get_doctor_performance,
)

class IsAdminOnly(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.isAdmin
        )
        

def check_admin_access(request):
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication is required."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        if not request.user.isAdmin:
            return Response(
                {"detail": "Admins only."},
                status=status.HTTP_403_FORBIDDEN
            )
            
        return None
    


class AdminOverviewView(APIView):
    def get(self, request):
        permission_error = check_admin_access(request)

        if permission_error:
            return permission_error

        data = get_admin_overview()
        return Response(data)


class AppointmentsByStatusView(APIView):
    def get(self, request):
        permission_error = check_admin_access(request)

        if permission_error:
            return permission_error

        data = get_appointments_by_status()
        return Response(data)


class AppointmentsByMonthView(APIView):
    def get(self, request):
        permission_error = check_admin_access(request)

        if permission_error:
            return permission_error

        data = get_appointments_by_month()
        return Response(data)


class TopSpecializationsView(APIView):
    def get(self, request):
        permission_error = check_admin_access(request)

        if permission_error:
            return permission_error

        data = get_top_specializations()
        return Response(data)


class DoctorPerformanceView(APIView):
    def get(self, request):
        permission_error = check_admin_access(request)

        if permission_error:
            return permission_error

        data = get_doctor_performance()
        return Response(data)


class ExportAnalyticsCSVView(APIView):
    def get(self, request):
        permission_error = check_admin_access(request)

        if permission_error:
            return permission_error

        data = get_admin_overview()
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="analytics-report.csv"'
        
        writer = csv.writer(response)
        
        # Users section
        writer.writerow(['USERS SUMMARY'])
        writer.writerow(['Metric', 'Count'])
        writer.writerow(['Total Users', data['users']['total']])
        writer.writerow(['Active Users', data['users']['active']])
        writer.writerow(['Inactive Users', data['users']['inactive']])
        writer.writerow(['Admins', data['users']['admins']])
        writer.writerow(['Receptionists', data['users']['receptionists']])
        writer.writerow(['Doctors', data['users']['doctors']])
        writer.writerow(['Patients', data['users']['patients']])
        writer.writerow([])
        
        # Doctors section
        writer.writerow(['DOCTORS SUMMARY'])
        writer.writerow(['Metric', 'Count'])
        writer.writerow(['Total Doctors', data['doctors']['total']])
        writer.writerow(['Approved Doctors', data['doctors']['approved']])
        writer.writerow(['Pending Doctors', data['doctors']['pending']])
        writer.writerow([])
        
        # Appointments section
        writer.writerow(['APPOINTMENT STATISTICS'])
        writer.writerow(['Status', 'Count', 'Percentage'])
        total_apt = data['appointments']['total']
        writer.writerow(['Total', total_apt, '100%'])
        writer.writerow(['Requested', data['appointments']['requested'], f"{(data['appointments']['requested']/total_apt*100 if total_apt > 0 else 0):.2f}%"])
        writer.writerow(['Confirmed', data['appointments']['confirmed'], f"{(data['appointments']['confirmed']/total_apt*100 if total_apt > 0 else 0):.2f}%"])
        writer.writerow(['Checked In', data['appointments']['checked_in'], f"{(data['appointments']['checked_in']/total_apt*100 if total_apt > 0 else 0):.2f}%"])
        writer.writerow(['Completed', data['appointments']['completed'], f"{(data['appointments']['completed']/total_apt*100 if total_apt > 0 else 0):.2f}%"])
        writer.writerow(['Cancelled', data['appointments']['cancelled'], f"{(data['appointments']['cancelled']/total_apt*100 if total_apt > 0 else 0):.2f}%"])
        writer.writerow(['No Show', data['appointments']['no_show'], f"{(data['appointments']['no_show']/total_apt*100 if total_apt > 0 else 0):.2f}%"])
        writer.writerow([])
        
        # Rates section
        writer.writerow(['PERFORMANCE RATES'])
        writer.writerow(['Metric', 'Rate'])
        writer.writerow(['Completion Rate', f"{data['rates']['completion_rate']:.2f}%"])
        writer.writerow(['Cancellation Rate', f"{data['rates']['cancellation_rate']:.2f}%"])
        writer.writerow(['No-Show Rate', f"{data['rates']['no_show_rate']:.2f}%"])
        
        return response
