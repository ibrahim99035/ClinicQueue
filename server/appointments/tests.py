from datetime import timedelta

from django.contrib.auth.models import Group
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models.doctor import DoctorProfile
from accounts.models.patient import PatientProfile
from accounts.models.user import User
from emr.models import ConsultationRecord
from scheduling.models import TimeSlot

from .models import Appointment, RescheduleHistory


class AppointmentLifecycleTests(APITestCase):
    def setUp(self):
        self.patients_group, _ = Group.objects.get_or_create(name="Patients")
        self.doctors_group, _ = Group.objects.get_or_create(name="Doctors")
        self.receptionists_group, _ = Group.objects.get_or_create(name="Receptionists")

        self.patient_user = User.create_user(
            email="patient@example.com",
            password="testpass123",
            first_name="Patient",
            last_name="User",
        )
        self.patient_user.groups.add(self.patients_group)
        self.patient_profile = PatientProfile.createPatient(self.patient_user)

        self.doctor_user = User.create_user(
            email="doctor@example.com",
            password="testpass123",
            first_name="Doctor",
            last_name="User",
        )
        self.doctor_user.groups.add(self.doctors_group)
        self.doctor_profile = DoctorProfile.createDoctor(self.doctor_user, specialization="Cardiology")

        self.receptionist_user = User.create_user(
            email="receptionist@example.com",
            password="testpass123",
            first_name="Receptionist",
            last_name="User",
        )
        self.receptionist_user.groups.add(self.receptionists_group)

        self.appointment_list_url = reverse("appointment-list")

    def create_slot(self, days_offset=1, start_hour=9):
        start_datetime = timezone.now().replace(
            hour=start_hour, minute=0, second=0, microsecond=0
        ) + timedelta(days=days_offset)
        end_datetime = start_datetime + timedelta(minutes=15)
        return TimeSlot.objects.create(
            doctor=self.doctor_profile,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            is_available=True,
        )

    def create_appointment(self, slot=None, status_value="REQUESTED"):
        if slot is None:
            slot = self.create_slot()
        return Appointment.objects.create(
            patient_id=self.patient_profile,
            doctor_id=self.doctor_profile,
            slot_id=slot,
            status=status_value,
            reason="Follow-up",
        )

    def test_patient_can_create_appointment_successfully(self):
        slot = self.create_slot()
        self.client.force_authenticate(user=self.patient_user)

        response = self.client.post(
            self.appointment_list_url,
            {
                "slot_id": slot.id,
                "doctor_id": self.doctor_profile.id,
                "reason": "Headache",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        appointment = Appointment.objects.get(pk=response.data["id"])
        self.assertEqual(appointment.status, "REQUESTED")
        self.assertEqual(appointment.patient_id, self.patient_profile)

    def test_booking_an_already_booked_slot_returns_400(self):
        slot = self.create_slot()
        self.create_appointment(slot=slot)
        self.client.force_authenticate(user=self.patient_user)

        response = self.client.post(
            self.appointment_list_url,
            {
                "slot_id": slot.id,
                "doctor_id": self.doctor_profile.id,
                "reason": "Second booking attempt",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("slot_id", response.data)

    def test_confirming_sets_status_confirmed_and_fills_confirmed_at(self):
        appointment = self.create_appointment(status_value="REQUESTED")
        self.client.force_authenticate(user=self.doctor_user)

        response = self.client.post(
            reverse("appointment-confirm", kwargs={"pk": appointment.pk}),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        appointment.refresh_from_db()
        self.assertEqual(appointment.status, "CONFIRMED")
        self.assertIsNotNone(appointment.confirmed_at)

    def test_checking_in_sets_status_checked_in_and_fills_checked_in_at(self):
        appointment = self.create_appointment(status_value="CONFIRMED")
        self.client.force_authenticate(user=self.receptionist_user)

        response = self.client.post(
            reverse("appointment-check-in", kwargs={"pk": appointment.pk}),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        appointment.refresh_from_db()
        self.assertEqual(appointment.status, "CHECKED_IN")
        self.assertIsNotNone(appointment.checked_in_at)

    def test_completing_without_consultation_returns_400(self):
        appointment = self.create_appointment(status_value="CHECKED_IN")
        self.client.force_authenticate(user=self.doctor_user)

        response = self.client.post(
            reverse("appointment-complete", kwargs={"pk": appointment.pk}),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        appointment.refresh_from_db()
        self.assertEqual(appointment.status, "CHECKED_IN")
        self.assertIsNone(appointment.completed_at)

    def test_completing_with_consultation_succeeds_and_fills_completed_at(self):
        appointment = self.create_appointment(status_value="CHECKED_IN")
        ConsultationRecord.objects.create(
            appointment_id=appointment,
            created_by=self.doctor_user,
            diagnosis="Migraine",
            notes="Stable patient",
        )
        self.client.force_authenticate(user=self.doctor_user)

        response = self.client.post(
            reverse("appointment-complete", kwargs={"pk": appointment.pk}),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        appointment.refresh_from_db()
        self.assertEqual(appointment.status, "COMPLETED")
        self.assertIsNotNone(appointment.completed_at)

    def test_rescheduling_updates_slot_and_creates_history(self):
        original_slot = self.create_slot(days_offset=1, start_hour=9)
        new_slot = self.create_slot(days_offset=2, start_hour=11)
        appointment = self.create_appointment(slot=original_slot, status_value="CONFIRMED")
        self.client.force_authenticate(user=self.patient_user)

        response = self.client.post(
            reverse("appointment-reschedule", kwargs={"pk": appointment.pk}),
            {
                "new_slot": new_slot.id,
                "reason": "Need another time",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        appointment.refresh_from_db()
        self.assertEqual(appointment.slot_id, new_slot)
        self.assertTrue(
            RescheduleHistory.objects.filter(
                appointment_id=appointment,
                old_slot_id=original_slot,
                new_slot_id=new_slot,
            ).exists()
        )
