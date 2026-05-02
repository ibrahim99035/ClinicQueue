<template>
  <div class="space-y-6 bg-bg text-text1 font-sans">
    <PageHeader
      title="Generate Appointment Slots"
      subtitle="Create available slots for doctors"
    />

    <div class="grid gap-6 md:grid-cols-2">
      <!-- Generator Form -->
      <div class="space-y-4 rounded border border-border bg-surface p-4">
        <h2 class="font-sans text-xl font-bold leading-tight text-text1">Generate New Slots</h2>

        <div>
          <label class="mb-1.5 block font-mono text-[11px] uppercase tracking-mono text-text2">Select Doctor</label>
          <select
            v-model="selectedDoctor"
            class="w-full rounded border border-border bg-surface px-3 py-2 font-mono text-sm text-text1 outline-none transition-all duration-150 focus:border-accent focus:ring-2 focus:ring-accent/10"
          >
            <option value="">-- Choose a doctor --</option>
            <option v-for="doctor in doctors" :key="doctor.id" :value="doctor.id">
              Dr. {{ doctor.name }} ({{ doctor.specialization }})
            </option>
          </select>
        </div>

        <div>
          <label class="mb-1.5 block font-mono text-[11px] uppercase tracking-mono text-text2">Start Date</label>
          <input
            v-model="startDate"
            type="date"
            class="w-full rounded border border-border bg-surface px-3 py-2 font-mono text-sm text-text1 outline-none transition-all duration-150 focus:border-accent focus:ring-2 focus:ring-accent/10"
          />
        </div>

        <div>
          <label class="mb-1.5 block font-mono text-[11px] uppercase tracking-mono text-text2">End Date</label>
          <input
            v-model="endDate"
            type="date"
            class="w-full rounded border border-border bg-surface px-3 py-2 font-mono text-sm text-text1 outline-none transition-all duration-150 focus:border-accent focus:ring-2 focus:ring-accent/10"
          />
        </div>

        <button
          @click="generateSlots"
          :disabled="!selectedDoctor || !startDate || !endDate || generating"
          class="w-full rounded bg-accent px-4 py-2 font-mono text-[11px] uppercase tracking-mono-wide text-black transition-all duration-150 cursor-pointer hover:bg-accent-dim hover:-translate-y-px disabled:cursor-not-allowed disabled:opacity-60"
        >
          {{ generating ? "Generating..." : "Generate Slots" }}
        </button>

        <div v-if="generationMessage" :class="[
          'rounded border px-4 py-3 font-sans text-sm',
          generationSuccess ? 'border-accent/40 bg-surface text-accent' : 'border-danger/40 bg-surface text-danger'
        ]">
          {{ generationMessage }}
        </div>
      </div>

      <!-- Slot Viewer -->
      <div class="space-y-4 rounded border border-border bg-surface p-4">
        <h2 class="font-sans text-xl font-bold leading-tight text-text1">View Slots</h2>

        <div>
          <label class="mb-1.5 block font-mono text-[11px] uppercase tracking-mono text-text2">Select Doctor</label>
          <select
            v-model="viewDoctor"
            class="w-full rounded border border-border bg-surface px-3 py-2 font-mono text-sm text-text1 outline-none transition-all duration-150 focus:border-accent focus:ring-2 focus:ring-accent/10"
          >
            <option value="">-- Choose a doctor --</option>
            <option v-for="doctor in doctors" :key="doctor.id" :value="doctor.id">
              Dr. {{ doctor.name }}
            </option>
          </select>
        </div>

        <div>
          <label class="mb-1.5 block font-mono text-[11px] uppercase tracking-mono text-text2">Select Date</label>
          <input
            v-model="viewDate"
            type="date"
            :disabled="!viewDoctor"
            class="w-full rounded border border-border bg-surface px-3 py-2 font-mono text-sm text-text1 outline-none transition-all duration-150 focus:border-accent focus:ring-2 focus:ring-accent/10 disabled:cursor-not-allowed disabled:opacity-50"
            @change="fetchSlots"
          />
        </div>

        <div v-if="loadingSlots" class="font-sans text-sm text-text2">Loading slots...</div>
        <div v-else-if="viewSlots.length === 0" class="font-sans text-sm text-text2">
          No slots available for this date
        </div>
        <div v-else class="space-y-2">
          <div
            v-for="slot in viewSlots"
            :key="slot.id"
            class="rounded border border-border bg-surface2 p-3 text-sm"
          >
            <p class="font-mono text-sm text-text1">{{ formatTime(slot.start_time) }}</p>
            <p class="font-mono text-[11px] uppercase tracking-mono" :class="slot.is_available ? 'text-accent' : 'text-danger'">{{ slot.is_available ? "Available" : "Booked" }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import PageHeader from "../../components/PageHeader.vue";
import useToast from "../../composables/useToast.js";
import * as appointmentApi from "../../api/appointments.js";
import * as schedulingApi from "../../api/scheduling.js";

const toast = useToast();
const doctors = ref([]);
const selectedDoctor = ref("");
const startDate = ref("");
const endDate = ref("");
const generating = ref(false);
const generationMessage = ref("");
const generationSuccess = ref(false);

const viewDoctor = ref("");
const viewDate = ref("");
const viewSlots = ref([]);
const loadingSlots = ref(false);

onMounted(async () => {
  try {
    doctors.value = await appointmentApi.getDoctorsList();
  } catch (err) {
    toast.error("Failed to load doctors");
  }
});

async function generateSlots() {
  generating.value = true;
  generationMessage.value = "";
  try {
    const response = await schedulingApi.generateSlots({
      doctor: selectedDoctor.value,
      start_date: startDate.value,
      end_date: endDate.value,
    });
    generationSuccess.value = true;
    generationMessage.value = `${response.count || 0} slots generated successfully`;
    selectedDoctor.value = "";
    startDate.value = "";
    endDate.value = "";
    toast.success("Slots generated!");
  } catch (err) {
    generationSuccess.value = false;
    generationMessage.value = err.response?.data?.detail || "Failed to generate slots";
    toast.error(generationMessage.value);
  } finally {
    generating.value = false;
  }
}

async function fetchSlots() {
  if (!viewDoctor.value || !viewDate.value) return;
  loadingSlots.value = true;
  try {
    viewSlots.value = await schedulingApi.getAvailableSlots({
      doctor: viewDoctor.value,
      date: viewDate.value,
    });
  } catch (err) {
    toast.error("Failed to load slots");
  } finally {
    loadingSlots.value = false;
  }
}

function formatTime(timeString) {
  if (!timeString) return "";
  return new Date(`2000-01-01T${timeString}`).toLocaleTimeString("en-US", {
    hour: "2-digit",
    minute: "2-digit",
  });
}
</script>
