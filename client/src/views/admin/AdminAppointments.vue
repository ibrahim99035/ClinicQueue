<script setup>
import { computed, onMounted, ref } from "vue";
import { getAdminUsers } from "../../api/admin";
import {
  getAppointments,
  getAppointmentDetails,
  getAppointmentHistory,
} from "../../api/appointments";

const users = ref([]);
const appointments = ref([]);
const loading = ref(false);
const loadingDetails = ref(false);
const errorMessage = ref("");
const selectedAppointment = ref(null);
const selectedHistory = ref([]);

const filters = ref({
  search: "",
  status: "",
  doctor: "",
  patient: "",
  date_from: "",
  date_to: "",
});

const statusOptions = [
  "REQUESTED",
  "CONFIRMED",
  "CHECKED_IN",
  "COMPLETED",
  "CANCELLED",
  "NO_SHOW",
];

function formatApiError(error) {
  if (!error.response) {
    return "Something went wrong. Please try again.";
  }
  const data = error.response.data;
  if (data.detail) {
    return data.detail;
  }
  if (data.message) {
    return data.message;
  }
  return "Please check the request data.";
}

function getUserGroups(user) {
  return user.groups || [];
}

function formatUserName(user) {
  const firstName = user.first_name || "";
  const lastName = user.last_name || "";

  const fullName = (firstName + " " + lastName).trim();

  if (fullName) {
    return fullName;
  }

  if (user.email) {
    return user.email;
  }

  return "Unknown user";
}

function getDoctorProfile(user) {
  return user.doctor_profile || null;
}

function getPatientProfile(user) {
  return user.patient_profile || null;
}

const doctors = computed(() => {
  const doctorsList = [];

  users.value.forEach((user) => {
    const groups = getUserGroups(user);

    if (!groups.includes("Doctors")) {
      return;
    }

    const profile = getDoctorProfile(user);

    if (!profile) {
      return;
    }

    doctorsList.push({
      id: profile.id,
      name: formatUserName(user),
    });
  });

  return doctorsList;
});

const patients = computed(() => {
  const patientsList = [];
  users.value.forEach((user) => {
    const groups = getUserGroups(user);
    if (!groups.includes("Patients")) {
      return;
    }
    const profile = getPatientProfile(user);
    if (!profile) {
      return;
    }
    patientsList.push({
      id: profile.id,
      name: formatUserName(user),
    });
  });
  return patientsList;
});

const totalAppointments = computed(() => appointments.value.length);

const requestedCount = computed(() =>
  appointments.value.filter((item) => item.status === "REQUESTED").length
);

const confirmedCount = computed(() =>
  appointments.value.filter((item) => item.status === "CONFIRMED").length
);

const checkedInCount = computed(() =>
  appointments.value.filter((item) => item.status === "CHECKED_IN").length
);

const completedCount = computed(() =>
  appointments.value.filter((item) => item.status === "COMPLETED").length
);

function buildParams() {
  const params = {};

  const search = filters.value.search;
  const status = filters.value.status;
  const doctor = filters.value.doctor;
  const patient = filters.value.patient;
  const dateFrom = filters.value.date_from;
  const dateTo = filters.value.date_to;

  if (search) {
    params.search = search;
  }

  if (status) {
    params.status = status;
  }

  if (doctor) {
    params.doctor = doctor;
  }

  if (patient) {
    params.patient = patient;
  }

  if (dateFrom) {
    params.date_from = dateFrom;
  }

  if (dateTo) {
    params.date_to = dateTo;
  }

  return params;
}

async function loadAppointments() {
  loading.value = true;
  errorMessage.value = "";

  try {
    appointments.value = await getAppointments(buildParams());
  } catch (error) {
    errorMessage.value = formatApiError(error);
  } finally {
    loading.value = false;
  }
}

async function loadInitialData() {
  loading.value = true;
  errorMessage.value = "";

  try {
    users.value = await getAdminUsers();
    appointments.value = await getAppointments();
  } catch (error) {
    errorMessage.value = formatApiError(error);
  } finally {
    loading.value = false;
  }
}

function resetFilters() {
  filters.value = {
    search: "",
    status: "",
    doctor: "",
    patient: "",
    date_from: "",
    date_to: "",
  };

  loadAppointments();
}

async function openAppointmentDetails(appointment) {
  loadingDetails.value = true;
  errorMessage.value = "";
  selectedAppointment.value = null;
  selectedHistory.value = [];

  try {
    selectedAppointment.value = await getAppointmentDetails(appointment.id);
    selectedHistory.value = await getAppointmentHistory(appointment.id);
  } catch (error) {
    errorMessage.value = formatApiError(error);
  } finally {
    loadingDetails.value = false;
  }
}

function closeDetails() {
  selectedAppointment.value = null;
  selectedHistory.value = [];
}

function formatDateTime(value) {
  if (!value) return "-";
  return new Date(value).toLocaleString();
}

function formatStatus(status) {
  if (!status) return "-";
  return status.replace("_", " ");
}

function getStatusClass(status) {
  return {
    requested: status === "REQUESTED",
    confirmed: status === "CONFIRMED",
    checked: status === "CHECKED_IN",
    completed: status === "COMPLETED",
    cancelled: status === "CANCELLED",
    noShow: status === "NO_SHOW",
  };
}

function getPatientName(appointment) {
  return appointment.patient_name || "-";
}

function getDoctorName(appointment) {
  return appointment.doctor_name || "-";
}

function getAppointmentStart(appointment) {
  if (appointment.slot_start) {
    return appointment.slot_start;
  }

  if (appointment.slot_time) {
    return appointment.slot_time;
  }

  if (appointment.appointment_datetime) {
    return appointment.appointment_datetime;
  }

  return "-";
}

function getStatusBadgeClass(status) {
  if (status === "REQUESTED") {
    return "bg-amber-100 text-amber-800";
  }

  if (status === "CONFIRMED") {
    return "bg-blue-100 text-blue-700";
  }

  if (status === "CHECKED_IN") {
    return "bg-purple-100 text-purple-700";
  }

  if (status === "COMPLETED") {
    return "bg-green-100 text-green-700";
  }

  if (status === "CANCELLED") {
    return "bg-red-100 text-red-700";
  }

  if (status === "NO_SHOW") {
    return "bg-slate-100 text-slate-700";
  }

  return "bg-slate-100 text-slate-700";
}

onMounted(() => {
  loadInitialData();
});

</script>
<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 p-6">
    <div class="mx-auto flex max-w-7xl flex-col gap-6">

      <!-- Header -->
      <div class="rounded-3xl bg-gradient-to-r from-blue-600 to-indigo-700 p-6 text-white shadow-lg">
        <div class="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <p class="mb-2 text-sm font-semibold uppercase tracking-wide text-blue-100">
              Appointments
            </p>

            <h2 class="text-3xl font-bold">
              Appointments Management
            </h2>

            <p class="mt-2 max-w-2xl text-sm leading-6 text-blue-100">
              View, filter, and review all clinic appointments from one place.
            </p>
          </div>

          <button
            type="button"
            @click="loadAppointments"
            :disabled="loading"
            class="w-fit rounded-2xl bg-white px-5 py-3 text-sm font-bold text-blue-700 shadow-sm transition hover:bg-blue-50 disabled:cursor-not-allowed disabled:bg-white/60"
          >
            {{ loading ? "Loading..." : "Refresh" }}
          </button>
        </div>
      </div>

      <!-- Error Message -->
      <p
        v-if="errorMessage"
        class="rounded-2xl border border-red-200 bg-red-50 px-5 py-4 text-sm font-semibold text-red-700 shadow-sm"
      >
        {{ errorMessage }}
      </p>

      <!-- Summary Cards -->
      <div class="grid gap-5 md:grid-cols-2 xl:grid-cols-5">
        <div class="rounded-3xl border border-white/70 bg-white/85 p-6 shadow-sm backdrop-blur transition hover:-translate-y-1 hover:shadow-md">
          <div class="mb-4 flex h-12 w-12 items-center justify-center rounded-2xl bg-blue-100 text-lg font-bold text-blue-700">
            T
          </div>

          <span class="text-sm font-semibold text-slate-500">
            Total
          </span>

          <strong class="mt-2 block text-3xl font-bold text-slate-900">
            {{ totalAppointments }}
          </strong>
        </div>

        <div class="rounded-3xl border border-white/70 bg-white/85 p-6 shadow-sm backdrop-blur transition hover:-translate-y-1 hover:shadow-md">
          <div class="mb-4 flex h-12 w-12 items-center justify-center rounded-2xl bg-amber-100 text-lg font-bold text-amber-700">
            R
          </div>

          <span class="text-sm font-semibold text-slate-500">
            Requested
          </span>

          <strong class="mt-2 block text-3xl font-bold text-slate-900">
            {{ requestedCount }}
          </strong>
        </div>

        <div class="rounded-3xl border border-white/70 bg-white/85 p-6 shadow-sm backdrop-blur transition hover:-translate-y-1 hover:shadow-md">
          <div class="mb-4 flex h-12 w-12 items-center justify-center rounded-2xl bg-blue-100 text-lg font-bold text-blue-700">
            C
          </div>

          <span class="text-sm font-semibold text-slate-500">
            Confirmed
          </span>

          <strong class="mt-2 block text-3xl font-bold text-slate-900">
            {{ confirmedCount }}
          </strong>
        </div>

        <div class="rounded-3xl border border-white/70 bg-white/85 p-6 shadow-sm backdrop-blur transition hover:-translate-y-1 hover:shadow-md">
          <div class="mb-4 flex h-12 w-12 items-center justify-center rounded-2xl bg-purple-100 text-lg font-bold text-purple-700">
            I
          </div>

          <span class="text-sm font-semibold text-slate-500">
            Checked In
          </span>

          <strong class="mt-2 block text-3xl font-bold text-slate-900">
            {{ checkedInCount }}
          </strong>
        </div>

        <div class="rounded-3xl border border-white/70 bg-white/85 p-6 shadow-sm backdrop-blur transition hover:-translate-y-1 hover:shadow-md">
          <div class="mb-4 flex h-12 w-12 items-center justify-center rounded-2xl bg-green-100 text-lg font-bold text-green-700">
            ✓
          </div>

          <span class="text-sm font-semibold text-slate-500">
            Completed
          </span>

          <strong class="mt-2 block text-3xl font-bold text-slate-900">
            {{ completedCount }}
          </strong>
        </div>
      </div>

      <!-- Filters -->
      <div class="rounded-3xl border border-white/70 bg-white/90 p-6 shadow-sm backdrop-blur">
        <div class="grid gap-4 md:grid-cols-2 xl:grid-cols-7">
          <div class="xl:col-span-2">
            <label class="mb-1.5 block text-sm font-semibold text-slate-700">
              Search
            </label>

            <input
              v-model="filters.search"
              type="text"
              placeholder="Appointment ID or patient name"
              class="w-full rounded-xl border border-slate-300 bg-white px-3 py-2.5 text-sm outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
            />
          </div>

          <div>
            <label class="mb-1.5 block text-sm font-semibold text-slate-700">
              Status
            </label>

            <select
              v-model="filters.status"
              class="w-full rounded-xl border border-slate-300 bg-white px-3 py-2.5 text-sm outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
            >
              <option value="">All Statuses</option>

              <option
                v-for="status in statusOptions"
                :key="status"
                :value="status"
              >
                {{ formatStatus(status) }}
              </option>
            </select>
          </div>

          <div>
            <label class="mb-1.5 block text-sm font-semibold text-slate-700">
              Doctor
            </label>

            <select
              v-model="filters.doctor"
              class="w-full rounded-xl border border-slate-300 bg-white px-3 py-2.5 text-sm outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
            >
              <option value="">All Doctors</option>

              <option
                v-for="doctor in doctors"
                :key="doctor.id"
                :value="doctor.id"
              >
                {{ doctor.name }}
              </option>
            </select>
          </div>

          <div>
            <label class="mb-1.5 block text-sm font-semibold text-slate-700">
              Patient
            </label>

            <select
              v-model="filters.patient"
              class="w-full rounded-xl border border-slate-300 bg-white px-3 py-2.5 text-sm outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
            >
              <option value="">All Patients</option>

              <option
                v-for="patient in patients"
                :key="patient.id"
                :value="patient.id"
              >
                {{ patient.name }}
              </option>
            </select>
          </div>

          <div>
            <label class="mb-1.5 block text-sm font-semibold text-slate-700">
              From
            </label>

            <input
              v-model="filters.date_from"
              type="date"
              class="w-full rounded-xl border border-slate-300 bg-white px-3 py-2.5 text-sm outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
            />
          </div>

          <div>
            <label class="mb-1.5 block text-sm font-semibold text-slate-700">
              To
            </label>

            <input
              v-model="filters.date_to"
              type="date"
              class="w-full rounded-xl border border-slate-300 bg-white px-3 py-2.5 text-sm outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
            />
          </div>
        </div>

        <div class="mt-5 flex flex-wrap gap-3">
          <button
            type="button"
            @click="loadAppointments"
            :disabled="loading"
            class="rounded-xl bg-blue-600 px-4 py-2.5 text-sm font-bold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-slate-400"
          >
            Apply
          </button>

          <button
            type="button"
            @click="resetFilters"
            :disabled="loading"
            class="rounded-xl bg-slate-100 px-4 py-2.5 text-sm font-bold text-slate-700 transition hover:bg-slate-200 disabled:cursor-not-allowed disabled:opacity-60"
          >
            Reset
          </button>
        </div>
      </div>

      <!-- Appointment Table -->
      <div class="overflow-hidden rounded-3xl border border-white/70 bg-white/90 shadow-sm backdrop-blur">
        <div class="flex flex-col gap-2 border-b border-slate-200 px-6 py-5 md:flex-row md:items-center md:justify-between">
          <div>
            <h3 class="text-xl font-bold text-slate-900">
              Appointment List
            </h3>

            <p class="mt-1 text-sm text-slate-500">
              Filtered clinic appointment records.
            </p>
          </div>

          <span class="w-fit rounded-full bg-blue-100 px-4 py-2 text-sm font-bold text-blue-700">
            {{ appointments.length }} result(s)
          </span>
        </div>

        <div
          v-if="loading"
          class="p-6 text-sm text-slate-500"
        >
          Loading appointments...
        </div>

        <div
          v-else-if="appointments.length === 0"
          class="p-6 text-sm text-slate-500"
        >
          No appointments found.
        </div>

        <div
          v-else
          class="overflow-x-auto"
        >
          <table class="w-full min-w-[1000px] border-collapse text-left">
            <thead>
              <tr class="bg-slate-50 text-sm text-slate-600">
                <th class="border-b border-slate-200 px-6 py-4 font-bold">
                  ID
                </th>

                <th class="border-b border-slate-200 px-6 py-4 font-bold">
                  Patient
                </th>

                <th class="border-b border-slate-200 px-6 py-4 font-bold">
                  Doctor
                </th>

                <th class="border-b border-slate-200 px-6 py-4 font-bold">
                  Date / Time
                </th>

                <th class="border-b border-slate-200 px-6 py-4 font-bold">
                  Status
                </th>

                <th class="border-b border-slate-200 px-6 py-4 font-bold">
                  Reason
                </th>

                <th class="w-32 border-b border-slate-200 px-6 py-4 font-bold">
                  Action
                </th>
              </tr>
            </thead>

            <tbody>
              <tr
                v-for="appointment in appointments"
                :key="appointment.id"
                class="text-sm text-slate-900 transition hover:bg-blue-50/60"
              >
                <td class="border-b border-slate-100 px-6 py-4 font-bold text-slate-700">
                  #{{ appointment.id }}
                </td>

                <td class="border-b border-slate-100 px-6 py-4">
                  {{ getPatientName(appointment) }}
                </td>

                <td class="border-b border-slate-100 px-6 py-4">
                  {{ getDoctorName(appointment) }}
                </td>

                <td class="border-b border-slate-100 px-6 py-4">
                  {{ formatDateTime(getAppointmentStart(appointment)) }}
                </td>

                <td class="border-b border-slate-100 px-6 py-4">
                  <span
                    class="inline-flex rounded-full px-3 py-1 text-xs font-bold"
                    :class="getStatusBadgeClass(appointment.status)"
                  >
                    {{ formatStatus(appointment.status) }}
                  </span>
                </td>

                <td class="border-b border-slate-100 px-6 py-4">
                  <span class="inline-block max-w-[220px] truncate text-slate-600">
                    {{ appointment.reason || "-" }}
                  </span>
                </td>

                <td class="border-b border-slate-100 px-6 py-4">
                  <button
                    type="button"
                    @click="openAppointmentDetails(appointment)"
                    class="rounded-xl bg-blue-600 px-3 py-2 text-xs font-bold text-white transition hover:bg-blue-700"
                  >
                    Details
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Loading Details -->
      <div
        v-if="loadingDetails"
        class="rounded-3xl border border-white/70 bg-white/90 p-6 text-sm font-semibold text-slate-500 shadow-sm backdrop-blur"
      >
        Loading appointment details...
      </div>

      <!-- Appointment Details -->
      <div
        v-if="selectedAppointment"
        class="rounded-3xl border border-white/70 bg-white/90 p-6 shadow-sm backdrop-blur"
      >
        <div class="mb-6 flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
          <div>
            <h3 class="text-2xl font-bold text-slate-900">
              Appointment #{{ selectedAppointment.id }}
            </h3>

            <p class="mt-1 text-sm text-slate-500">
              {{ getPatientName(selectedAppointment) }}
              with
              {{ getDoctorName(selectedAppointment) }}
            </p>
          </div>

          <button
            type="button"
            @click="closeDetails"
            class="w-fit rounded-xl bg-slate-100 px-4 py-2.5 text-sm font-bold text-slate-700 transition hover:bg-slate-200"
          >
            Close
          </button>
        </div>

        <div class="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          <div class="rounded-2xl border border-slate-200 bg-slate-50 p-4">
            <span class="block text-sm font-semibold text-slate-500">
              Status
            </span>

            <strong class="mt-1 block text-base text-slate-900">
              {{ formatStatus(selectedAppointment.status) }}
            </strong>
          </div>

          <div class="rounded-2xl border border-slate-200 bg-slate-50 p-4">
            <span class="block text-sm font-semibold text-slate-500">
              Type
            </span>

            <strong class="mt-1 block text-base text-slate-900">
              {{ selectedAppointment.type || "-" }}
            </strong>
          </div>

          <div class="rounded-2xl border border-slate-200 bg-slate-50 p-4">
            <span class="block text-sm font-semibold text-slate-500">
              Start
            </span>

            <strong class="mt-1 block text-base text-slate-900">
              {{ formatDateTime(getAppointmentStart(selectedAppointment)) }}
            </strong>
          </div>

          <div class="rounded-2xl border border-slate-200 bg-slate-50 p-4">
            <span class="block text-sm font-semibold text-slate-500">
              Created
            </span>

            <strong class="mt-1 block text-base text-slate-900">
              {{ formatDateTime(selectedAppointment.created_at) }}
            </strong>
          </div>

          <div class="rounded-2xl border border-slate-200 bg-slate-50 p-4">
            <span class="block text-sm font-semibold text-slate-500">
              Checked In
            </span>

            <strong class="mt-1 block text-base text-slate-900">
              {{ formatDateTime(selectedAppointment.checked_in_at) }}
            </strong>
          </div>

          <div class="rounded-2xl border border-slate-200 bg-slate-50 p-4">
            <span class="block text-sm font-semibold text-slate-500">
              Completed
            </span>

            <strong class="mt-1 block text-base text-slate-900">
              {{ formatDateTime(selectedAppointment.completed_at) }}
            </strong>
          </div>
        </div>

        <div class="mt-5 rounded-2xl border border-slate-200 bg-slate-50 p-4">
          <h4 class="text-base font-bold text-slate-900">
            Reason
          </h4>

          <p class="mt-2 text-sm leading-6 text-slate-600">
            {{ selectedAppointment.reason || "No reason provided." }}
          </p>
        </div>

        <div class="mt-6">
          <h4 class="text-base font-bold text-slate-900">
            Reschedule History
          </h4>

          <div
            v-if="selectedHistory.length === 0"
            class="mt-3 rounded-2xl border border-dashed border-slate-300 bg-slate-50 p-4 text-sm text-slate-500"
          >
            No reschedule history found.
          </div>

          <div class="mt-3 flex flex-col gap-3">
            <div
              v-for="item in selectedHistory"
              :key="item.id"
              class="flex flex-col gap-3 rounded-2xl border border-slate-200 bg-slate-50 p-4 md:flex-row md:items-start md:justify-between"
            >
              <div>
                <strong class="text-sm text-slate-900">
                  {{ formatDateTime(item.old_slot_start || item.old_slot_time) }}
                  →
                  {{ formatDateTime(item.new_slot_start || item.new_slot_time) }}
                </strong>

                <p class="mt-1 text-sm text-slate-500">
                  {{ item.reason || "No reason provided." }}
                </p>
              </div>

              <span class="text-sm font-semibold text-slate-500">
                {{ item.changed_by_name || item.rescheduled_by_name || "Unknown" }}
              </span>
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>