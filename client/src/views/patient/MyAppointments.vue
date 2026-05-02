<template>
  <div class="space-y-6 bg-bg text-text1 font-sans">
    <PageHeader
      title="My Appointments"
      subtitle="Manage your appointments"
    />

    <div v-if="loading" class="py-8 text-center font-sans text-sm text-text2">
      Loading appointments...
    </div>
    <div
      v-else-if="filteredAppointments.length === 0"
      class="rounded border border-border bg-surface p-8 text-center font-sans text-sm text-text2"
    >
      <p>No appointments found</p>
      <router-link to="/patient/book" class="font-mono text-[11px] uppercase tracking-mono text-accent transition-all duration-150 cursor-pointer hover:text-accent-dim">
        Book your first appointment
      </router-link>
    </div>

    <div
      v-else-if="errorMessage"
      class="rounded border border-danger/40 bg-surface p-8 text-center font-sans text-sm text-danger"
    >
      <p>{{ errorMessage }}</p>
    </div>

    <div v-else class="space-y-4">
      <div
        v-for="appointment in filteredAppointments"
        :key="appointment.id"
        class="rounded border bg-surface p-4"
        :class="getStatusBorderColor(appointment.status)"
      >
        <div class="mb-4 flex items-start justify-between gap-4">
          <div>
            <h3 class="font-sans text-lg font-bold text-text1">
              {{
                appointment.doctorName && appointment.doctorName !== "Unknown"
                  ? `Dr. ${appointment.doctorName}`
                  : "Dr. Unknown"
              }}
            </h3>
          </div>
          <StatusBadge :status="appointment.status || 'UNKNOWN'" />
        </div>

        <div class="mb-4 grid gap-4 text-sm md:grid-cols-2">
          <div>
            <p class="font-mono text-[11px] uppercase tracking-mono text-text2">Date & Time</p>
            <p class="font-sans text-sm font-semibold text-text1">{{ formatDateTime(appointment.appointmentDateTime) }}</p>
          </div>
          <div>
            <p class="font-mono text-[11px] uppercase tracking-mono text-text2">Reason</p>
            <p class="font-sans text-sm font-semibold text-text1">{{ appointment.reason || "Not specified" }}</p>
          </div>
          <div v-if="appointment.status === 'CHECKED_IN'">
            <p class="font-mono text-[11px] uppercase tracking-mono text-text2">Checked In</p>
            <p class="font-sans text-sm font-semibold text-text1">{{ formatDateTime(appointment.checked_in_at) }}</p>
          </div>
          <div v-if="appointment.status === 'COMPLETED'">
            <p class="font-mono text-[11px] uppercase tracking-mono text-text2">Completed</p>
            <p class="font-sans text-sm font-semibold text-text1">{{ formatDateTime(appointment.completed_at) }}</p>
          </div>
        </div>

        <div class="flex gap-2 flex-wrap">
          <button
            v-if="['REQUESTED', 'CONFIRMED'].includes(appointment.status)"
            @click="openRescheduleModal(appointment)"
            class="rounded border border-border px-4 py-2 font-mono text-[11px] uppercase tracking-mono text-text2 transition-all duration-150 cursor-pointer hover:border-accent hover:text-text1"
          >
            Reschedule
          </button>
          <button
            v-if="['REQUESTED', 'CONFIRMED'].includes(appointment.status)"
            @click="cancelAppointment(appointment.id)"
            class="rounded border border-danger px-4 py-2 font-mono text-[11px] uppercase tracking-mono-wide text-danger transition-all duration-150 cursor-pointer hover:bg-danger/10"
          >
            Cancel
          </button>
          <router-link
            v-if="appointment.status === 'COMPLETED'"
            :to="`/emr/appointments/${appointment.id}/consultation`"
            class="inline-flex items-center justify-center rounded bg-accent px-4 py-2 font-mono text-[11px] uppercase tracking-mono-wide text-black transition-all duration-150 cursor-pointer hover:bg-accent-dim hover:-translate-y-px"
          >
            View Consultation
          </router-link>
        </div>
      </div>

    </div>

    <!-- Reschedule Modal -->
    <div
      v-if="showRescheduleModal"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/70"
    >
      <div class="mx-4 w-full max-w-md space-y-4 rounded border border-border bg-surface p-6">
        <h3 class="font-sans text-xl font-bold leading-tight text-text1">Reschedule Appointment</h3>

        <div>
          <label class="mb-1.5 block font-mono text-[11px] uppercase tracking-mono text-text2">New Date</label>
          <input
            v-model="rescheduleDate"
            type="date"
            :min="new Date().toISOString().split('T')[0]"
            class="w-full rounded border border-border bg-surface px-3 py-2 font-mono text-sm text-text1 outline-none transition-all duration-150 focus:border-accent focus:ring-2 focus:ring-accent/10"
            @change="fetchRescheduleSlots"
          />
        </div>

        <div v-if="rescheduleSlots.length > 0">
          <label class="mb-1.5 block font-mono text-[11px] uppercase tracking-mono text-text2">New Time</label>
          <div class="grid grid-cols-2 gap-2">
            <button
              v-for="slot in rescheduleSlots"
              :key="slot.id"
              @click="rescheduleSlot = slot"
              :class="[
                'rounded border px-3 py-2 transition-all duration-150 cursor-pointer font-mono text-sm',
                rescheduleSlot?.id === slot.id
                  ? 'border-accent/40 bg-surface2 text-accent'
                  : 'border-border text-text1 hover:border-accent/30',
              ]"
            >
              {{ formatTime(slot.start_datetime) }}
            </button>
          </div>
        </div>

        <div class="flex gap-3">
          <button
            @click="closeRescheduleModal"
            class="flex-1 rounded border border-border px-4 py-2 font-mono text-[11px] uppercase tracking-mono text-text2 transition-all duration-150 cursor-pointer hover:border-accent hover:text-text1"
          >
            Cancel
          </button>
          <button
            @click="submitReschedule"
            :disabled="!rescheduleSlot || rescheduling"
            class="flex-1 rounded bg-accent px-4 py-2 font-mono text-[11px] uppercase tracking-mono-wide text-black transition-all duration-150 cursor-pointer hover:bg-accent-dim hover:-translate-y-px disabled:cursor-not-allowed disabled:opacity-60"
          >
            {{ rescheduling ? "Rescheduling..." : "Confirm" }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from "vue";
import PageHeader from "../../components/PageHeader.vue";
import StatusBadge from "../../components/StatusBadge.vue";
import useToast from "../../composables/useToast.js";
import * as appointmentApi from "../../api/appointments.js";
import * as schedulingApi from "../../api/scheduling.js";

const toast = useToast();

const loading = ref(false);
const errorMessage = ref("");
const appointments = ref([]);
const filteredAppointments = computed(() => {
  return appointments.value;
});

const showRescheduleModal = ref(false);
const currentAppointment = ref(null);
const rescheduleDate = ref("");
const rescheduleSlot = ref(null);
const rescheduleSlots = ref([]);
const rescheduling = ref(false);

onMounted(async () => {
  await fetchAppointments();
});

async function fetchAppointments() {
  loading.value = true;
  errorMessage.value = "";

  try {
    const response = await appointmentApi.getMyAppointments();
    const data = response?.data ?? response;

    console.log("Patient appointments raw response:", data);

    const rawAppointments = Array.isArray(data)
      ? data
      : data.results || [];

    appointments.value = rawAppointments.map(normalizeAppointment);

    console.log("Normalized appointments:", appointments.value);
  } catch (error) {
    console.error("Failed to load appointments:", error);
    errorMessage.value = "Failed to load appointments.";
  } finally {
    loading.value = false;
  }
}

function normalizeAppointment(appointment) {
  return {
    ...appointment,
    doctorName:
      appointment.doctor_name ||
      appointment.doctorName ||
      "Unknown",
    appointmentDateTime:
      appointment.appointment_datetime ||
      appointment.slot_time ||
      appointment.slotTime ||
      appointment.start_datetime ||
      "",
    reason:
      appointment.reason ||
      "Not specified",
    status:
      appointment.status ||
      "UNKNOWN",
    doctorId: appointment.doctor_id || null,
  };
}

function getStatusBorderColor(status) {
  const colors = {
    REQUESTED: "border-yellow-500",
    CONFIRMED: "border-blue-500",
    CHECKED_IN: "border-purple-500",
    COMPLETED: "border-green-500",
    CANCELLED: "border-red-500",
    NO_SHOW: "border-gray-500",
  };
  return colors[status] || "border-gray-300";
}

function formatDateTime(dateTime) {
  if (!dateTime) return "Not scheduled";

  const date = new Date(dateTime);
  if (Number.isNaN(date.getTime())) {
    return dateTime;
  }

  return date.toLocaleString();
}

function formatTime(timeString) {
  if (!timeString) return "";
  return new Date(timeString).toLocaleTimeString("en-US", {
    hour: "2-digit",
    minute: "2-digit",
  });
}

async function cancelAppointment(appointmentId) {
  if (!confirm("Are you sure you want to cancel this appointment?")) return;
  try {
    await appointmentApi.cancelAppointment(appointmentId);
    toast.success("Appointment cancelled");
    await fetchAppointments();
  } catch (err) {
    toast.error("Failed to cancel appointment");
  }
}

function openRescheduleModal(apt) {
  currentAppointment.value = apt;
  rescheduleDate.value = "";
  rescheduleSlot.value = null;
  rescheduleSlots.value = [];
  showRescheduleModal.value = true;
}

function closeRescheduleModal() {
  showRescheduleModal.value = false;
  currentAppointment.value = null;
}

async function fetchRescheduleSlots() {
  if (!rescheduleDate.value || !currentAppointment.value) return;
  try {
    rescheduleSlots.value = await schedulingApi.getAvailableSlots({
      doctor: currentAppointment.value.doctorId,
      date: rescheduleDate.value,
    });
    rescheduleSlot.value = null;
  } catch (err) {
    toast.error("Failed to load slots");
  }
}

async function submitReschedule() {
  if (!rescheduleSlot.value) return;
  rescheduling.value = true;
  try {
    await appointmentApi.rescheduleAppointment(currentAppointment.value.id, {
      new_slot: rescheduleSlot.value.id,
    });
    toast.success("Appointment rescheduled");
    await fetchAppointments();
    closeRescheduleModal();
  } catch (err) {
    toast.error("Failed to reschedule appointment");
  } finally {
    rescheduling.value = false;
  }
}
</script>
