from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from accounts.models.user import User
from accounts.models.patient import PatientProfile
from accounts.models.doctor import DoctorProfile
from accounts.models.notification import Notification
# Register your models here.

admin.site.register(User)
class UserAdmin(BaseUserAdmin):
    ordering= ("id",)
    list_display = ("id", "email", "username", "full_name", "phone", "role_summary", "is_staff", "is_active")
    search_fields = ("email", "username", "first_name", "last_name", "phone")
    list_filter = ("is_staff", "is_superuser", "is_active", "groups")
    readonly_fields = ("last_login", "date_joined")
    fieldsets = (
        ("Authentication", {
            "fields": ("email", "username", "password")
        }),
        ("personal info", {
            "fields": ("first_name", "last_name", "phone", "email")
        }),
        ("permissions",{
            "fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")
        }),
        ("Important dates", {
            "fields": ("last_login", "date_joined")
        }),
    )
    
    def full_name(self, obj):
        name = f"{obj.first_name} {obj.last_name}"
        return name.strip()
    full_name.short_description = "Full name"
    
    def role_summary(self, obj):
        roles = []
        if obj.isPatient:
            roles.append("Patient")
        if obj.isDoctor:
            roles.append("Doctor")
        if obj.isReceptionist:
            roles.append("Receptionist")
        if obj.isAdmin:
            roles.append("Admin")
        if not roles:
            return "-"      
        return ", ".join(roles)   
        role_summary.short_description = "Roles"
        
        
admin.site.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    ordering = ("id",)
    list_display = ("id", "user", "user_email", "dateOfBirth", "gender",)
    search_fields = ("user__email","user__first_name","user__last_name",)
    list_filter = ("gender",)
    autocomplete_fields = ("user",)   
    list_select_related = ("user",)    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = "Email"


admin.site.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    ordering = ("id",)
    list_display = ("id", "user", "user_email", "specialization", "consultationDuration", "is_approved", "approved_by", "approved_at",)
    search_fields = ("user_email", "user__first_name", "user__last_name", "specialization")
    list_filter = ("is_approved", "specialization")
    autocomplete_fields = ("user", "approved_by")
    list_select_related = ("user", "approved_by")
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = "Email"
    
    
admin.site.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    ordering = ("-created_at", "-id")
    list_display = ("id", "user", "status", "is_read", "created_at", "short_message",)
    search_fields = ("user__email", "message", "status")
    autocomplete_fields = ("user",)
    list_select_related = ("user",)
    readonly_fields = ("created_at",)
    def short_message(self, obj):
        if len(obj.message) > 50:
            return obj.message[:50] + "..."
        return obj.message
    short_message.short_description = "Message"
    
    
admin.site.site_header = "ClinicPanal Adminstartion"
