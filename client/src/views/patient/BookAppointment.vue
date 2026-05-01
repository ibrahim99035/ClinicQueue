<template>
  <div class="space-y-6">
    <PageHeader
      title="Book Appointment"
      subtitle="Follow the steps to book your appointment"
    />

    <!-- Step indicator -->
    <div class="flex justify-between mb-8">
      <div
        v-for="(stepName, idx) in ['Choose Doctor', 'Pick Date & Slot', 'Confirm']"
        :key="idx"
        :class="[
          'flex-1 text-center py-2 border-b-2',
          step > idx
            ? 'border-green-500 text-green-700'
            : step === idx
            ? 'border-blue-500 text-blue-700 font-semibold'
            : 'border-gray-300 text-gray-500',
        ]"
      >
        {{ stepName }}
      </div>
    </div>

    <!-- Step 1: Choose Doctor -->
    <div v-if="step === 0" class="bg-white rounded-lg shadow-md p-6 space-y-4">
      <h2 class="text-lg font-semibold">Select a Doctor</h2>

      <input
        v-model="searchTerm"
        type="text"
        placeholder="Search by name or specialization..."
        class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
      />

      <div v-if="loadingDoctors" class="text-gray-500">Loading doctors...</div>
      <div v-else-if="filteredDoctors.length === 0" class="text-gray-500">
        No doctors found
      </div>
      <div v-else class="grid gap-4">
        <div
          v-for="doctor in filteredDoctors"
          :key="doctor.id"
          @click="selectedDoctor = doctor"
          :class="[
            'p-4 border rounded-lg cursor-pointer transition',
            selectedDoctor?.id === doctor.id
              ? 'border-blue-500 bg-blue-50'
              : 'border-gray-300 hover:border-blue-300',
          ]"
        >
          <p class="font-semibold">Dr. {{ doctor.name }}</p>
          <p class="text-sm text-gray-600">{{ doctor.specialization }}</p>
          <p class="text-xs text-gray-500">Duration: {{ doctor.consultation_duration }} min</p>
        </div>
      </div>

      <button
        @click="step = 1"
        :disabled="!selectedDoctor"
        class="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-300"
      >
        Next
      </button>
    </div>

    <!-- Step 2: Pick Date & Slot -->
    <div v-else-if="step === 1" class="bg-white rounded-lg shadow-md p-6 space-y-4">
      <h2 class="text-lg font-semibold">
        Select Date & Time for Dr. {{ selectedDoctor?.name }}
      </h2>

      <div class="grid md:grid-cols-2 gap-6">
        <!-- Date picker -->
        <div>
          <label class="block mb-2 font-semibold">Date</label>
          <input
            v-model="selectedDate"
            type="date"
            :min="new Date().toISOString().split('T')[0]"
            class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            @change="fetchSlots"
          />
        </div>

        <!-- Slots -->
        <div>
          <label class="block mb-2 font-semibold">Time Slot</label>
          <div v-if="loadingSlots" class="text-gray-500">Loading slots...</div>
          <div v-else-if="availableSlots.length === 0" class="text-gray-500">
            <p>No slots available for this date</p>
            <button
              @click="joinWaitingList = true"
              class="text-blue-600 hover:underline mt-2"
            >
              Join Waiting List
            </button>
          </div>
          <div v-else class="grid grid-cols-2 gap-2">
            <button
              v-for="slot in availableSlots"
              :key="slot.id"
              @click="selectedSlot = slot"
              :class="[
                'px-3 py-2 border rounded-lg transition',
                selectedSlot?.id === slot.id
                  ? 'border-blue-500 bg-blue-100 text-blue-700 font-semibold'
                  : 'border-gray-300 hover:border-blue-300',
              ]"
            >
              {{ formatTime(slot.start_datetime) }}
            </button>
          </div>
        </div>
      </div>

      <div class="flex gap-3">
        <button
          @click="step = 0"
          class="flex-1 border border-gray-300 text-gray-700 py-2 rounded-lg hover:bg-gray-50"
        >
          Back
        </button>
        <button
          @click="step = 2"
          :disabled="!selectedSlot"
          class="flex-1 bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-300"
        >
          Next
        </button>
      </div>
    </div>

    <!-- Step 3: Confirm -->
    <div v-else-if="step === 2" class="bg-white rounded-lg shadow-md p-6 space-y-4">
      <h2 class="text-lg font-semibold">Confirm Your Appointment</h2>

      <div class="space-y-3 border-b pb-4">
        <div class="flex justify-between">
          <span class="text-gray-600">Doctor</span>
          <span class="font-semibold">Dr. {{ selectedDoctor?.name }}</span>
        </div>
        <div class="flex justify-between">
          <span class="text-gray-600">Specialization</span>
          <span class="font-semibold">{{ selectedDoctor?.specialization }}</span>
        </div>
        <div class="flex justify-between">
          <span class="text-gray-600">Date & Time</span>
          <span class="font-semibold">{{ formatBookingDateTime() }}</span>
        </div>
      </div>

      <div>
        <label class="block mb-2 font-semibold">Reason for Appointment</label>
        <textarea
          v-model="appointmentReason"
          placeholder="Describe your symptoms or reason..."
          rows="4"
          class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <div v-if="submitError" class="bg-red-100 text-red-700 p-3 rounded-lg">
        {{ submitError }}
      </div>

      <div class="flex gap-3">
        <button
          @click="step = 1"
          class="flex-1 border border-gray-300 text-gray-700 py-2 rounded-lg hover:bg-gray-50"
        >
          Back
        </button>
        <button
          @click="bookAppointment"
          :disabled="submitting"
          class="flex-1 bg-green-600 text-white py-2 rounded-lg hover:bg-green-700 disabled:bg-gray-300"
        >
          {{ submitting ? "Booking..." : "Confirm Booking" }}
        </button>
      </div>
    </div>

    <!-- Waiting List Modal -->
    <div
      v-if="joinWaitingList"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    >
      <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4 space-y-4">
        <h3 class="text-lg font-semibold">Join Waiting List</h3>
        <p class="text-gray-600">
          You'll be notified when a slot becomes available for this doctor on
          this date.
        </p>
        <div class="flex gap-3">
          <button
            @click="joinWaitingList = false"
            class="flex-1 border border-gray-300 text-gray-700 py-2 rounded-lg hover:bg-gray-50"
          >
            Cancel
          </button>
          <button
            @click="submitWaitingList"
            :disabled="waitingListSubmitting"
            class="flex-1 bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-300"
          >
            {{ waitingListSubmitting ? "Adding..." : "Add to List" }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import PageHeader from "../../components/PageHeader.vue";
import useToast from "../../composables/useToast.js";
import { useAppointmentsStore } from "../../stores/appointments.js";
import * as schedulingApi from "../../api/scheduling.js";
import * as appointmentApi from "../../api/appointments.js";

const router = useRouter();
const toast = useToast();
const appointmentsStore = useAppointmentsStore();

const step = ref(0);
const searchTerm = ref("");
const doctors = ref([]);
const selectedDoctor = ref(null);
const selectedDate = ref("");
const selectedSlot = ref(null);
const appointmentReason = ref("");
const availableSlots = ref([]);
const loadingDoctors = ref(false);
const loadingSlots = ref(false);
const submitting = ref(false);
const submitError = ref("");
const joinWaitingList = ref(false);
const waitingListSubmitting = ref(false);

const filteredDoctors = computed(() => {
  if (!searchTerm.value) return doctors.value;
  const term = searchTerm.value.toLowerCase();
  return doctors.value.filter(
    (d) =>
      d.name.toLowerCase().includes(term) ||
      (d.specialization || "").toLowerCase().includes(term)
  );
});

onMounted(async () => {
  loadingDoctors.value = true;
  try {
    const rawDoctors = await appointmentApi.getDoctorsList();
    doctors.value = rawDoctors.map(normalizeDoctor);
  } catch (err) {
    toast.error("Failed to load doctors");
  } finally {
    loadingDoctors.value = false;
  }
});

function normalizeDoctor(doctor) {
  const user = doctor.user || {};
  const name =
    [user.first_name, user.last_name].filter(Boolean).join(" ") ||
    user.email ||
    "Unknown";

  return {
    ...doctor,
    name,
    specialization: doctor.specialization || "",
    consultation_duration: doctor.consultationDuration || doctor.consultation_duration || 15,
  };
}

async function fetchSlots() {
  if (!selectedDoctor.value || !selectedDate.value) return;
  loadingSlots.value = true;
  try {
    availableSlots.value = await schedulingApi.getAvailableSlots({
      doctor: selectedDoctor.value.id,
      date: selectedDate.value,
    });
    selectedSlot.value = null;
  } catch (err) {
    toast.error("Failed to load available slots");
  } finally {
    loadingSlots.value = false;
  }
}

function formatTime(timeString) {
  if (!timeString) return "";
  return new Date(timeString).toLocaleTimeString("en-US", {
    hour: "2-digit",
    minute: "2-digit",
  });
}

function formatBookingDateTime() {
  if (!selectedSlot.value || !selectedDate.value) return "";
  const date = new Date(selectedDate.value);
  const time = formatTime(selectedSlot.value.start_datetime);
  return `${date.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  })} at ${time}`;
}

async function bookAppointment() {
  submitError.value = "";
  submitting.value = true;
  try {
    await appointmentApi.createAppointment({
      doctor_id: selectedDoctor.value.id,
      slot_id: selectedSlot.value.id,
      reason: appointmentReason.value,
    });
    toast.success("Appointment booked successfully!");
    await appointmentsStore.fetchAppointments();
    router.push("/patient/appointments");
  } catch (err) {
    submitError.value = err.response?.data?.detail || "Failed to book appointment";
    toast.error(submitError.value);
  } finally {
    submitting.value = false;
  }
}

async function submitWaitingList() {
  waitingListSubmitting.value = true;
  try {
    await appointmentApi.joinWaitingList({
      doctor_id: selectedDoctor.value.id,
      preferred_date: selectedDate.value,
    });
    toast.success("Added to waiting list!");
    joinWaitingList.value = false;
    router.push("/patient/waiting-list");
  } catch (err) {
    toast.error("Failed to join waiting list");
  } finally {
    waitingListSubmitting.value = false;
  }
}
</script>
