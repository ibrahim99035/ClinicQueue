<template>
  <div class="space-y-6 bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 font-sans">
    <PageHeader
      title="Check-In Desk"
      subtitle="Check in patients for their appointments"
    />

    <div v-if="loading" class="py-8 text-center font-sans text-sm text-slate-500 dark:text-slate-400">
      Loading appointments...
    </div>
    <div v-else-if="confirmedAppointments.length === 0" class="rounded border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-8 text-center font-sans text-sm text-slate-500 dark:text-slate-400">
      <p>No confirmed appointments today</p>
    </div>

    <div v-else class="space-y-4">
      <h2 class="font-sans text-xl font-bold leading-tight text-slate-900 dark:text-slate-100">Today's Confirmed Appointments</h2>
      <div
        v-for="appointment in confirmedAppointments"
        :key="appointment.id"
        class="rounded border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-4"
      >
        <div class="mb-4 flex items-start justify-between gap-4">
          <div>
            <h3 class="font-sans text-lg font-semibold text-slate-900 dark:text-slate-100">
              {{ appointment.patient?.user?.name || "Patient" }}
            </h3>
            <p class="font-mono text-[11px] uppercase tracking-wide text-slate-500 dark:text-slate-400">
              Dr. {{ appointment.doctor?.name }}
            </p>
            <p class="font-mono text-[11px] uppercase tracking-wide text-slate-500 dark:text-slate-400">
              Slot: {{ formatDateTime(appointment.slot?.start) }}
            </p>
          </div>
          <StatusBadge :status="appointment.status" />
        </div>

        <div class="flex gap-2">
          <button
            @click="checkIn(appointment.id)"
            :disabled="appointment.status === 'checked_in'"
            class="rounded bg-blue-600 px-4 py-2 font-mono text-[11px] uppercase tracking-wider text-white transition-all duration-150 cursor-pointer hover:bg-blue-700 hover:-translate-y-px disabled:cursor-not-allowed disabled:opacity-60"
          >
            {{ appointment.status === "checked_in" ? "Checked In" : "Check In" }}
          </button>
          <button
            v-if="isPastSlotTime(appointment.slot?.start)"
            @click="markNoShow(appointment.id)"
            class="rounded border border-red-200 dark:border-red-800 px-4 py-2 font-mono text-[11px] uppercase tracking-wider text-red-600 dark:text-red-400 transition-all duration-150 cursor-pointer hover:bg-danger/10"
          >
            Mark No Show
          </button>
        </div>
      </div>
    </div>

    <!-- Current Queue -->
    <div
      v-if="checkedInAppointments.length > 0"
      class="rounded border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-4"
    >
      <h2 class="mb-4 font-sans text-xl font-bold leading-tight text-slate-900 dark:text-slate-100">Current Queue</h2>
      <div class="space-y-2">
        <div
          v-for="appointment in checkedInAppointments"
          :key="appointment.id"
          class="flex items-center justify-between rounded border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800 p-3"
        >
          <div>
            <p class="font-sans text-sm font-semibold text-slate-900 dark:text-slate-100">{{ appointment.patient?.user?.name }}</p>
            <p class="font-mono text-[11px] uppercase tracking-wide text-slate-500 dark:text-slate-400">
              Checked in: {{ formatTime(appointment.checked_in_at) }}
            </p>
          </div>
          <span class="font-mono text-[11px] uppercase tracking-wide text-slate-500 dark:text-slate-400">
            Waiting: {{ getWaitingDuration(appointment.checked_in_at) }} min
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue";
import PageHeader from "../../components/PageHeader.vue";
import StatusBadge from "../../components/StatusBadge.vue";
import useToast from "../../composables/useToast.js";
import { useAppointmentsStore } from "../../stores/appointments";

const toast = useToast();
const appointmentsStore = useAppointmentsStore();
const loading = ref(false);
let refreshTimer = null;

const today = new Date().toDateString();

const confirmedAppointments = computed(() =>
  appointmentsStore.list.filter(
    (a) =>
      a.status === "confirmed" &&
      new Date(a.slot?.start).toDateString() === today
  )
);

const checkedInAppointments = computed(() =>
  appointmentsStore.list.filter(
    (a) =>
      a.status === "checked_in" &&
      new Date(a.slot?.start).toDateString() === today
  )
);

onMounted(async () => {
  loading.value = true;
  await appointmentsStore.fetchAppointments();
  loading.value = false;

  // Refresh every 30 seconds
  refreshTimer = setInterval(async () => {
    await appointmentsStore.fetchAppointments();
  }, 30000);
});

onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer);
  }
});

async function checkIn(appointmentId) {
  try {
    await appointmentsStore.checkInAppointment(appointmentId);
    toast.success("Patient checked in");
    await appointmentsStore.fetchAppointments();
  } catch (err) {
    toast.error("Failed to check in patient");
  }
}

async function markNoShow(appointmentId) {
  if (!confirm("Mark this appointment as no-show?")) return;
  try {
    await appointmentsStore.markNoShowAppointment(appointmentId);
    toast.success("Marked as no-show");
    await appointmentsStore.fetchAppointments();
  } catch (err) {
    toast.error("Failed to mark no-show");
  }
}

function formatDateTime(dateTime) {
  if (!dateTime) return "";
  return new Date(dateTime).toLocaleString("en-US", {
    hour: "2-digit",
    minute: "2-digit",
  });
}

function formatTime(dateTime) {
  if (!dateTime) return "";
  return new Date(dateTime).toLocaleTimeString("en-US", {
    hour: "2-digit",
    minute: "2-digit",
  });
}

function isPastSlotTime(slotStart) {
  if (!slotStart) return false;
  return new Date(slotStart) < new Date();
}

function getWaitingDuration(checkedInAt) {
  if (!checkedInAt) return 0;
  const now = new Date();
  const checkedIn = new Date(checkedInAt);
  return Math.round((now - checkedIn) / 60000);
}
</script>
