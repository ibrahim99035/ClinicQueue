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
        v-for="consultation in consultations"
        :key="consultation.id"
        class="bg-white rounded-lg shadow-md p-6"
      >
        <div class="flex justify-between items-start mb-4">
          <div>
            <h3 class="text-lg font-semibold">
              Dr. {{ consultation.appointment?.doctor?.name }}
            </h3>
            <p class="text-sm text-gray-600">
              Consultation on {{ formatDateTime(consultation.created_at) }}
            </p>
          </div>
          <button
            @click="selectedId = selectedId === consultation.id ? null : consultation.id"
            class="text-blue-600 hover:underline"
          >
            {{ selectedId === consultation.id ? "Collapse" : "View Details" }}
          </button>
        </div>

        <div v-if="selectedId === consultation.id" class="space-y-4 border-t pt-4">
          <!-- Diagnosis -->
          <div>
            <h4 class="font-semibold text-gray-700 mb-2">Diagnosis</h4>
            <p class="text-gray-600 whitespace-pre-wrap">
              {{ consultation.diagnosis || "Not recorded" }}
            </p>
          </div>

          <!-- Notes -->
          <div>
            <h4 class="font-semibold text-gray-700 mb-2">Doctor's Notes</h4>
            <p class="text-gray-600 whitespace-pre-wrap">
              {{ consultation.notes || "No notes" }}
            </p>
          </div>

          <!-- Prescriptions -->
          <div v-if="consultation.prescription_items?.length > 0">
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
                  v-for="item in consultation.prescription_items"
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
          <div v-if="consultation.test_requests?.length > 0">
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
                  v-for="test in consultation.test_requests"
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
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import PageHeader from "../../components/PageHeader.vue";
import useToast from "../../composables/useToast.js";
import * as emrApi from "../../api/emr.js";

const toast = useToast();
const loading = ref(false);
const consultations = ref([]);
const selectedId = ref(null);

onMounted(async () => {
  loading.value = true;
  try {
    consultations.value = await emrApi.listConsultations();
  } catch (err) {
    toast.error("Failed to load consultations");
  } finally {
    loading.value = false;
  }
});

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
