<template>
  <div class="space-y-6 bg-bg text-text1 font-sans">
    <PageHeader
      title="My Consultations"
      subtitle="View your completed consultations"
    />

    <div v-if="loading" class="py-8 text-center font-sans text-sm text-text2">
      Loading consultations...
    </div>
    <div
      v-else-if="consultations.length === 0"
      class="rounded border border-border bg-surface p-8 text-center font-sans text-sm text-text2"
    >
      <p>No completed consultations yet</p>
    </div>

    <div v-else class="space-y-4">
      <div
        v-for="appointment in consultations"
        :key="appointment.id"
        class="rounded border border-border bg-surface p-4"
      >
        <div class="mb-4 flex items-start justify-between gap-4">
          <div>
            <h3 class="font-sans text-lg font-semibold text-text1">
              Dr. {{ appointment.doctorName }}
            </h3>
            <p class="font-mono text-[11px] uppercase tracking-mono text-text2">
              Consultation on {{ formatDateTime(appointment.completed_at || appointment.appointmentDateTime) }}
            </p>
          </div>
          <button
            v-if="canViewConsultation(appointment)"
            @click="toggleConsultation(appointment)"
            class="font-mono text-[11px] uppercase tracking-mono text-accent transition-all duration-150 cursor-pointer hover:text-accent-dim"
          >
            {{ selectedId === appointment.id ? "Collapse" : "View Details" }}
          </button>
          <span
            v-else
            class="font-sans text-sm text-text2"
          >
            Consultation summary will be available after completion.
          </span>
        </div>

        <div v-if="selectedId === appointment.id" class="space-y-4 border-t border-border pt-4">
          <div v-if="loadingDetailsId === appointment.id" class="font-sans text-sm text-text2">
            Loading consultation details...
          </div>

          <div v-else-if="consultationDetailsByAppointment[appointment.id]" class="space-y-4">
          <!-- Diagnosis -->
          <div>
            <h4 class="mb-2 font-sans text-base font-semibold text-text1">Diagnosis</h4>
            <p class="whitespace-pre-wrap font-sans text-sm text-text2">
              {{ consultationDetailsByAppointment[appointment.id].diagnosis || "Not recorded" }}
            </p>
          </div>

          <!-- Notes -->
          <div>
            <h4 class="mb-2 font-sans text-base font-semibold text-text1">Doctor's Notes</h4>
            <p class="whitespace-pre-wrap font-sans text-sm text-text2">
              {{ consultationDetailsByAppointment[appointment.id].notes || "No notes" }}
            </p>
          </div>

          <!-- Prescriptions -->
          <div v-if="consultationDetailsByAppointment[appointment.id].prescription_items?.length > 0">
            <h4 class="mb-2 font-sans text-base font-semibold text-text1">Prescriptions</h4>
            <table class="w-full border-collapse text-sm">
              <thead>
                <tr class="bg-surface2">
                  <th class="px-4 py-3 text-left font-mono text-[11px] uppercase tracking-mono text-text2">Drug Name</th>
                  <th class="px-4 py-3 text-left font-mono text-[11px] uppercase tracking-mono text-text2">Dose</th>
                  <th class="px-4 py-3 text-left font-mono text-[11px] uppercase tracking-mono text-text2">Duration</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="item in consultationDetailsByAppointment[appointment.id].prescription_items"
                  :key="item.id"
                  class="border-t border-border transition-colors duration-150 hover:bg-surface2"
                >
                  <td class="px-4 py-3 font-sans text-sm text-text1">{{ item.drug_name }}</td>
                  <td class="px-4 py-3 font-sans text-sm text-text1">{{ item.dose }}</td>
                  <td class="px-4 py-3 font-sans text-sm text-text1">{{ item.duration }}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Tests -->
          <div v-if="consultationDetailsByAppointment[appointment.id].requested_tests?.length > 0">
            <h4 class="mb-2 font-sans text-base font-semibold text-text1">Requested Tests</h4>
            <table class="w-full border-collapse text-sm">
              <thead>
                <tr class="bg-surface2">
                  <th class="px-4 py-3 text-left font-mono text-[11px] uppercase tracking-mono text-text2">Test Name</th>
                  <th class="px-4 py-3 text-left font-mono text-[11px] uppercase tracking-mono text-text2">Notes</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="test in consultationDetailsByAppointment[appointment.id].requested_tests"
                  :key="test.id"
                  class="border-t border-border transition-colors duration-150 hover:bg-surface2"
                >
                  <td class="px-4 py-3 font-sans text-sm text-text1">{{ test.test_name }}</td>
                  <td class="px-4 py-3 font-sans text-sm text-text1">{{ test.notes || "—" }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          </div>
          <div
            v-else-if="consultationDetailsByAppointment[appointment.id] === null"
            class="rounded border border-border bg-surface2 px-4 py-3 font-sans text-sm text-text2"
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

    consultations.value = rawAppointments
      .map(normalizeAppointment)
      .filter(canViewConsultation);
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

function hasConsultation(appointment) {
  return Boolean(
    appointment.has_consultation ||
    appointment.hasConsultation ||
    appointment.consultation_id ||
    appointment.consultationId
  );
}

function canViewConsultation(appointment) {
  const status = appointment.status || "UNKNOWN";
  return status === "COMPLETED" && hasConsultation(appointment);
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
