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
        v-for="entry in items"
        :key="entry.id"
        class="bg-white rounded-lg shadow-md p-6"
      >
        <div class="flex justify-between items-start">
          <div>
            <h3 class="text-lg font-semibold">
              Dr. {{ entry.doctor?.name }}
            </h3>
            <p class="text-sm text-gray-600">
              {{ entry.doctor?.specialization }}
            </p>
            <p class="text-sm text-gray-600 mt-2">
              Preferred date: {{ formatDate(entry.preferred_date) }}
            </p>
            <p class="text-xs text-gray-500 mt-1">
              Added on: {{ formatDateTime(entry.created_at) }}
            </p>
          </div>
          <span
            :class="[
              'px-3 py-1 rounded-full text-sm font-semibold',
              entry.status === 'active'
                ? 'bg-yellow-100 text-yellow-700'
                : 'bg-gray-100 text-gray-700',
            ]"
          >
            {{ entry.status }}
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
    items.value = Array.isArray(response) ? response : response.results || [];
  } catch (err) {
    console.error(err);
  } finally {
    loading.value = false;
  }
});

function formatDate(dateString) {
  if (!dateString) return "";
  return new Date(dateString).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

function formatDateTime(dateTime) {
  if (!dateTime) return "";
  return new Date(dateTime).toLocaleString("en-US", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}
</script>
