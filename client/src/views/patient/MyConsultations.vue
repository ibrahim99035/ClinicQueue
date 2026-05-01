<template>
  <div class="space-y-6">
    <PageHeader
      title="My Consultations"
      subtitle="View your completed consultations"
    />

    <div v-if="loading" class="text-center py-8 text-gray-500">
      Loading consultations...
    </div>
    <div
      v-else-if="consultations.length === 0"
      class="bg-white rounded-lg shadow-md p-8 text-center text-gray-500"
    >
      <p>No completed consultations yet</p>
    </div>

    <div v-else class="space-y-4">
      <div
        v-for="appointment in consultations"
        :key="appointment.id"
        class="bg-white rounded-lg shadow-md p-6"
      >
        <div class="flex justify-between items-start mb-4">
          <div>
            <h3 class="text-lg font-semibold">
              Dr. {{ appointment.doctorName }}
            </h3>
            <p class="text-sm text-gray-600">
              Consultation on {{ formatDateTime(appointment.completed_at || appointment.appointmentDateTime) }}
            </p>
          </div>
          <button
            v-if="appointment.status === 'COMPLETED' || appointment.status === 'completed'"
            @click="toggleConsultation(appointment)"
            class="text-blue-600 hover:underline"
          >
            {{ selectedId === appointment.id ? "Collapse" : "View Details" }}
          </button>
          <span
            v-else
            class="text-sm text-gray-500"
          >
            Consultation not available yet
          </span>
        </div>

        <div v-if="selectedId === appointment.id" class="space-y-4 border-t pt-4">
          <div v-if="loadingDetailsId === appointment.id" class="text-sm text-gray-500">
            Loading consultation details...
          </div>

          <div v-else-if="consultationDetailsByAppointment[appointment.id]" class="space-y-4">
          <!-- Diagnosis -->
          <div>
            <h4 class="font-semibold text-gray-700 mb-2">Diagnosis</h4>
            <p class="text-gray-600 whitespace-pre-wrap">
              {{ consultationDetailsByAppointment[appointment.id].diagnosis || "Not recorded" }}
            </p>
          </div>

          <!-- Notes -->
          <div>
            <h4 class="font-semibold text-gray-700 mb-2">Doctor's Notes</h4>
            <p class="text-gray-600 whitespace-pre-wrap">
              {{ consultationDetailsByAppointment[appointment.id].notes || "No notes" }}
            </p>
          </div>

          <!-- Prescriptions -->
          <div v-if="consultationDetailsByAppointment[appointment.id].prescription_items?.length > 0">
            <h4 class="font-semibold text-gray-700 mb-2">Prescriptions</h4>
            <table class="w-full text-sm border-collapse">
              <thead>
                <tr class="border-b">
                  <th class="text-left py-2">Drug Name</th>
                  <th class="text-left py-2">Dose</th>
                  <th class="text-left py-2">Duration</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="item in consultationDetailsByAppointment[appointment.id].prescription_items"
                  :key="item.id"
                  class="border-b"
                >
                  <td class="py-2">{{ item.drug_name }}</td>
                  <td class="py-2">{{ item.dose }}</td>
                  <td class="py-2">{{ item.duration }}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Tests -->
          <div v-if="consultationDetailsByAppointment[appointment.id].requested_tests?.length > 0">
            <h4 class="font-semibold text-gray-700 mb-2">Requested Tests</h4>
            <table class="w-full text-sm border-collapse">
              <thead>
                <tr class="border-b">
                  <th class="text-left py-2">Test Name</th>
                  <th class="text-left py-2">Notes</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="test in consultationDetailsByAppointment[appointment.id].requested_tests"
                  :key="test.id"
                  class="border-b"
                >
                  <td class="py-2">{{ test.test_name }}</td>
                  <td class="py-2">{{ test.notes || "—" }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          </div>
          <div
            v-else-if="consultationDetailsByAppointment[appointment.id] === null"
            class="rounded-lg bg-slate-50 px-4 py-3 text-sm text-slate-600"
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
