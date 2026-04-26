from rest_framework.permissions import BasePermission


class IsPatient(BasePermission):
    """"req user is ->  Patients group """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.isPatient)
    
class IsDoctor(BasePermission):
    """req user is ->  Doctors group """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.isDoctor)
    
class IsReceptionist(BasePermission):
    """req user is -> Receptionists group """
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
    '''request user is the patient on this appointment.'''
    def has_object_permission(self, request, view, obj):
        return obj.patient == request.user
 
 
class IsAppointmentDoctor(BasePermission):
    '''request user is the doctor on this appointment.'''
    def has_object_permission(self, request, view, obj):
        return obj.doctor == request.user
    
