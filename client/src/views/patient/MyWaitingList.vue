<template>
  <div class="space-y-6 bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 font-sans">
    <PageHeader
      title="Waiting List"
      subtitle="Waiting list entries for appointments"
    />

    <div v-if="loading" class="py-8 text-center font-sans text-sm text-slate-500 dark:text-slate-400">
      Loading...
    </div>
    <div v-else-if="items.length === 0" class="rounded border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-8 text-center font-sans text-sm text-slate-500 dark:text-slate-400">
      <p>You're not on any waiting lists</p>
      <router-link to="/patient/book" class="font-mono text-[11px] uppercase tracking-wide text-blue-600 dark:text-blue-400 transition-all duration-150 cursor-pointer hover:text-blue-700 dark:hover:text-blue-300">
        Book an appointment
      </router-link>
    </div>

    <div v-else class="space-y-4">
      <div
        v-for="item in items"
        :key="item.id"
        class="rounded border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-4"
      >
        <div class="flex items-start justify-between gap-4">
          <div>
            <h3 class="font-sans text-lg font-semibold text-slate-900 dark:text-slate-100">
              {{
                item.doctorName && item.doctorName !== "Unknown"
                  ? `Dr. ${item.doctorName}`
                  : "Dr. Unknown"
              }}
            </h3>
            <p class="mt-2 font-mono text-[11px] uppercase tracking-wide text-slate-500 dark:text-slate-400">
              Preferred date: {{ formatDateTime(item.appointmentDateTime) }}
            </p>
            <p class="mt-1 font-mono text-[11px] uppercase tracking-wide text-slate-400 dark:text-slate-500">
              Added on: {{ formatDateTime(item.created_at) }}
            </p>
          </div>
          <span
            :class="[
              'inline-flex items-center gap-1 rounded border px-2 py-0.5 font-mono text-[10px] uppercase tracking-wider',
              item.status === 'REQUESTED'
                ? 'border-yellow-400/40 text-yellow-400'
                : 'border-slate-200 dark:border-slate-800 text-slate-500 dark:text-slate-400',
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
