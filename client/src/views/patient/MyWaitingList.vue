<template>
  <div class="space-y-6">
    <PageHeader
      title="Waiting List"
      subtitle="Waiting list entries for appointments"
    />

    <div v-if="loading" class="text-center py-8 text-gray-500">
      Loading...
    </div>
    <div v-else-if="items.length === 0" class="bg-white rounded-lg shadow-md p-8 text-center text-gray-500">
      <p>You're not on any waiting lists</p>
      <router-link to="/patient/book" class="text-blue-600 hover:underline">
        Book an appointment
      </router-link>
    </div>

    <div v-else class="space-y-4">
      <div
        v-for="item in items"
        :key="item.id"
        class="bg-white rounded-lg shadow-md p-6"
      >
        <div class="flex justify-between items-start">
          <div>
            <h3 class="text-lg font-semibold">
              {{
                item.doctorName && item.doctorName !== "Unknown"
                  ? `Dr. ${item.doctorName}`
                  : "Dr. Unknown"
              }}
            </h3>
            <p class="text-sm text-gray-600 mt-2">
              Preferred date: {{ formatDateTime(item.appointmentDateTime) }}
            </p>
            <p class="text-xs text-gray-500 mt-1">
              Added on: {{ formatDateTime(item.created_at) }}
            </p>
          </div>
          <span
            :class="[
              'px-3 py-1 rounded-full text-sm font-semibold',
              item.status === 'REQUESTED'
                ? 'bg-yellow-100 text-yellow-700'
                : 'bg-gray-100 text-gray-700',
            ]"
          >
            {{ item.status || "REQUESTED" }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import PageHeader from "../../components/PageHeader.vue";
import * as appointmentApi from "../../api/appointments.js";

const loading = ref(false);
const items = ref([]);

onMounted(async () => {
  loading.value = true;
  try {
    // Assuming there's a getWaitingList endpoint
    const response = await appointmentApi.getAppointments({
      status: "waiting",
    });
    const rawItems = Array.isArray(response) ? response : response.results || [];
    items.value = rawItems.map(normalizeItem);
  } catch (err) {
    console.error(err);
  } finally {
    loading.value = false;
  }
});

function normalizeItem(item) {
  return {
    ...item,
    doctorName:
      item.doctorName ||
      item.doctor_name ||
      "Unknown",
    appointmentDateTime:
      item.appointmentDateTime ||
      item.slot_time ||
      item.preferred_date ||
      item.created_at ||
      "",
    reason:
      item.reason ||
      "Not specified",
    status:
      item.status ||
      "REQUESTED",
  };
}

function formatDateTime(value) {
  if (!value) return "Not scheduled";

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return date.toLocaleString();
}
</script>
