<template>
  <div class="space-y-6 bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 font-sans">
    <PageHeader title="Dashboard" subtitle="Welcome back to ClinicQueue" />

    <div class="grid grid-cols-3 gap-4">
      <StatCard
        label="Upcoming Appointments"
        :value="upcomingCount"
        color="blue"
      />
      <StatCard
        label="Completed Consultations"
        :value="completedCount"
        color="green"
      />
      <StatCard
        label="On Waiting List"
        :value="waitingCount"
        color="amber"
      />
    </div>

    <div class="rounded border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-4">
      <h2 class="mb-4 font-sans text-xl font-bold leading-tight text-slate-900 dark:text-slate-100">Upcoming Appointments</h2>
      <div v-if="loading" class="font-sans text-sm text-slate-500 dark:text-slate-400">Loading...</div>
      <div v-else-if="upcomingAppointments.length === 0" class="font-sans text-sm text-slate-500 dark:text-slate-400">
        No upcoming appointments. <router-link to="/patient/book" class="font-mono text-[11px] uppercase tracking-wide text-blue-600 dark:text-blue-400 transition-all duration-150 cursor-pointer hover:text-blue-700 dark:hover:text-blue-300">Book one now</router-link>
      </div>
      <div v-else class="space-y-3">
        <div
          v-for="apt in upcomingAppointments"
          :key="apt.id"
          class="flex items-center justify-between rounded border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800 p-3"
        >
          <div>
            <p class="font-sans text-sm font-semibold text-slate-900 dark:text-slate-100">Dr. {{ apt.doctor_name || "Unknown" }}</p>
            <p class="font-mono text-[11px] uppercase tracking-wide text-slate-500 dark:text-slate-400">{{ formatDateTime(apt.slot_time) }}</p>
          </div>
          <StatusBadge :status="apt.status" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import PageHeader from "../../components/PageHeader.vue";
import StatCard from "../../components/StatCard.vue";
import StatusBadge from "../../components/StatusBadge.vue";
import { useAppointmentsStore } from "../../stores/appointments";

const appointmentsStore = useAppointmentsStore();
const loading = ref(false);

const upcomingAppointments = computed(() =>
  appointmentsStore.list.filter(
    (a) =>
      ["REQUESTED", "CONFIRMED", "CHECKED_IN"].includes(a.status) &&
      new Date(a.slot_time) > new Date()
  )
);

const upcomingCount = computed(() => upcomingAppointments.value.length);
const completedCount = computed(
  () => appointmentsStore.list.filter((a) => a.status === "COMPLETED").length
);
const waitingCount = computed(
  () => appointmentsStore.list.filter((a) => a.status === "waiting").length
);

function formatDateTime(dateTime) {
  if (!dateTime) return "";
  return new Date(dateTime).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

onMounted(async () => {
  loading.value = true;
  await appointmentsStore.fetchAppointments();
  loading.value = false;
});
</script>
