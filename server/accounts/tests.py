from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models.doctor import DoctorProfile
from accounts.models.user import User


class AdminDashboardEndpointsTests(APITestCase):
    def setUp(self):
        self.admins_group = Group.objects.create(name="Admins")
        self.doctors_group = Group.objects.create(name="Doctors")
        self.patients_group = Group.objects.create(name="Patients")
        self.receptionists_group = Group.objects.create(name="Receptionists")

        self.admin_user = User.objects.create_user(
            email="admin@example.com",
            username="admin@example.com",
            password="testpass123",
            first_name="Admin",
            last_name="User",
        )
        self.admin_user.groups.add(self.admins_group)

        self.patient_user = User.objects.create_user(
            email="patient@example.com",
            username="patient@example.com",
            password="testpass123",
            first_name="Patient",
            last_name="User",
        )
        self.patient_user.groups.add(self.patients_group)

        self.doctor_user = User.objects.create_user(
            email="doctor@example.com",
            username="doctor@example.com",
            password="testpass123",
            first_name="Doctor",
            last_name="User",
            is_active=False,
        )
        self.doctor_user.groups.add(self.doctors_group)

        self.pending_doctor_profile = DoctorProfile.objects.create(
            user=self.doctor_user,
            specialization="Cardiology",
            consultationDuration=15,
            bio="Pending approval doctor",
            is_approved=False,
        )

        self.users_url = reverse("user-list")
        self.pending_doctors_url = reverse("pending-doctors")

    def test_admin_can_access_users_endpoint(self):
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.get(self.users_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertIsInstance(response.data["results"], list)

    def test_non_admin_gets_403_for_users_endpoint(self):
        self.client.force_authenticate(user=self.patient_user)

        response = self.client.get(self.users_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_access_pending_doctors_endpoint(self):
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.get(self.pending_doctors_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.pending_doctor_profile.id)

    def test_dashboard_required_fields_are_still_present(self):
        self.client.force_authenticate(user=self.admin_user)

        users_response = self.client.get(self.users_url)
        pending_doctors_response = self.client.get(self.pending_doctors_url)

        user_payload = users_response.data["results"]
        self.assertGreaterEqual(len(user_payload), 3)

        admin_user_data = next(item for item in user_payload if item["id"] == self.admin_user.id)
        self.assertIn("groups", admin_user_data)
        self.assertIn("is_active", admin_user_data)
        self.assertIn("patient_profile", admin_user_data)
        self.assertIn("doctor_profile", admin_user_data)
        self.assertIsInstance(admin_user_data["groups"], list)

        pending_doctor_data = pending_doctors_response.data[0]
        self.assertIn("id", pending_doctor_data)
        self.assertIn("user", pending_doctor_data)
        self.assertIn("specialization", pending_doctor_data)
        self.assertIn("consultationDuration", pending_doctor_data)
        self.assertIn("bio", pending_doctor_data)
        self.assertIn("is_approved", pending_doctor_data)
        self.assertIn("approved_by_name", pending_doctor_data)
        self.assertIn("approved_at", pending_doctor_data)
