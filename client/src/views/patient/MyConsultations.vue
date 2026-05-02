<template>
  <div class="space-y-6 bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 font-sans">
    <PageHeader
      title="My Consultations"
      subtitle="View your completed consultations"
    />

    <div v-if="loading" class="py-8 text-center font-sans text-sm text-slate-500 dark:text-slate-400">
      Loading consultations...
    </div>
    <div
      v-else-if="consultations.length === 0"
      class="rounded border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-8 text-center font-sans text-sm text-slate-500 dark:text-slate-400"
    >
      <p>No completed consultations yet</p>
    </div>

    <div v-else class="space-y-4">
      <div
        v-for="appointment in consultations"
        :key="appointment.id"
        class="rounded border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-4"
      >
        <div class="mb-4 flex items-start justify-between gap-4">
          <div>
            <h3 class="font-sans text-lg font-semibold text-slate-900 dark:text-slate-100">
              Dr. {{ appointment.doctorName }}
            </h3>
            <p class="font-mono text-[11px] uppercase tracking-wide text-slate-500 dark:text-slate-400">
              Consultation on {{ formatDateTime(appointment.completed_at || appointment.appointmentDateTime) }}
            </p>
          </div>
          <button
            v-if="appointment.status === 'COMPLETED' || appointment.status === 'completed'"
            @click="toggleConsultation(appointment)"
            class="font-mono text-[11px] uppercase tracking-wide text-blue-600 dark:text-blue-400 transition-all duration-150 cursor-pointer hover:text-blue-700 dark:hover:text-blue-300"
          >
            {{ selectedId === appointment.id ? "Collapse" : "View Details" }}
          </button>
          <span
            v-else
            class="font-sans text-sm text-slate-500 dark:text-slate-400"
          >
            Consultation not available yet
          </span>
        </div>

        <div v-if="selectedId === appointment.id" class="space-y-4 border-t border-slate-200 dark:border-slate-800 pt-4">
          <div v-if="loadingDetailsId === appointment.id" class="font-sans text-sm text-slate-500 dark:text-slate-400">
            Loading consultation details...
          </div>

          <div v-else-if="consultationDetailsByAppointment[appointment.id]" class="space-y-4">
          <!-- Diagnosis -->
          <div>
            <h4 class="mb-2 font-sans text-base font-semibold text-slate-900 dark:text-slate-100">Diagnosis</h4>
            <p class="whitespace-pre-wrap font-sans text-sm text-slate-500 dark:text-slate-400">
              {{ consultationDetailsByAppointment[appointment.id].diagnosis || "Not recorded" }}
            </p>
          </div>

          <!-- Notes -->
          <div>
            <h4 class="mb-2 font-sans text-base font-semibold text-slate-900 dark:text-slate-100">Doctor's Notes</h4>
            <p class="whitespace-pre-wrap font-sans text-sm text-slate-500 dark:text-slate-400">
              {{ consultationDetailsByAppointment[appointment.id].notes || "No notes" }}
            </p>
          </div>

          <!-- Prescriptions -->
          <div v-if="consultationDetailsByAppointment[appointment.id].prescription_items?.length > 0">
            <h4 class="mb-2 font-sans text-base font-semibold text-slate-900 dark:text-slate-100">Prescriptions</h4>
            <table class="w-full border-collapse text-sm">
              <thead>
                <tr class="bg-slate-50 dark:bg-slate-800">
                  <th class="px-4 py-3 text-left font-mono text-[11px] uppercase tracking-wide text-slate-500 dark:text-slate-400">Drug Name</th>
                  <th class="px-4 py-3 text-left font-mono text-[11px] uppercase tracking-wide text-slate-500 dark:text-slate-400">Dose</th>
                  <th class="px-4 py-3 text-left font-mono text-[11px] uppercase tracking-wide text-slate-500 dark:text-slate-400">Duration</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="item in consultationDetailsByAppointment[appointment.id].prescription_items"
                  :key="item.id"
                  class="border-t border-slate-200 dark:border-slate-800 transition-colors duration-150 hover:bg-slate-50 dark:hover:bg-slate-800"
                >
                  <td class="px-4 py-3 font-sans text-sm text-slate-900 dark:text-slate-100">{{ item.drug_name }}</td>
                  <td class="px-4 py-3 font-sans text-sm text-slate-900 dark:text-slate-100">{{ item.dose }}</td>
                  <td class="px-4 py-3 font-sans text-sm text-slate-900 dark:text-slate-100">{{ item.duration }}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Tests -->
          <div v-if="consultationDetailsByAppointment[appointment.id].requested_tests?.length > 0">
            <h4 class="mb-2 font-sans text-base font-semibold text-slate-900 dark:text-slate-100">Requested Tests</h4>
            <table class="w-full border-collapse text-sm">
              <thead>
                <tr class="bg-slate-50 dark:bg-slate-800">
                  <th class="px-4 py-3 text-left font-mono text-[11px] uppercase tracking-wide text-slate-500 dark:text-slate-400">Test Name</th>
                  <th class="px-4 py-3 text-left font-mono text-[11px] uppercase tracking-wide text-slate-500 dark:text-slate-400">Notes</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="test in consultationDetailsByAppointment[appointment.id].requested_tests"
                  :key="test.id"
                  class="border-t border-slate-200 dark:border-slate-800 transition-colors duration-150 hover:bg-slate-50 dark:hover:bg-slate-800"
                >
                  <td class="px-4 py-3 font-sans text-sm text-slate-900 dark:text-slate-100">{{ test.test_name }}</td>
                  <td class="px-4 py-3 font-sans text-sm text-slate-900 dark:text-slate-100">{{ test.notes || "—" }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          </div>
          <div
            v-else-if="consultationDetailsByAppointment[appointment.id] === null"
            class="rounded border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800 px-4 py-3 font-sans text-sm text-slate-500 dark:text-slate-400"
          >
            No consultation summary is available for this appointment yet.
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
import * as emrApi from "../../api/emr.js";

const toast = useToast();
const loading = ref(false);
const consultations = ref([]);
const selectedId = ref(null);
const loadingDetailsId = ref(null);
const consultationDetailsByAppointment = ref({});

onMounted(async () => {
  loading.value = true;
  try {
    const response = await appointmentApi.getMyAppointments({ status: "COMPLETED" });
    const rawAppointments = Array.isArray(response)
      ? response
      : response.results || [];

    consultations.value = rawAppointments.map(normalizeAppointment);
  } catch (err) {
    toast.error("Failed to load consultations");
  } finally {
    loading.value = false;
  }
});

function normalizeAppointment(appointment) {
  return {
    ...appointment,
    doctorName: appointment.doctor_name || "Unknown",
    appointmentDateTime: appointment.slot_time || "",
    status: appointment.status || "UNKNOWN",
  };
}

async function toggleConsultation(appointment) {
  const appointmentId = appointment.id;

  if (selectedId.value === appointmentId) {
    selectedId.value = null;
    return;
  }

  selectedId.value = appointmentId;

  if (consultationDetailsByAppointment.value[appointmentId] !== undefined) {
    return;
  }

  loadingDetailsId.value = appointmentId;
  try {
    consultationDetailsByAppointment.value = {
      ...consultationDetailsByAppointment.value,
      [appointmentId]: await emrApi.getConsultationByAppointment(appointmentId),
    };
  } catch (err) {
    if (err.response?.status === 404) {
      consultationDetailsByAppointment.value = {
        ...consultationDetailsByAppointment.value,
        [appointmentId]: null,
      };
      return;
    }

    console.error("Failed to load consultation:", err);
    toast.error("Failed to load consultation details");
    selectedId.value = null;
  } finally {
    loadingDetailsId.value = null;
  }
}

function formatDateTime(dateTime) {
  if (!dateTime) return "";
  return new Date(dateTime).toLocaleString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}
</script>
