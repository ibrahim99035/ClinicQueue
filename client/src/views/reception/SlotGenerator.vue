<template>
  <div class="space-y-6">
    <PageHeader
      title="Generate Appointment Slots"
      subtitle="Create available slots for doctors"
    />

    <div class="grid md:grid-cols-2 gap-6">
      <!-- Generator Form -->
      <div class="bg-white rounded-lg shadow-md p-6 space-y-4">
        <h2 class="text-lg font-semibold">Generate New Slots</h2>

        <div>
          <label class="block mb-2 font-semibold">Select Doctor</label>
          <select
            v-model="selectedDoctor"
            class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">-- Choose a doctor --</option>
            <option v-for="doctor in doctors" :key="doctor.id" :value="doctor.id">
              Dr. {{ doctor.name }} ({{ doctor.specialization }})
            </option>
          </select>
        </div>

        <div>
          <label class="block mb-2 font-semibold">Start Date</label>
          <input
            v-model="startDate"
            type="date"
            class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label class="block mb-2 font-semibold">End Date</label>
          <input
            v-model="endDate"
            type="date"
            class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <button
          @click="generateSlots"
          :disabled="!selectedDoctor || !startDate || !endDate || generating"
          class="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300"
        >
          {{ generating ? "Generating..." : "Generate Slots" }}
        </button>

        <div v-if="generationMessage" :class="[
          'p-3 rounded-lg text-sm',
          generationSuccess ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
        ]">
          {{ generationMessage }}
        </div>
      </div>

      <!-- Slot Viewer -->
      <div class="bg-white rounded-lg shadow-md p-6 space-y-4">
        <h2 class="text-lg font-semibold">View Slots</h2>

        <div>
          <label class="block mb-2 font-semibold">Select Doctor</label>
          <select
            v-model="viewDoctor"
            class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">-- Choose a doctor --</option>
            <option v-for="doctor in doctors" :key="doctor.id" :value="doctor.id">
              Dr. {{ doctor.name }}
            </option>
          </select>
        </div>

        <div>
          <label class="block mb-2 font-semibold">Select Date</label>
          <input
            v-model="viewDate"
            type="date"
            :disabled="!viewDoctor"
            class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
            @change="fetchSlots"
          />
        </div>

        <div v-if="loadingSlots" class="text-gray-500">Loading slots...</div>
        <div v-else-if="viewSlots.length === 0" class="text-gray-500">
          No slots available for this date
        </div>
        <div v-else class="space-y-2">
          <div
            v-for="slot in viewSlots"
            :key="slot.id"
            class="p-3 border rounded-lg text-sm"
          >
            <p class="font-semibold">{{ formatTime(slot.start_time) }}</p>
            <p class="text-gray-600">{{ slot.is_available ? "Available" : "Booked" }}</p>
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
