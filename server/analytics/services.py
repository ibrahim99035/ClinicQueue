from django.db.models import Count
from operator import itemgetter

from accounts.models import User, DoctorProfile, PatientProfile, Notification
from appointments.models import Appointment, WaitingList

APPOINTMENT_STATUSES = [
    "REQUESTED",
    "CONFIRMED",
    "CHECKED_IN",
    "COMPLETED",
    "CANCELLED",
    "NO_SHOW",
]

def calculate_percentage(part, total):
    if (total == 0):
        return 0
    percentage = part / total
    percentage = percentage * 100
    percentage = round(percentage, 2)
    
    return percentage

def get_user_group_count(group_name):
    return User.objects.filter(groups__name=group_name).distinct().count()


def get_appointment_status_counts():
    status_counts = {}
    for status in APPOINTMENT_STATUSES:
        count =  Appointment.objects.filter(status=status).count()
        status_counts[status] = count
    return status_counts
    

def get_admin_overview():
    status_counts = get_appointment_status_counts()
    total_appointments = 0
    for status in status_counts:
        total_appointments = total_appointments + status_counts[status]
        
    return {
        "users": {
            "total": User.objects.count(),
            "active": User.objects.filter(is_active=True).count(),
            "inactive": User.objects.filter(is_active=False).count(),
            "admins": get_user_group_count("Admins"),
            "receptionists": get_user_group_count("Receptionists"),
            "doctors": get_user_group_count("Doctors"),
            "patients": get_user_group_count("Patients"),
        },
        "doctors": {
            "total": DoctorProfile.objects.count(),
            "approved": DoctorProfile.objects.filter(is_approved=True).count(),
            "pending": DoctorProfile.objects.filter(is_approved=False).count(),
        },
        "patients": {
            "total": PatientProfile.objects.count(),
        },
        "appointments": {
            "total": total_appointments,
            "requested": status_counts["REQUESTED"],
            "confirmed": status_counts["CONFIRMED"],
            "checked_in": status_counts["CHECKED_IN"],
            "completed": status_counts["COMPLETED"],
            "cancelled": status_counts["CANCELLED"],
            "no_show": status_counts["NO_SHOW"],
        },
        "waiting_list": {
            "total": WaitingList.objects.count(),
        },
        "notifications": {
            "total": Notification.objects.count(),
            "unread": Notification.objects.filter(is_read=False).count(),
        },
        "rates": {
            "completion_rate": calculate_percentage(status_counts["COMPLETED"], total_appointments),
            "cancellation_rate": calculate_percentage(status_counts["CANCELLED"], total_appointments),
            "no_show_rate": calculate_percentage(status_counts["NO_SHOW"], total_appointments),
        },
    }
 

def get_appointment_by_status():
    status_counts = get_appointment_status_counts()
    results = []
    for status in status_counts:
        status_data = {
            "status": status,
            "count": status_counts[status],
        }
        results.append(status_data)
    
    return {
        "results": results
    }


def get_appointments_by_month():
    appointments = Appointment.objects.all()
    results = []
    monthly_counts = {}
    
    for appointment in appointments:
        month = appointment.created_at.strftime("%Y-%m")
        if month not in monthly_counts:
            monthly_counts[month] = 0
        monthly_counts[month] = monthly_counts[month] + 1
        
    for month in monthly_counts:
        month_data = {
            "month" : month,
            "count" : monthly_counts[month],
        }
        results.append(month_data)
    
    return {
        "date_field": "created_at",
        "results": results,
    }
        
        
def get_top_specializations():
    appointments = Appointment.objects.all()
    results = []
    specialization_counts = {}
    
    for appointment in appointments:
        specialization = appointment.doctor_id.specialization
        if not specialization:
            specialization = "Unspecified"
        if specialization not in specialization_counts:
            specialization_counts[specialization] = 0

        specialization_counts[specialization] = specialization_counts[specialization] + 1
        
    for specialization in specialization_counts:
        specialization_data = {
            "specialization": specialization,
            "appointment_count": specialization_counts[specialization],
        }
        
    results.append(specialization_data)

    return {
        "results": results
    }


def get_doctor_display_name(doctor_data):
    first_name = doctor_data["doctor_id__user__first_name"] or ""
    last_name = doctor_data["doctor_id__user__last_name"] or ""
    email = doctor_data["doctor_id__user__email"] or ""

    full_name = f"{first_name} {last_name}".strip()

    return full_name or email or "Unknown doctor"  


def get_doctor_display_name(doctor):
    first_name = doctor.user.first_name or ""
    last_name = doctor.user.last_name or ""
    email = doctor.user.email or ""

    full_name = first_name + " " + last_name
    full_name = full_name.strip()

    if full_name:
        return full_name

    if email:
        return email

    return "Unknown doctor"


def get_doctor_performance():
    appointments = Appointment.objects.all()

    doctors_data = {}

    for appointment in appointments:
        doctor = appointment.doctor_id
        doctor_id = doctor.id

        if doctor_id not in doctors_data:
            specialization = doctor.specialization

            if not specialization:
                specialization = "Unspecified"

            doctors_data[doctor_id] = {
                "doctor_id": doctor_id,
                "doctor_name": get_doctor_display_name(doctor),
                "specialization": specialization,
                "total_appointments": 0,
                "requested_count": 0,
                "confirmed_count": 0,
                "checked_in_count": 0,
                "completed_count": 0,
                "cancelled_count": 0,
                "no_show_count": 0,
            }

        doctors_data[doctor_id]["total_appointments"] = doctors_data[doctor_id]["total_appointments"] + 1

        if appointment.status == "REQUESTED":
            doctors_data[doctor_id]["requested_count"] = doctors_data[doctor_id]["requested_count"] + 1

        elif appointment.status == "CONFIRMED":
            doctors_data[doctor_id]["confirmed_count"] = doctors_data[doctor_id]["confirmed_count"] + 1

        elif appointment.status == "CHECKED_IN":
            doctors_data[doctor_id]["checked_in_count"] = doctors_data[doctor_id]["checked_in_count"] + 1

        elif appointment.status == "COMPLETED":
            doctors_data[doctor_id]["completed_count"] = doctors_data[doctor_id]["completed_count"] + 1

        elif appointment.status == "CANCELLED":
            doctors_data[doctor_id]["cancelled_count"] = doctors_data[doctor_id]["cancelled_count"] + 1

        elif appointment.status == "NO_SHOW":
            doctors_data[doctor_id]["no_show_count"] = doctors_data[doctor_id]["no_show_count"] + 1

    results = []

    for doctor_id in doctors_data:
        results.append(doctors_data[doctor_id])

    results.sort(
    key=itemgetter("total_appointments"),
    reverse=True
)

    return {
        "results": results
    }
    