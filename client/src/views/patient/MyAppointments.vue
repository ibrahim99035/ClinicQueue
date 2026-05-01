<template>
  <div class="space-y-6">
    <PageHeader
      title="My Appointments"
      subtitle="Manage your appointments"
    />

    <div v-if="loading" class="text-center py-8 text-gray-500">
      Loading appointments...
    </div>
    <div
      v-else-if="appointments.items.length === 0"
      class="bg-white rounded-lg shadow-md p-8 text-center text-gray-500"
    >
      <p>No appointments found</p>
      <router-link to="/patient/book" class="text-blue-600 hover:underline">
        Book your first appointment
      </router-link>
    </div>

    <div v-else class="space-y-4">
      <div
        v-for="apt in appointments.items"
        :key="apt.id"
        class="bg-white rounded-lg shadow-md p-6 border-l-4"
        :class="getStatusBorderColor(apt.status)"
      >
        <div class="flex justify-between items-start mb-4">
          <div>
            <h3 class="text-lg font-semibold">
              Dr. {{ apt.doctor?.name || "Unknown" }}
            </h3>
            <p class="text-sm text-gray-600">
              {{ apt.doctor?.specialization }}
            </p>
          </div>
          <StatusBadge :status="apt.status" />
        </div>

        <div class="grid md:grid-cols-2 gap-4 mb-4 text-sm">
          <div>
            <p class="text-gray-600">Date & Time</p>
            <p class="font-semibold">{{ formatDateTime(apt.slot?.start) }}</p>
          </div>
          <div>
            <p class="text-gray-600">Reason</p>
            <p class="font-semibold">{{ apt.reason || "Not specified" }}</p>
          </div>
          <div v-if="apt.status === 'checked_in'">
            <p class="text-gray-600">Checked In</p>
            <p class="font-semibold">{{ formatDateTime(apt.checked_in_at) }}</p>
          </div>
          <div v-if="apt.status === 'completed'">
            <p class="text-gray-600">Completed</p>
            <p class="font-semibold">{{ formatDateTime(apt.completed_at) }}</p>
          </div>
        </div>

        <div class="flex gap-2 flex-wrap">
          <button
            v-if="['requested', 'confirmed'].includes(apt.status)"
            @click="openRescheduleModal(apt)"
            class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 text-sm"
          >
            Reschedule
          </button>
          <button
            v-if="['requested', 'confirmed'].includes(apt.status)"
            @click="cancelAppointment(apt.id)"
            class="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 text-sm"
          >
            Cancel
          </button>
          <router-link
            v-if="apt.status === 'completed'"
            :to="`/emr/appointments/${apt.id}/consultation`"
            class="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 text-sm inline-block"
          >
            View Consultation
          </router-link>
        </div>
      </div>

      <!-- Pagination -->
      <div class="flex justify-center gap-2 mt-6">
        <button
          @click="appointments.prev()"
          :disabled="!appointments.hasPrevPage.value"
          class="px-4 py-2 border rounded-lg hover:bg-gray-100 disabled:opacity-50"
        >
          Previous
        </button>
        <span class="px-4 py-2">
          Page {{ appointments.page.value }} of
          {{ appointments.totalPages.value }}
        </span>
        <button
          @click="appointments.next()"
          :disabled="!appointments.hasNextPage.value"
          class="px-4 py-2 border rounded-lg hover:bg-gray-100 disabled:opacity-50"
        >
          Next
        </button>
      </div>
    </div>

    <!-- Reschedule Modal -->
    <div
      v-if="showRescheduleModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    >
      <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4 space-y-4">
        <h3 class="text-lg font-semibold">Reschedule Appointment</h3>

        <div>
          <label class="block mb-2 font-semibold">New Date</label>
          <input
            v-model="rescheduleDate"
            type="date"
            :min="new Date().toISOString().split('T')[0]"
            class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            @change="fetchRescheduleSlots"
          />
        </div>

        <div v-if="rescheduleSlots.length > 0">
          <label class="block mb-2 font-semibold">New Time</label>
          <div class="grid grid-cols-2 gap-2">
            <button
              v-for="slot in rescheduleSlots"
              :key="slot.id"
              @click="rescheduleSlot = slot"
              :class="[
                'px-3 py-2 border rounded-lg transition text-sm',
                rescheduleSlot?.id === slot.id
                  ? 'border-blue-500 bg-blue-100'
                  : 'border-gray-300 hover:border-blue-300',
              ]"
            >
              {{ formatTime(slot.start_time) }}
            </button>
          </div>
        </div>

        <div class="flex gap-3">
          <button
            @click="closeRescheduleModal"
            class="flex-1 border border-gray-300 text-gray-700 py-2 rounded-lg hover:bg-gray-50"
          >
            Cancel
          </button>
          <button
            @click="submitReschedule"
            :disabled="!rescheduleSlot || rescheduling"
            class="flex-1 bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-300"
          >
            {{ rescheduling ? "Rescheduling..." : "Confirm" }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import PageHeader from "../../components/PageHeader.vue";
import StatusBadge from "../../components/StatusBadge.vue";
import usePagination from "../../composables/usePagination.js";
import useToast from "../../composables/useToast.js";
import { useAppointmentsStore } from "../../stores/appointments.js";
import * as appointmentApi from "../../api/appointments.js";
import * as schedulingApi from "../../api/scheduling.js";

const toast = useToast();
const appointmentsStore = useAppointmentsStore();

const loading = ref(false);
const appointments = usePagination(
  (params) => appointmentApi.getAppointments(params),
  10
);

const showRescheduleModal = ref(false);
const currentAppointment = ref(null);
const rescheduleDate = ref("");
const rescheduleSlot = ref(null);
const rescheduleSlots = ref([]);
const rescheduling = ref(false);

onMounted(async () => {
  loading.value = true;
  await appointments.fetch();
  loading.value = false;
});

function getStatusBorderColor(status) {
  const colors = {
    requested: "border-yellow-500",
    confirmed: "border-blue-500",
    checked_in: "border-purple-500",
    completed: "border-green-500",
    cancelled: "border-red-500",
    no_show: "border-gray-500",
  };
  return colors[status] || "border-gray-300";
}

function formatDateTime(dateTime) {
  if (!dateTime) return "";
  return new Date(dateTime).toLocaleString("en-US", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function formatTime(timeString) {
  if (!timeString) return "";
  return new Date(`2000-01-01T${timeString}`).toLocaleTimeString("en-US", {
    hour: "2-digit",
    minute: "2-digit",
  });
}

async function cancelAppointment(appointmentId) {
  if (!confirm("Are you sure you want to cancel this appointment?")) return;
  try {
    await appointmentApi.cancelAppointment(appointmentId);
    toast.success("Appointment cancelled");
    await appointments.fetch();
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
      doctor: currentAppointment.value.doctor.id,
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
      slot: rescheduleSlot.value.id,
    });
    toast.success("Appointment rescheduled");
    await appointments.fetch();
    closeRescheduleModal();
  } catch (err) {
    toast.error("Failed to reschedule appointment");
  } finally {
    rescheduling.value = false;
  }
}
</script>
