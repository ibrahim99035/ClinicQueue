<template>
  <div class="space-y-6">
    <PageHeader
      title="My Schedule"
      subtitle="Your working hours and exceptions"
    />

    <div class="grid md:grid-cols-2 gap-6">
      <!-- Weekly Schedules -->
      <div class="bg-white rounded-lg shadow-md p-6">
        <h2 class="text-lg font-semibold mb-4">Working Hours</h2>
        <div v-if="loadingSchedules" class="text-gray-500">Loading...</div>
        <div v-else-if="schedules.length === 0" class="text-gray-500">
          No schedules configured
        </div>
        <div v-else class="space-y-2">
          <div
            v-for="schedule in schedules"
            :key="schedule.id"
            class="p-3 border rounded-lg text-sm"
          >
            <p class="font-semibold">{{ getDayName(schedule.day_of_week) }}</p>
            <p class="text-gray-600">
              {{ formatTime(schedule.start_time) }} - {{ formatTime(schedule.end_time) }}
            </p>
          </div>
        </div>
      </div>

      <!-- Exceptions -->
      <div class="bg-white rounded-lg shadow-md p-6">
        <h2 class="text-lg font-semibold mb-4">Upcoming Exceptions</h2>
        <div v-if="loadingExceptions" class="text-gray-500">Loading...</div>
        <div v-else-if="exceptions.length === 0" class="text-gray-500">
          No exceptions
        </div>
        <div v-else class="space-y-2">
          <div
            v-for="exception in exceptions"
            :key="exception.id"
            class="p-3 border rounded-lg text-sm"
          >
            <p class="font-semibold">{{ exception.exception_type }}</p>
            <p class="text-gray-600">
              {{ formatDate(exception.date) }}
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import PageHeader from "../../components/PageHeader.vue";
import useToast from "../../composables/useToast.js";
import * as schedulingApi from "../../api/scheduling.js";

const toast = useToast();
const schedules = ref([]);
const exceptions = ref([]);
const loadingSchedules = ref(false);
const loadingExceptions = ref(false);

const days = [
  "Sunday",
  "Monday",
  "Tuesday",
  "Wednesday",
  "Thursday",
  "Friday",
  "Saturday",
];

onMounted(async () => {
  loadingSchedules.value = true;
  loadingExceptions.value = true;
  try {
    schedules.value = await schedulingApi.getWeeklySchedules();
  } catch (err) {
    toast.error("Failed to load schedule");
  } finally {
    loadingSchedules.value = false;
  }

  try {
    exceptions.value = await schedulingApi.getScheduleExceptions();
  } catch (err) {
    toast.error("Failed to load exceptions");
  } finally {
    loadingExceptions.value = false;
  }
});

function getDayName(dayNum) {
  return days[dayNum] || "Unknown";
}

function formatTime(timeString) {
  if (!timeString) return "";
  return new Date(`2000-01-01T${timeString}`).toLocaleTimeString("en-US", {
    hour: "2-digit",
    minute: "2-digit",
  });
}

function formatDate(dateString) {
  if (!dateString) return "";
  return new Date(dateString).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}
</script>
