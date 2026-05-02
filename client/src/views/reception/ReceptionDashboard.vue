<template>
  <div class="space-y-6 bg-bg text-text1 font-sans">
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

    <div class="rounded border border-border bg-surface p-4">
      <h2 class="mb-4 font-sans text-xl font-bold leading-tight text-text1">Quick Actions</h2>
      <div class="space-y-2">
        <router-link
          to="/reception/check-in"
          class="block rounded border border-border bg-surface2 px-4 py-3 text-center font-mono text-[11px] uppercase tracking-mono text-text1 transition-all duration-150 cursor-pointer hover:border-accent hover:text-accent"
        >
          Go to Check-In Desk
        </router-link>
        <router-link
          to="/reception/slots"
          class="block rounded border border-border bg-surface2 px-4 py-3 text-center font-mono text-[11px] uppercase tracking-mono text-text1 transition-all duration-150 cursor-pointer hover:border-accent hover:text-accent"
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
  () => appointmentsStore.list.filter((a) => a.status === "checked_in").length
);
const completedCount = computed(
  () => appointmentsStore.list.filter((a) => a.status === "completed").length
);

onMounted(async () => {
  loading.value = true;
  await appointmentsStore.fetchAppointments();
  loading.value = false;
});
</script>
