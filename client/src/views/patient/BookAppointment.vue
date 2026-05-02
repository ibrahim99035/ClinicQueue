<template>
  <div class="space-y-6 bg-bg text-text1 font-sans">
    <PageHeader
      title="Book Appointment"
      subtitle="Follow the steps to book your appointment"
    />

    <!-- Step indicator -->
    <div class="mb-8 flex justify-between gap-2 rounded border border-border bg-surface2 p-2">
      <div
        v-for="(stepName, idx) in ['Choose Doctor', 'Pick Date & Slot', 'Confirm']"
        :key="idx"
        :class="[
          'flex-1 text-center rounded px-2 py-2 font-mono text-[11px] uppercase tracking-mono transition-all duration-150',
          step > idx
            ? 'text-accent border border-accent/40 bg-surface'
            : step === idx
            ? 'text-text1 border border-border bg-surface'
            : 'text-text3 border border-border/40',
        ]"
      >
        {{ stepName }}
      </div>
    </div>

    <!-- Step 1: Choose Doctor -->
    <div v-if="step === 0" class="space-y-4 rounded border border-border bg-surface p-4">
      <h2 class="font-sans text-xl font-bold leading-tight text-text1">Select a Doctor</h2>

      <input
        v-model="searchTerm"
        type="text"
        placeholder="Search by name or specialization..."
        class="w-full rounded border border-border bg-surface px-3 py-2 font-mono text-sm text-text1 placeholder:text-text3 outline-none transition-all duration-150 focus:border-accent focus:ring-2 focus:ring-accent/10"
      />

      <div v-if="loadingDoctors" class="font-sans text-sm text-text2">Loading doctors...</div>
      <div v-else-if="filteredDoctors.length === 0" class="font-sans text-sm text-text2">
        No doctors found
      </div>
      <div v-else class="grid gap-4">
        <div
          v-for="doctor in filteredDoctors"
          :key="doctor.id"
          @click="selectedDoctor = doctor"
          :class="[
            'rounded border p-4 transition-all duration-150 cursor-pointer',
            selectedDoctor?.id === doctor.id
              ? 'border-accent/40 bg-surface2'
              : 'border-border hover:border-accent/30',
          ]"
        >
          <p class="font-sans text-sm font-semibold text-text1">Dr. {{ doctor.name }}</p>
          <p class="font-sans text-sm text-text2">{{ doctor.specialization }}</p>
          <p class="font-mono text-[11px] uppercase tracking-mono text-text3">Duration: {{ doctor.consultation_duration }} min</p>
        </div>
      </div>

      <button
        @click="step = 1"
        :disabled="!selectedDoctor"
        class="w-full rounded bg-accent px-4 py-2 font-mono text-[11px] uppercase tracking-mono-wide text-black transition-all duration-150 cursor-pointer hover:bg-accent-dim hover:-translate-y-px disabled:cursor-not-allowed disabled:opacity-60"
      >
        Next
      </button>
    </div>

    <!-- Step 2: Pick Date & Slot -->
    <div v-else-if="step === 1" class="space-y-4 rounded border border-border bg-surface p-4">
      <h2 class="font-sans text-xl font-bold leading-tight text-text1">
        Select Date & Time for Dr. {{ selectedDoctor?.name }}
      </h2>

      <div class="grid gap-6 md:grid-cols-2">
        <!-- Date picker -->
        <div>
          <label class="mb-1.5 block font-mono text-[11px] uppercase tracking-mono text-text2">Date</label>
          <input
            v-model="selectedDate"
            type="date"
            :min="new Date().toISOString().split('T')[0]"
            class="w-full rounded border border-border bg-surface px-3 py-2 font-mono text-sm text-text1 outline-none transition-all duration-150 focus:border-accent focus:ring-2 focus:ring-accent/10"
            @change="fetchSlots"
          />
        </div>

        <!-- Slots -->
        <div>
          <label class="mb-1.5 block font-mono text-[11px] uppercase tracking-mono text-text2">Time Slot</label>
          <div v-if="loadingSlots" class="font-sans text-sm text-text2">Loading slots...</div>
          <div v-else-if="availableSlots.length === 0" class="font-sans text-sm text-text2">
            <p>No slots available for this date</p>
            <button
              @click="joinWaitingList = true"
              class="mt-2 font-mono text-[11px] uppercase tracking-mono text-accent transition-all duration-150 cursor-pointer hover:text-accent-dim"
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
                'rounded border px-3 py-2 transition-all duration-150 cursor-pointer font-mono text-sm',
                selectedSlot?.id === slot.id
                  ? 'border-accent/40 bg-surface2 text-accent'
                  : 'border-border text-text1 hover:border-accent/30',
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
          class="flex-1 rounded border border-border px-4 py-2 font-mono text-[11px] uppercase tracking-mono text-text2 transition-all duration-150 cursor-pointer hover:border-accent hover:text-text1"
        >
          Back
        </button>
        <button
          @click="step = 2"
          :disabled="!selectedSlot"
          class="flex-1 rounded bg-accent px-4 py-2 font-mono text-[11px] uppercase tracking-mono-wide text-black transition-all duration-150 cursor-pointer hover:bg-accent-dim hover:-translate-y-px disabled:cursor-not-allowed disabled:opacity-60"
        >
          Next
        </button>
      </div>
    </div>

    <!-- Step 3: Confirm -->
    <div v-else-if="step === 2" class="space-y-4 rounded border border-border bg-surface p-4">
      <h2 class="font-sans text-xl font-bold leading-tight text-text1">Confirm Your Appointment</h2>

      <div class="space-y-3 border-b border-border pb-4">
        <div class="flex justify-between">
          <span class="font-mono text-[11px] uppercase tracking-mono text-text2">Doctor</span>
          <span class="font-sans text-sm font-semibold text-text1">Dr. {{ selectedDoctor?.name }}</span>
        </div>
        <div class="flex justify-between">
          <span class="font-mono text-[11px] uppercase tracking-mono text-text2">Specialization</span>
          <span class="font-sans text-sm font-semibold text-text1">{{ selectedDoctor?.specialization }}</span>
        </div>
        <div class="flex justify-between">
          <span class="font-mono text-[11px] uppercase tracking-mono text-text2">Date & Time</span>
          <span class="font-sans text-sm font-semibold text-text1">{{ formatBookingDateTime() }}</span>
        </div>
      </div>

      <div>
        <label class="mb-1.5 block font-mono text-[11px] uppercase tracking-mono text-text2">Reason for Appointment</label>
        <textarea
          v-model="appointmentReason"
          placeholder="Describe your symptoms or reason..."
          rows="4"
          class="w-full rounded border border-border bg-surface px-3 py-2 font-mono text-sm text-text1 placeholder:text-text3 outline-none transition-all duration-150 focus:border-accent focus:ring-2 focus:ring-accent/10"
        />
      </div>

      <div v-if="submitError" class="rounded border border-danger/40 bg-surface px-4 py-3 font-sans text-sm text-danger">
        {{ submitError }}
      </div>

      <div class="flex gap-3">
        <button
          @click="step = 1"
          class="flex-1 rounded border border-border px-4 py-2 font-mono text-[11px] uppercase tracking-mono text-text2 transition-all duration-150 cursor-pointer hover:border-accent hover:text-text1"
        >
          Back
        </button>
        <button
          @click="bookAppointment"
          :disabled="submitting"
          class="flex-1 rounded bg-accent px-4 py-2 font-mono text-[11px] uppercase tracking-mono-wide text-black transition-all duration-150 cursor-pointer hover:bg-accent-dim hover:-translate-y-px disabled:cursor-not-allowed disabled:opacity-60"
        >
          {{ submitting ? "Booking..." : "Confirm Booking" }}
        </button>
      </div>
    </div>

    <!-- Waiting List Modal -->
    <div
      v-if="joinWaitingList"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/70"
    >
      <div class="mx-4 w-full max-w-md space-y-4 rounded border border-border bg-surface p-6">
        <h3 class="font-sans text-xl font-bold leading-tight text-text1">Join Waiting List</h3>
        <p class="font-sans text-sm text-text2">
          You'll be notified when a slot becomes available for this doctor on
          this date.
        </p>
        <div class="flex gap-3">
          <button
            @click="joinWaitingList = false"
            class="flex-1 rounded border border-border px-4 py-2 font-mono text-[11px] uppercase tracking-mono text-text2 transition-all duration-150 cursor-pointer hover:border-accent hover:text-text1"
          >
            Cancel
          </button>
          <button
            @click="submitWaitingList"
            :disabled="waitingListSubmitting"
            class="flex-1 rounded bg-accent px-4 py-2 font-mono text-[11px] uppercase tracking-mono-wide text-black transition-all duration-150 cursor-pointer hover:bg-accent-dim hover:-translate-y-px disabled:cursor-not-allowed disabled:opacity-60"
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
