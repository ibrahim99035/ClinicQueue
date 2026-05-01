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
