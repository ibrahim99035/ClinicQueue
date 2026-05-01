<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <div>
        <PageHeader 
          title="Appointment Queue" 
          subtitle="Today's checked-in appointments"
        />
      </div>
      <button
        @click="refreshQueue"
        class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
      >
        Refresh
      </button>
    </div>

    <div v-if="loading" class="text-center py-8 text-gray-500">
      Loading queue...
    </div>
    <div v-else-if="queue.length === 0" class="bg-white rounded-lg shadow-md p-8 text-center text-gray-500">
      <p>No patients checked in</p>
    </div>

    <div v-else class="space-y-4">
      <div
        v-for="appointment in queue"
        :key="appointment.id"
        class="bg-white rounded-lg shadow-md p-6 border-l-4 border-purple-500"
      >
        <div class="flex justify-between items-start mb-4">
          <div>
            <h3 class="text-lg font-semibold">
              {{ appointment.patient?.user?.name || "Patient" }}
            </h3>
            <p class="text-sm text-gray-600">
              Check-in: {{ formatDateTime(appointment.checked_in_at) }}
            </p>
            <p class="text-sm text-gray-600 mt-1">
              Waiting: {{ getWaitingDuration(appointment.checked_in_at) }} minutes
            </p>
          </div>
        </div>

        <div class="mb-4">
          <p class="text-sm text-gray-600">Reason</p>
          <p class="font-semibold">{{ appointment.reason || "Not specified" }}</p>
        </div>

        <router-link
          :to="`/emr/appointments/${appointment.id}/consultation/create`"
          class="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 inline-block"
        >
          Start Consultation
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from "vue";
import PageHeader from "../../components/PageHeader.vue";
import useToast from "../../composables/useToast.js";
import * as appointmentApi from "../../api/appointments.js";

const toast = useToast();
const loading = ref(false);
const queue = ref([]);
let refreshTimer = null;

onMounted(() => {
  refreshQueue();
  // Poll every 30 seconds
  refreshTimer = setInterval(refreshQueue, 30000);
});

onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer);
  }
});

async function refreshQueue() {
  loading.value = true;
  try {
    const response = await appointmentApi.getDoctorQueue();
    queue.value = Array.isArray(response) ? response : response.results || [];
  } catch (err) {
    toast.error("Failed to load queue");
  } finally {
    loading.value = false;
  }
}

function formatDateTime(dateTime) {
  if (!dateTime) return "";
  return new Date(dateTime).toLocaleTimeString("en-US", {
    hour: "2-digit",
    minute: "2-digit",
  });
}

function getWaitingDuration(checkedInAt) {
  if (!checkedInAt) return 0;
  const now = new Date();
  const checkedIn = new Date(checkedInAt);
  return Math.round((now - checkedIn) / 60000);
}
</script>
