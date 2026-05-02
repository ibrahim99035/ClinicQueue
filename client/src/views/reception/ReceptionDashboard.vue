<template>
  <div class="space-y-6 bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 font-sans">
    <PageHeader
      title="Reception Dashboard"
      subtitle="Overview of appointments today"
    />

    <div class="grid grid-cols-3 gap-4">
      <StatCard
        label="Total Appointments"
        :value="totalCount"
        color="blue"
      />
      <StatCard
        label="Checked In"
        :value="checkedInCount"
        color="green"
      />
      <StatCard
        label="Completed"
        :value="completedCount"
        color="amber"
      />
    </div>

    <div class="rounded border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-4">
      <h2 class="mb-4 font-sans text-xl font-bold leading-tight text-slate-900 dark:text-slate-100">Quick Actions</h2>
      <div class="space-y-2">
        <router-link
          to="/reception/check-in"
          class="block rounded border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800 px-4 py-3 text-center font-mono text-[11px] uppercase tracking-wide text-slate-900 dark:text-slate-100 transition-all duration-150 cursor-pointer hover:border-blue-500 hover:text-blue-600 dark:hover:text-blue-400"
        >
          Go to Check-In Desk
        </router-link>
        <router-link
          to="/reception/slots"
          class="block rounded border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800 px-4 py-3 text-center font-mono text-[11px] uppercase tracking-wide text-slate-900 dark:text-slate-100 transition-all duration-150 cursor-pointer hover:border-blue-500 hover:text-blue-600 dark:hover:text-blue-400"
        >
          Generate Appointment Slots
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from "vue";
import PageHeader from "../../components/PageHeader.vue";
import StatCard from "../../components/StatCard.vue";
import { useAppointmentsStore } from "../../stores/appointments";

const appointmentsStore = useAppointmentsStore();
const loading = ref(false);

const totalCount = computed(() => appointmentsStore.list.length);
const checkedInCount = computed(
  () => appointmentsStore.list.filter((a) => a.status === "CHECKED_IN").length
);
const completedCount = computed(
  () => appointmentsStore.list.filter((a) => a.status === "COMPLETED").length
);

onMounted(async () => {
  loading.value = true;
  await appointmentsStore.fetchAppointments();
  loading.value = false;
});
</script>
