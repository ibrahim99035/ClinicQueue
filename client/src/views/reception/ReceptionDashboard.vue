<template>
  <div class="space-y-6">
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

    <div class="bg-white rounded-lg shadow-md p-6">
      <h2 class="text-lg font-semibold mb-4">Quick Actions</h2>
      <div class="space-y-2">
        <router-link
          to="/reception/check-in"
          class="block px-4 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 text-center"
        >
          Go to Check-In Desk
        </router-link>
        <router-link
          to="/reception/slots"
          class="block px-4 py-3 bg-green-500 text-white rounded-lg hover:bg-green-600 text-center"
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
