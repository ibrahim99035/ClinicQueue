<template>
  <div class="space-y-6">
    <PageHeader
      title="Check-In Desk"
      subtitle="Check in patients for their appointments"
    />

    <div v-if="loading" class="text-center py-8 text-gray-500">
      Loading appointments...
    </div>
    <div v-else-if="confirmedAppointments.length === 0" class="bg-white rounded-lg shadow-md p-8 text-center text-gray-500">
      <p>No confirmed appointments today</p>
    </div>

    <div v-else class="space-y-4">
      <h2 class="text-lg font-semibold">Today's Confirmed Appointments</h2>
      <div
        v-for="appointment in confirmedAppointments"
        :key="appointment.id"
        class="bg-white rounded-lg shadow-md p-6 border-l-4 border-blue-500"
      >
        <div class="flex justify-between items-start mb-4">
          <div>
            <h3 class="text-lg font-semibold">
              {{ appointment.patient?.user?.name || "Patient" }}
            </h3>
            <p class="text-sm text-gray-600">
              Dr. {{ appointment.doctor?.name }}
            </p>
            <p class="text-sm text-gray-600">
              Slot: {{ formatDateTime(appointment.slot?.start) }}
            </p>
          </div>
          <StatusBadge :status="appointment.status" />
        </div>

        <div class="flex gap-2">
          <button
            @click="checkIn(appointment.id)"
            :disabled="appointment.status === 'checked_in'"
            class="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 disabled:bg-gray-300"
          >
            {{ appointment.status === "checked_in" ? "Checked In" : "Check In" }}
          </button>
          <button
            v-if="isPastSlotTime(appointment.slot?.start)"
            @click="markNoShow(appointment.id)"
            class="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600"
          >
            Mark No Show
          </button>
        </div>
      </div>
    </div>

    <!-- Current Queue -->
    <div
      v-if="checkedInAppointments.length > 0"
      class="bg-white rounded-lg shadow-md p-6"
    >
      <h2 class="text-lg font-semibold mb-4">Current Queue</h2>
      <div class="space-y-2">
        <div
          v-for="appointment in checkedInAppointments"
          :key="appointment.id"
          class="flex justify-between items-center p-3 border rounded-lg"
        >
          <div>
            <p class="font-semibold">{{ appointment.patient?.user?.name }}</p>
            <p class="text-sm text-gray-600">
              Checked in: {{ formatTime(appointment.checked_in_at) }}
            </p>
          </div>
          <span class="text-sm text-gray-500">
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
