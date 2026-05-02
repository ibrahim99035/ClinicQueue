<template>
  <div class="space-y-6 bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 font-sans">
    <div class="flex items-center justify-between gap-4">
      <div>
        <PageHeader 
          title="Appointment Queue" 
          subtitle="Today's checked-in appointments"
        />
      </div>
      <button
        @click="refreshQueue"
        class="rounded bg-blue-600 px-4 py-2 font-mono text-[11px] uppercase tracking-wider text-white transition-all duration-150 cursor-pointer hover:bg-blue-700 hover:-translate-y-px"
      >
        Refresh
      </button>
    </div>

    <div v-if="loading" class="py-8 text-center font-sans text-sm text-slate-500 dark:text-slate-400">
      Loading queue...
    </div>
    <div v-else-if="queue.length === 0" class="rounded border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-8 text-center font-sans text-sm text-slate-500 dark:text-slate-400">
      <p>No patients checked in</p>
    </div>

    <div v-else class="space-y-4">
      <div
        v-for="appointment in queue"
        :key="appointment.id"
        class="rounded border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-4"
      >
        <div class="mb-4 flex items-start justify-between gap-4">
          <div>
            <h3 class="font-sans text-lg font-semibold text-slate-900 dark:text-slate-100">
              {{ appointment.patient_name || "Patient" }}
            </h3>
            <p class="font-mono text-[11px] uppercase tracking-wide text-slate-500 dark:text-slate-400">
              Check-in: {{ formatDateTime(appointment.checked_in_at) }}
            </p>
            <p class="mt-1 font-mono text-[11px] uppercase tracking-wide text-slate-500 dark:text-slate-400">
              Waiting: {{ getWaitingDuration(appointment.checked_in_at) }} minutes
            </p>
          </div>
        </div>

        <div class="mb-4">
          <p class="font-mono text-[11px] uppercase tracking-wide text-slate-500 dark:text-slate-400">Reason</p>
          <p class="font-sans text-sm text-slate-900 dark:text-slate-100">Ready for consultation</p>
        </div>

        <router-link
          :to="`/emr/appointments/${appointment.id}/consultation/create`"
          class="inline-flex items-center justify-center rounded bg-blue-600 px-4 py-2 font-mono text-[11px] uppercase tracking-wider text-white transition-all duration-150 cursor-pointer hover:bg-blue-700 hover:-translate-y-px"
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
