<template>
  <div class="space-y-6 bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 font-sans">
    <PageHeader title="Doctor Dashboard" subtitle="Your clinical workspace" />

    <div class="grid gap-4 md:grid-cols-3">
      <StatCard label="Today's Queue" :value="todayQueueCount" color="blue" />
      <StatCard label="Upcoming" :value="upcomingCount" color="amber" />
      <StatCard label="Completed Today" :value="completedToday" color="green" />
    </div>

    <div class="grid gap-6 lg:grid-cols-2">
      <div class="rounded border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-4">
        <h2 class="mb-4 font-sans text-xl font-bold leading-tight text-slate-900 dark:text-slate-100">Quick Actions</h2>
        <div class="space-y-2">
          <router-link
            to="/doctor/queue"
            class="block rounded border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800 px-4 py-3 text-center font-mono text-[11px] uppercase tracking-wide text-slate-900 dark:text-slate-100 transition-all duration-150 cursor-pointer hover:border-blue-500 hover:text-blue-600 dark:hover:text-blue-400"
          >
            View Appointment Queue
          </router-link>
          <router-link
            to="/doctor/schedule"
            class="block rounded border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800 px-4 py-3 text-center font-mono text-[11px] uppercase tracking-wide text-slate-900 dark:text-slate-100 transition-all duration-150 cursor-pointer hover:border-blue-500 hover:text-blue-600 dark:hover:text-blue-400"
          >
            View My Schedule
          </router-link>
        </div>
      </div>

      <div class="rounded border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-4">
        <h2 class="mb-4 font-sans text-xl font-bold leading-tight text-slate-900 dark:text-slate-100">Today's Schedule</h2>
        <div v-if="todayAppointments.length === 0" class="font-sans text-sm text-slate-500 dark:text-slate-400">
          No appointments today
        </div>
        <div v-else class="space-y-2">
          <div
            v-for="apt in todayAppointments.slice(0, 5)"
            :key="apt.id"
            class="flex items-center justify-between rounded border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800 p-3"
          >
            <span class="font-mono text-sm text-slate-900 dark:text-slate-100">{{ formatTime(apt.slot_time) }}</span>
            <StatusBadge :status="apt.status" />
          </div>
        </div>
      </div>
    </div>

    <div class="rounded border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-4">
      <div class="flex flex-col gap-2 md:flex-row md:items-start md:justify-between">
        <div>
          <h2 class="font-sans text-xl font-bold leading-tight text-slate-900 dark:text-slate-100">Patient History Search</h2>
          <p class="mt-1 font-sans text-sm text-slate-500 dark:text-slate-400">
            Search previous appointments and consultation records for follow-up visits.
          </p>
        </div>
        <button
          type="button"
          @click="loadHistoryAppointments"
          :disabled="historyLoading"
          class="rounded bg-blue-600 px-4 py-2 font-mono text-[11px] uppercase tracking-wider text-white transition-all duration-150 cursor-pointer hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {{ historyLoading ? "Loading..." : "Refresh" }}
        </button>
      </div>

      <form class="mt-5 grid gap-3 md:grid-cols-5" @submit.prevent="loadHistoryAppointments">
        <div class="md:col-span-2">
          <label class="mb-1.5 block font-mono text-[11px] uppercase tracking-wide text-slate-500 dark:text-slate-400">Search</label>
          <input
            v-model.trim="historyFilters.search"
            type="text"
            placeholder="Search by patient name, phone, email, reason, or appointment ID"
            class="w-full rounded border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 px-3 py-2 font-mono text-sm text-slate-900 dark:text-slate-100 placeholder:text-slate-400 outline-none transition-all duration-150 focus:border-blue-500 focus:ring-2 focus:ring-blue-100 dark:focus:ring-blue-900/30"
          />
        </div>

        <div>
          <label class="mb-1.5 block font-mono text-[11px] uppercase tracking-wide text-slate-500 dark:text-slate-400">Status</label>
          <select
            v-model="historyFilters.status"
            class="w-full rounded border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 px-3 py-2 font-mono text-sm text-slate-900 dark:text-slate-100 outline-none transition-all duration-150 focus:border-blue-500 focus:ring-2 focus:ring-blue-100 dark:focus:ring-blue-900/30"
          >
            <option value="">All statuses</option>
            <option value="REQUESTED">Requested</option>
            <option value="CONFIRMED">Confirmed</option>
            <option value="CHECKED_IN">Checked In</option>
            <option value="COMPLETED">Completed</option>
            <option value="CANCELLED">Cancelled</option>
            <option value="NO_SHOW">No Show</option>
          </select>
        </div>

        <div>
          <label class="mb-1.5 block font-mono text-[11px] uppercase tracking-wide text-slate-500 dark:text-slate-400">From</label>
          <input
            v-model="historyFilters.date_from"
            type="date"
            class="w-full rounded border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 px-3 py-2 font-mono text-sm text-slate-900 dark:text-slate-100 outline-none transition-all duration-150 focus:border-blue-500 focus:ring-2 focus:ring-blue-100 dark:focus:ring-blue-900/30"
          />
        </div>

        <div>
          <label class="mb-1.5 block font-mono text-[11px] uppercase tracking-wide text-slate-500 dark:text-slate-400">To</label>
          <input
            v-model="historyFilters.date_to"
            type="date"
            class="w-full rounded border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 px-3 py-2 font-mono text-sm text-slate-900 dark:text-slate-100 outline-none transition-all duration-150 focus:border-blue-500 focus:ring-2 focus:ring-blue-100 dark:focus:ring-blue-900/30"
          />
        </div>

        <div class="flex gap-2 md:col-span-5">
          <button
            type="submit"
            :disabled="historyLoading"
            class="rounded bg-blue-600 px-4 py-2 font-mono text-[11px] uppercase tracking-wider text-white transition-all duration-150 cursor-pointer hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
          >
            Search
          </button>
          <button
            type="button"
            @click="resetHistoryFilters"
            class="rounded border border-slate-200 dark:border-slate-800 px-4 py-2 font-mono text-[11px] uppercase tracking-wide text-slate-500 dark:text-slate-400 transition-all duration-150 cursor-pointer hover:border-blue-500 hover:text-slate-900 dark:hover:text-slate-100"
          >
            Reset
          </button>
        </div>
      </form>

      <div v-if="historyError" class="mt-4 rounded border border-red-200 dark:border-red-800/40 bg-white dark:bg-slate-900 px-4 py-3 font-sans text-sm text-red-600 dark:text-red-400">
        {{ historyError }}
      </div>

      <div v-if="historyLoading" class="mt-5 py-6 text-center font-sans text-sm text-slate-500 dark:text-slate-400">
        Loading history...
      </div>

      <div v-else-if="historyAppointments.length === 0" class="mt-5 rounded border border-dashed border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800 p-6 text-center font-sans text-sm text-slate-500 dark:text-slate-400">
        No matching appointments found.
      </div>

      <div v-else class="mt-5 overflow-x-auto">
        <table class="w-full min-w-[850px] text-left text-sm">
          <thead class="font-mono text-[11px] uppercase tracking-wide text-slate-500 dark:text-slate-400">
            <tr>
              <th class="border-b border-slate-200 dark:border-slate-800 px-4 py-3">Patient</th>
              <th class="border-b border-slate-200 dark:border-slate-800 px-4 py-3">Date / Time</th>
              <th class="border-b border-slate-200 dark:border-slate-800 px-4 py-3">Status</th>
              <th class="border-b border-slate-200 dark:border-slate-800 px-4 py-3">Reason</th>
              <th class="border-b border-slate-200 dark:border-slate-800 px-4 py-3">Consultation</th>
              <th class="border-b border-slate-200 dark:border-slate-800 px-4 py-3">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="appointment in historyAppointments"
              :key="appointment.id"
              class="text-slate-900 dark:text-slate-100 transition hover:bg-slate-50 dark:hover:bg-slate-800"
            >
              <td class="border-b border-slate-100 dark:border-slate-800 px-4 py-3">
                <div class="font-semibold">{{ appointment.patientName }}</div>
                <div v-if="appointment.patientEmail" class="mt-1 text-xs text-slate-500 dark:text-slate-400">{{ appointment.patientEmail }}</div>
                <div v-if="appointment.patientPhone" class="mt-1 text-xs text-slate-500 dark:text-slate-400">{{ appointment.patientPhone }}</div>
              </td>
              <td class="border-b border-slate-100 dark:border-slate-800 px-4 py-3">{{ formatDateTime(appointment.appointmentDateTime) }}</td>
              <td class="border-b border-slate-100 dark:border-slate-800 px-4 py-3"><StatusBadge :status="appointment.status" /></td>
              <td class="border-b border-slate-100 dark:border-slate-800 px-4 py-3 max-w-xs truncate">{{ appointment.reason }}</td>
              <td class="border-b border-slate-100 dark:border-slate-800 px-4 py-3">
                <span v-if="appointment.hasConsultation" class="rounded bg-green-100 px-2 py-1 text-xs font-semibold text-green-700 dark:bg-green-950/50 dark:text-green-300">Available</span>
                <span v-else class="text-xs text-slate-500 dark:text-slate-400">No consultation record</span>
              </td>
              <td class="border-b border-slate-100 dark:border-slate-800 px-4 py-3">
                <div class="flex flex-wrap gap-2">
                  <router-link
                    v-if="appointment.hasConsultation"
                    :to="`/emr/appointments/${appointment.id}/consultation`"
                    class="rounded border border-slate-200 dark:border-slate-800 px-3 py-2 font-mono text-[11px] uppercase tracking-wide text-slate-500 dark:text-slate-400 transition-all duration-150 cursor-pointer hover:border-blue-500 hover:text-slate-900 dark:hover:text-slate-100"
                  >
                    View Consultation
                  </router-link>
                  <router-link
                    v-if="appointment.hasConsultation && appointment.consultationId"
                    :to="`/emr/consultations/${appointment.consultationId}/edit`"
                    class="rounded bg-blue-600 px-3 py-2 font-mono text-[11px] uppercase tracking-wider text-white transition-all duration-150 cursor-pointer hover:bg-blue-700"
                  >
                    Edit Consultation
                  </router-link>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from "vue";
import PageHeader from "../../components/PageHeader.vue";
import StatCard from "../../components/StatCard.vue";
import StatusBadge from "../../components/StatusBadge.vue";
import { useAppointmentsStore } from "../../stores/appointments";
import { getDoctorAppointments } from "../../api/appointments";

const appointmentsStore = useAppointmentsStore();
const loading = ref(false);
const historyLoading = ref(false);
const historyError = ref("");
const historyAppointments = ref([]);

const historyFilters = reactive({
  search: "",
  status: "",
  date_from: "",
  date_to: "",
});

const todayAppointments = computed(() => {
  const today = new Date().toDateString();
  return appointmentsStore.list.filter(
    (a) =>
      new Date(a.slot_time).toDateString() === today &&
      ["REQUESTED", "CONFIRMED", "CHECKED_IN"].includes(a.status)
  );
});

const todayQueueCount = computed(
  () => todayAppointments.value.filter((a) => a.status === "CHECKED_IN").length
);
const upcomingCount = computed(() =>
  appointmentsStore.list.filter(
    (a) =>
      ["REQUESTED", "CONFIRMED"].includes(a.status) &&
      new Date(a.slot_time) > new Date()
  ).length
);
const completedToday = computed(() => {
  const today = new Date().toDateString();
  return appointmentsStore.list.filter(
    (a) =>
      a.status === "COMPLETED" &&
      a.completed_at &&
      new Date(a.completed_at).toDateString() === today
  ).length;
});

function formatTime(dateTime) {
  if (!dateTime) return "";
  return new Date(dateTime).toLocaleTimeString("en-US", {
    hour: "2-digit",
    minute: "2-digit",
  });
}

function formatDateTime(dateTime) {
  if (!dateTime) return "Not scheduled";
  return new Date(dateTime).toLocaleString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function normalizeAppointment(appointment) {
  return {
    ...appointment,
    id: appointment.id,
    patientName:
      appointment.patient_name ||
      appointment.patientName ||
      appointment.patient?.name ||
      appointment.patient?.full_name ||
      "Unknown Patient",
    patientEmail:
      appointment.patient_email ||
      appointment.patientEmail ||
      appointment.patient?.email ||
      "",
    patientPhone:
      appointment.patient_phone ||
      appointment.patientPhone ||
      appointment.patient?.phone ||
      "",
    doctorName:
      appointment.doctor_name ||
      appointment.doctorName ||
      appointment.doctor?.name ||
      appointment.doctor?.full_name ||
      "Unknown Doctor",
    appointmentDateTime:
      appointment.slot_time ||
      appointment.appointment_datetime ||
      appointment.appointmentDateTime ||
      appointment.datetime ||
      "",
    reason:
      appointment.reason ||
      "Not specified",
    status:
      appointment.status ||
      "UNKNOWN",
    hasConsultation:
      appointment.has_consultation ||
      appointment.hasConsultation ||
      Boolean(appointment.consultation_id || appointment.consultationId),
    consultationId:
      appointment.consultation_id ||
      appointment.consultationId ||
      null,
  };
}

function buildHistoryParams() {
  const params = {};

  if (historyFilters.search) {
    params.search = historyFilters.search;
  }
  if (historyFilters.status) {
    params.status = historyFilters.status;
  }
  if (historyFilters.date_from) {
    params.date_from = historyFilters.date_from;
  }
  if (historyFilters.date_to) {
    params.date_to = historyFilters.date_to;
  }

  return params;
}

async function loadHistoryAppointments() {
  historyLoading.value = true;
  historyError.value = "";

  try {
    const data = await getDoctorAppointments(buildHistoryParams());
    historyAppointments.value = data.map(normalizeAppointment);
  } catch (error) {
    historyError.value = error.response?.data?.detail || "Failed to load patient history.";
  } finally {
    historyLoading.value = false;
  }
}

async function resetHistoryFilters() {
  historyFilters.search = "";
  historyFilters.status = "";
  historyFilters.date_from = "";
  historyFilters.date_to = "";
  await loadHistoryAppointments();
}

onMounted(async () => {
  loading.value = true;
  await appointmentsStore.fetchAppointments();
  loading.value = false;
  await loadHistoryAppointments();
});
</script>
