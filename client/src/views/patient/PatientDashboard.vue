<template>
  <div class="space-y-6">
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

    <div class="bg-white rounded-lg shadow-md p-6">
      <h2 class="text-lg font-semibold mb-4">Upcoming Appointments</h2>
      <div v-if="loading" class="text-gray-500">Loading...</div>
      <div v-else-if="upcomingAppointments.length === 0" class="text-gray-500">
        No upcoming appointments. <router-link to="/patient/book" class="text-blue-600 hover:underline">Book one now</router-link>
      </div>
      <div v-else class="space-y-3">
        <div
          v-for="apt in upcomingAppointments"
          :key="apt.id"
          class="flex justify-between items-center p-3 border rounded-lg"
        >
          <div>
            <p class="font-semibold">Dr. {{ apt.doctor?.name }}</p>
            <p class="text-sm text-gray-600">{{ formatDateTime(apt.slot?.start) }}</p>
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
      ["requested", "confirmed", "checked_in"].includes(a.status) &&
      new Date(a.slot?.start) > new Date()
  )
);

const upcomingCount = computed(() => upcomingAppointments.value.length);
const completedCount = computed(
  () => appointmentsStore.list.filter((a) => a.status === "completed").length
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
