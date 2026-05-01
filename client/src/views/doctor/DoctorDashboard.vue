<template>
  <div class="space-y-6">
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

    <div class="grid md:grid-cols-2 gap-6">
      <div class="bg-white rounded-lg shadow-md p-6">
        <h2 class="text-lg font-semibold mb-4">Quick Actions</h2>
        <div class="space-y-2">
          <router-link
            to="/doctor/queue"
            class="block px-4 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 text-center"
          >
            View Appointment Queue
          </router-link>
          <router-link
            to="/doctor/schedule"
            class="block px-4 py-3 bg-green-500 text-white rounded-lg hover:bg-green-600 text-center"
          >
            View My Schedule
          </router-link>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow-md p-6">
        <h2 class="text-lg font-semibold mb-4">Today's Schedule</h2>
        <div v-if="todayAppointments.length === 0" class="text-gray-500">
          No appointments today
        </div>
        <div v-else class="space-y-2">
          <div
            v-for="apt in todayAppointments.slice(0, 5)"
            :key="apt.id"
            class="flex justify-between items-center p-2 border rounded"
          >
            <span>{{ formatTime(apt.slot?.start) }}</span>
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
