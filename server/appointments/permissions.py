from rest_framework.permissions import BasePermission

class IsPatient(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.isPatient)
    
class IsDoctor(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.isDoctor)
    
class IsReceptionist(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.isReceptionist)

class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.isAdmin)
    
class IsDoctorOrReceptionist(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and (request.user.isDoctor or request.user.isReceptionist)
        )
        
class IsAppointmentPatient(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.patient == request.user
 
class IsAppointmentDoctor(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.doctor == request.user