<template>
  <div class="space-y-6 bg-bg text-text1 font-sans">
    <PageHeader 
      title="Doctor Dashboard" 
      subtitle="Overview of your appointments"
    />

    <div class="grid grid-cols-3 gap-4">
      <StatCard
        label="Today's Queue"
        :value="todayQueueCount"
        color="blue"
      />
      <StatCard
        label="Upcoming Appointments"
        :value="upcomingCount"
        color="green"
      />
      <StatCard
        label="Completed Today"
        :value="completedToday"
        color="amber"
      />
    </div>

    <div class="grid gap-6 md:grid-cols-2">
      <div class="rounded border border-border bg-surface p-4">
        <h2 class="mb-4 font-sans text-xl font-bold leading-tight text-text1">Quick Actions</h2>
        <div class="space-y-2">
          <router-link
            to="/doctor/queue"
            class="block rounded border border-border bg-surface2 px-4 py-3 text-center font-mono text-[11px] uppercase tracking-mono text-text1 transition-all duration-150 cursor-pointer hover:border-accent hover:text-accent"
          >
            View Appointment Queue
          </router-link>
          <router-link
            to="/doctor/schedule"
            class="block rounded border border-border bg-surface2 px-4 py-3 text-center font-mono text-[11px] uppercase tracking-mono text-text1 transition-all duration-150 cursor-pointer hover:border-accent hover:text-accent"
          >
            View My Schedule
          </router-link>
        </div>
      </div>

      <div class="rounded border border-border bg-surface p-4">
        <h2 class="mb-4 font-sans text-xl font-bold leading-tight text-text1">Today's Schedule</h2>
        <div v-if="todayAppointments.length === 0" class="font-sans text-sm text-text2">
          No appointments today
        </div>
        <div v-else class="space-y-2">
          <div
            v-for="apt in todayAppointments.slice(0, 5)"
            :key="apt.id"
            class="flex items-center justify-between rounded border border-border bg-surface2 p-3"
          >
            <span class="font-mono text-sm text-text1">{{ formatTime(apt.slot?.start) }}</span>
            <StatusBadge :status="apt.status" />
          </div>
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

const todayAppointments = computed(() => {
  const today = new Date().toDateString();
  return appointmentsStore.list.filter(
    (a) =>
      new Date(a.slot?.start).toDateString() === today &&
      ["confirmed", "checked_in"].includes(a.status)
  );
});

const todayQueueCount = computed(
  () => todayAppointments.value.filter((a) => a.status === "checked_in").length
);
const upcomingCount = computed(() =>
  appointmentsStore.list.filter(
    (a) =>
      a.status === "confirmed" &&
      new Date(a.slot?.start) > new Date()
  ).length
);
const completedToday = computed(() => {
  const today = new Date().toDateString();
  return appointmentsStore.list.filter(
    (a) =>
      a.status === "completed" &&
      new Date(a.completed_at).toDateString() === today
  ).length;
});

function formatTime(dateTime) {
  if (!dateTime) return "";
  return new Date(dateTime).toLocaleTimeString("en-US", {
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
