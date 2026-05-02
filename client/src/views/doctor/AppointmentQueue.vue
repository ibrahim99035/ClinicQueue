<template>
  <div class="space-y-6 bg-bg text-text1 font-sans">
    <div class="flex items-center justify-between gap-4">
      <div>
        <PageHeader 
          title="Appointment Queue" 
          subtitle="Today's checked-in appointments"
        />
      </div>
      <button
        @click="refreshQueue"
        class="rounded bg-accent px-4 py-2 font-mono text-[11px] uppercase tracking-mono-wide text-black transition-all duration-150 cursor-pointer hover:bg-accent-dim hover:-translate-y-px"
      >
        Refresh
      </button>
    </div>

    <div v-if="loading" class="py-8 text-center font-sans text-sm text-text2">
      Loading queue...
    </div>
    <div v-else-if="queue.length === 0" class="rounded border border-border bg-surface p-8 text-center font-sans text-sm text-text2">
      <p>No patients checked in</p>
    </div>

    <div v-else class="space-y-4">
      <div
        v-for="appointment in queue"
        :key="appointment.id"
        class="rounded border border-border bg-surface p-4"
      >
        <div class="mb-4 flex items-start justify-between gap-4">
          <div>
            <h3 class="font-sans text-lg font-semibold text-text1">
              {{ appointment.patient?.user?.name || "Patient" }}
            </h3>
            <p class="font-mono text-[11px] uppercase tracking-mono text-text2">
              Check-in: {{ formatDateTime(appointment.checked_in_at) }}
            </p>
            <p class="mt-1 font-mono text-[11px] uppercase tracking-mono text-text2">
              Waiting: {{ getWaitingDuration(appointment.checked_in_at) }} minutes
            </p>
          </div>
        </div>

        <div class="mb-4">
          <p class="font-mono text-[11px] uppercase tracking-mono text-text2">Reason</p>
          <p class="font-sans text-sm text-text1">{{ appointment.reason || "Not specified" }}</p>
        </div>

        <router-link
          :to="`/emr/appointments/${appointment.id}/consultation/create`"
          class="inline-flex items-center justify-center rounded bg-accent px-4 py-2 font-mono text-[11px] uppercase tracking-mono-wide text-black transition-all duration-150 cursor-pointer hover:bg-accent-dim hover:-translate-y-px"
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
