<template>
  <div class="space-y-6 bg-bg text-text1 font-sans">
    <PageHeader
      title="Check-In Desk"
      subtitle="Check in patients for their appointments"
    />

    <!-- Status Filter -->
    <div class="flex flex-wrap gap-2">
      <button
        v-for="status in statuses"
        :key="status"
        @click="selectedStatus = status"
        :class="[
          'rounded px-3 py-2 font-mono text-[11px] uppercase tracking-mono-wide transition-all duration-150',
          selectedStatus === status
            ? 'bg-accent text-black'
            : 'border border-border bg-surface text-text1 hover:bg-surface2'
        ]"
      >
        {{ status === 'all' ? 'All' : statusLabels[status] }}
      </button>
    </div>

    <div v-if="loading" class="py-8 text-center font-sans text-sm text-text2">
      Loading appointments...
    </div>
    <div v-else-if="filteredAppointments.length === 0" class="rounded border border-border bg-surface p-8 text-center font-sans text-sm text-text2">
      <p>No {{ selectedStatus === 'all' ? '' : statusLabels[selectedStatus] }} appointments today</p>
    </div>

    <!-- Appointments List -->
    <div v-else class="space-y-4">
      <div
        v-for="appointment in filteredAppointments"
        :key="appointment.id"
        class="rounded border border-border bg-surface p-4"
      >
        <div class="mb-4 flex items-start justify-between gap-4">
          <div>
            <h3 class="font-sans text-lg font-semibold text-text1">
              {{ getPatientName(appointment) }}
            </h3>
            <p class="font-mono text-[11px] uppercase tracking-mono text-text2">
            Dr. {{ getDoctorName(appointment) }}            </p>
            <p class="font-mono text-[11px] uppercase tracking-mono text-text2">
            Slot: {{ formatDateTime(getAppointmentDateTime(appointment)) }}            </p>
          </div>
          <StatusBadge :status="appointment.status" />
        </div>

        <div class="flex gap-2">
          <!-- REQUESTED: Approve and Cancel -->
          <template v-if="normalizeStatus(appointment.status) === 'requested'">
            <button
              @click="confirmAppointmentAction(appointment.id)"
              class="rounded bg-accent px-4 py-2 font-mono text-[11px] uppercase tracking-mono-wide text-black transition-all duration-150 cursor-pointer hover:bg-accent-dim hover:-translate-y-px"
            >
              Approve
            </button>
            <button
              @click="cancelAppointmentAction(appointment.id)"
              class="rounded border border-danger px-4 py-2 font-mono text-[11px] uppercase tracking-mono-wide text-danger transition-all duration-150 cursor-pointer hover:bg-danger/10"
            >
              Cancel
            </button>
          </template>

          <!-- CONFIRMED: Check In, Cancel, and Mark No Show if past -->
          <template v-else-if="normalizeStatus(appointment.status) === 'confirmed'">
            <button
              @click="checkIn(appointment.id)"
              class="rounded bg-accent px-4 py-2 font-mono text-[11px] uppercase tracking-mono-wide text-black transition-all duration-150 cursor-pointer hover:bg-accent-dim hover:-translate-y-px"
            >
              Check In
            </button>
            <button
              @click="cancelAppointmentAction(appointment.id)"
              class="rounded border border-danger px-4 py-2 font-mono text-[11px] uppercase tracking-mono-wide text-danger transition-all duration-150 cursor-pointer hover:bg-danger/10"
            >
              Cancel
            </button>
            <button
              v-if="isPastSlotTime(getAppointmentDateTime(appointment))"
              @click="markNoShow(appointment.id)"
              class="rounded border border-danger px-4 py-2 font-mono text-[11px] uppercase tracking-mono-wide text-danger transition-all duration-150 cursor-pointer hover:bg-danger/10"
            >
              Mark No Show
            </button>
          </template>

          <!-- CHECKED_IN, COMPLETED, CANCELLED, NO_SHOW: view only -->
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
const selectedStatus = ref("all");
let refreshTimer = null;

const today = new Date().toDateString();
const statuses = ["all", "requested", "confirmed", "checked_in", "completed", "cancelled", "no_show"];
const statusLabels = {
  requested: "Requested",
  confirmed: "Confirmed",
  checked_in: "Checked In",
  completed: "Completed",
  cancelled: "Cancelled",
  no_show: "No Show",
};

const todayAppointments = computed(() => {
  const appointments = Array.isArray(appointmentsStore.list)
    ? appointmentsStore.list
    : [];

  return appointments.filter((appointment) => {
    const dateTime = getAppointmentDateTime(appointment);

    if (!dateTime) {
      return false;
    }

    return new Date(dateTime).toDateString() === today;
  });
});

const filteredAppointments = computed(() => {
  if (selectedStatus.value === "all") {
    return todayAppointments.value;
  }

  return todayAppointments.value.filter(
    (appointment) =>
      normalizeStatus(appointment.status) === selectedStatus.value
  );
});

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

function normalizeStatus(status) {
  return String(status || "").toLowerCase();
}

function getAppointmentDateTime(appointment) {
  return (
    appointment.slot_time ||
    appointment.slot?.start ||
    appointment.appointment_datetime ||
    appointment.start ||
    appointment.datetime ||
    appointment.slot_start ||
    appointment.start_time ||
    null
  );
}

function getPatientName(appointment) {
  return (
    appointment.patient_name ||
    appointment.patient?.user?.name ||
    appointment.patient?.name ||
    appointment.patient?.full_name ||
    "Patient"
  );
}

function getDoctorName(appointment) {
  return (
    appointment.doctor_name ||
    appointment.doctor?.name ||
    appointment.doctor?.user?.name ||
    appointment.doctor?.full_name ||
    "Doctor"
  );
}

async function confirmAppointmentAction(appointmentId) {
  try {
    await appointmentsStore.confirmAppointment(appointmentId);
    toast.success("Appointment approved");
    await appointmentsStore.fetchAppointments();
  } catch (err) {
    console.error("Confirm error:", err.response?.data?.detail || err.message);
    const errorDetail = err.response?.data?.detail || "Failed to approve appointment";
    toast.error(errorDetail);
  }
}

async function cancelAppointmentAction(appointmentId) {
  if (!confirm("Cancel this appointment?")) return;
  try {
    await appointmentsStore.cancelAppointment(appointmentId);
    toast.success("Appointment cancelled");
    await appointmentsStore.fetchAppointments();
  } catch (err) {
    // Log detailed error for debugging
    console.error("Cancel error status:", err.response?.status);
    console.error("Cancel error data:", err.response?.data);
    console.error("Cancel error headers:", err.response?.headers);
    
    // Show backend error detail if available
    const errorDetail = err.response?.data?.detail || "Failed to cancel appointment";
    toast.error(errorDetail);
  }
}

async function checkIn(appointmentId) {
  try {
    await appointmentsStore.checkInAppointment(appointmentId);
    toast.success("Patient checked in");
    await appointmentsStore.fetchAppointments();
  } catch (err) {
    console.error("Check-in error:", err.response?.data?.detail || err.message);
    const errorDetail = err.response?.data?.detail || "Failed to check in patient";
    toast.error(errorDetail);
  }
}

async function markNoShow(appointmentId) {
  if (!confirm("Mark this appointment as no-show?")) return;
  try {
    await appointmentsStore.markNoShowAppointment(appointmentId);
    toast.success("Marked as no-show");
    await appointmentsStore.fetchAppointments();
  } catch (err) {
    console.error("Mark no-show error:", err.response?.data?.detail || err.message);
    const errorDetail = err.response?.data?.detail || "Failed to mark no-show";
    toast.error(errorDetail);
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
