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
          <p class="font-mono text-[11px] uppercase tracking-wide text-slate-500 dark:text-slate-400">
            Reason
          </p>

          <p class="font-sans text-sm text-slate-900 dark:text-slate-100">
            {{ appointment.reason || "Ready for consultation" }}
          </p>
        </div>

        <div class="flex flex-wrap gap-3">
          <router-link
            v-if="!hasConsultation(appointment)"
            :to="`/emr/appointments/${appointment.id}/consultation/create`"
            class="inline-flex items-center justify-center rounded bg-blue-600 px-4 py-2 font-mono text-[11px] uppercase tracking-wider text-white transition-all duration-150 cursor-pointer hover:bg-blue-700 hover:-translate-y-px"
          >
            Start Consultation
          </router-link>

          <router-link
            v-if="hasConsultation(appointment) && getConsultationId(appointment)"
            :to="`/emr/consultations/${getConsultationId(appointment)}/edit`"
            class="inline-flex items-center justify-center rounded border border-slate-300 bg-white px-4 py-2 font-mono text-[11px] uppercase tracking-wider text-slate-700 transition-all duration-150 cursor-pointer hover:bg-slate-100 hover:-translate-y-px dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100 dark:hover:bg-slate-800"
          >
            Edit Consultation
          </router-link>

          <button
            v-if="canCompleteAppointment(appointment)"
            type="button"
            @click="handleCompleteAppointment(appointment)"
            class="inline-flex items-center justify-center rounded bg-green-600 px-4 py-2 font-mono text-[11px] uppercase tracking-wider text-white transition-all duration-150 cursor-pointer hover:bg-green-700 hover:-translate-y-px"
          >
            Complete Appointment
          </button>
        </div>
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
    showError("Failed to load queue");
  } finally {
    loading.value = false;
  }
}

function hasConsultation(appointment) {
  return Boolean(
    appointment.has_consultation ||
    appointment.hasConsultation ||
    appointment.consultation_id ||
    appointment.consultationId
  );
}

function getConsultationId(appointment) {
  return appointment.consultation_id || appointment.consultationId || null;
}

function canCompleteAppointment(appointment) {
  const status = appointment.status || "CHECKED_IN";

  return status === "CHECKED_IN" && hasConsultation(appointment);
}

async function handleCompleteAppointment(appointment) {
  try {
    await appointmentApi.completeAppointment(appointment.id);
    showSuccess("Appointment completed successfully.");
    await refreshQueue();
  } catch (err) {
    const message =
      err.response?.data?.detail ||
      err.response?.data?.non_field_errors?.[0] ||
      "Failed to complete appointment.";

    showError(message);
  }
}

function showSuccess(message) {
  if (typeof toast.success === "function") {
    toast.success(message);
    return;
  }

  if (typeof toast.showToast === "function") {
    toast.showToast(message, "success");
  }
}

function showError(message) {
  if (typeof toast.error === "function") {
    toast.error(message);
    return;
  }

  if (typeof toast.showToast === "function") {
    toast.showToast(message, "error");
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