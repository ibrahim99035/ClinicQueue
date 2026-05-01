<script setup>
import { computed, onMounted, ref} from "vue";

import {
  getAdminOverview,
  getAppointmentsByStatus,
  getAppointmentsByMonth,
  getTopSpecializations,
  getDoctorPerformance,
} from "../../api/analytics";

const loading = ref(false);
const errorMessage = ref("");
const overview = ref({});

const appointmentsByStatus = ref({ results: [] });
const appointmentsByMonth = ref({ results: [] });
const topSpecializations = ref({ results: [] });
const doctorPerformance = ref({ results: [] });
const statusItems = computed(() => appointmentsByStatus.value.results || []);
const monthItems = computed(() => appointmentsByMonth.value.results || []);
const specializationItems = computed(() => topSpecializations.value.results || []);
const doctorItems = computed(() => doctorPerformance.value.results || []);
const statusChartSeries = computed(() => {
  return statusItems.value.map((item) => item.count);
});
const statusChartOptions = computed(() => {
  return {
    chart: {
      type: "donut",
      toolbar: {
        show: false,
      },
    },
    labels: statusItems.value.map((item) => formatStatus(item.status)),
    legend: {
      position: "bottom",
    },
    dataLabels: {
      enabled: true,
    },
  };
});

const monthChartSeries = computed(() => {
  return [
    {
      name: "Appointments",
      data: monthItems.value.map((item) => item.count),
    },
  ];
});

const monthChartOptions = computed(() => {
  return {
    chart: {
      type: "area",
      toolbar: {
        show: false,
      },
    },
    xaxis: {
      categories: monthItems.value.map((item) => item.month),
    },
    stroke: {
      curve: "smooth",
    },
    dataLabels: {
      enabled: false,
    },
    tooltip: {
      y: {
        formatter: (value) => `${value} appointments`,
      },
    },
  };
});

const specializationChartSeries = computed(() => {
  return [
    {
      name: "Appointments",
      data: specializationItems.value.map((item) => item.appointment_count),
    },
  ];
});

const specializationChartOptions = computed(() => {
  return {
    chart: {
      type: "bar",
      toolbar: {
        show: false,
      },
    },
    xaxis: {
      categories: specializationItems.value.map((item) => item.specialization),
    },
    plotOptions: {
      bar: {
        borderRadius: 6,
        columnWidth: "45%",
      },
    },
    dataLabels: {
      enabled: false,
    },
    tooltip: {
      y: {
        formatter: (value) => `${value} appointments`,
      },
    },
  };
});


async function loadAnalytics() {
  loading.value = true;
  errorMessage.value = "";

  try {
    const overviewData = await getAdminOverview();
    overview.value = overviewData;

    const statusData = await getAppointmentsByStatus();
    appointmentsByStatus.value = statusData;

    const monthData = await getAppointmentsByMonth();
    appointmentsByMonth.value = monthData;

    const specializationData = await getTopSpecializations();
    topSpecializations.value = specializationData;

    const doctorData = await getDoctorPerformance();
    doctorPerformance.value = doctorData;

  } catch (error) {
    errorMessage.value = "Failed to load analytics data.";
  } finally {
    loading.value = false;
  }
}

function formatStatus(status) {
  if (!status) {
    return "Unknown";
  }

  return status
    .toLowerCase()
    .split("_")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}

function formatRate(value) {
  return `${value || 0}%`;
}

onMounted(() => {
  loadAnalytics();
});
</script>
<template>
  <div class="space-y-8">
    <!-- Page Header -->
    <div class="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
      <div>
        <h1 class="text-3xl font-bold text-slate-900">
          Analytics
        </h1>
        <p class="mt-1 text-sm text-slate-600">
          Monitor clinic performance, appointment trends, and doctor activity.
        </p>
      </div>

      <button
        type="button"
        :disabled="loading"
        @click="loadAnalytics"
        class="w-fit rounded-xl bg-gradient-to-r from-blue-600 to-cyan-500 px-5 py-2.5 text-sm font-semibold text-white shadow-md transition hover:shadow-lg disabled:cursor-not-allowed disabled:opacity-60"
      >
        {{ loading ? "Loading..." : "Refresh" }}
      </button>
    </div>

    <!-- Error -->
    <div
      v-if="errorMessage"
      class="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm font-medium text-red-700"
    >
      {{ errorMessage }}
    </div>

    <!-- Loading -->
    <div
      v-if="loading"
      class="rounded-xl border border-slate-200 bg-white px-4 py-6 text-center text-sm font-medium text-slate-600 shadow-sm"
    >
      Loading analytics data...
    </div>

    <template v-else>
      <!-- Summary Cards -->
      <section class="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
        <div class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <p class="text-sm font-medium text-slate-500">Total Appointments</p>
          <h2 class="mt-2 text-3xl font-bold text-slate-900">
            {{ overview.appointments?.total || 0 }}
          </h2>
        </div>

        <div class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <p class="text-sm font-medium text-slate-500">Completed</p>
          <h2 class="mt-2 text-3xl font-bold text-slate-900">
            {{ overview.appointments?.completed || 0 }}
          </h2>
        </div>

        <div class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <p class="text-sm font-medium text-slate-500">Cancelled</p>
          <h2 class="mt-2 text-3xl font-bold text-slate-900">
            {{ overview.appointments?.cancelled || 0 }}
          </h2>
        </div>

        <div class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <p class="text-sm font-medium text-slate-500">No-show Rate</p>
          <h2 class="mt-2 text-3xl font-bold text-slate-900">
            {{ formatRate(overview.rates?.no_show_rate) }}
          </h2>
        </div>

        <div class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <p class="text-sm font-medium text-slate-500">Total Doctors</p>
          <h2 class="mt-2 text-3xl font-bold text-slate-900">
            {{ overview.doctors?.total || 0 }}
          </h2>
        </div>

        <div class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <p class="text-sm font-medium text-slate-500">Total Patients</p>
          <h2 class="mt-2 text-3xl font-bold text-slate-900">
            {{ overview.patients?.total || 0 }}
          </h2>
        </div>

        <div class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <p class="text-sm font-medium text-slate-500">Pending Doctors</p>
          <h2 class="mt-2 text-3xl font-bold text-slate-900">
            {{ overview.doctors?.pending || 0 }}
          </h2>
        </div>

        <div class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <p class="text-sm font-medium text-slate-500">Unread Notifications</p>
          <h2 class="mt-2 text-3xl font-bold text-slate-900">
            {{ overview.notifications?.unread || 0 }}
          </h2>
        </div>
      </section>

      <!-- Charts -->
      <section class="grid grid-cols-1 gap-6 xl:grid-cols-2">
        <div class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <div class="mb-4">
            <h2 class="text-lg font-bold text-slate-900">
              Appointments by Status
            </h2>
            <p class="text-sm text-slate-500">
              Distribution of appointments by lifecycle status.
            </p>
          </div>

          <apexchart
            v-if="statusItems.length"
            type="donut"
            height="320"
            :options="statusChartOptions"
            :series="statusChartSeries"
          />

          <p v-else class="py-12 text-center text-sm text-slate-500">
            No appointment status data available.
          </p>
        </div>

        <div class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <div class="mb-4">
            <h2 class="text-lg font-bold text-slate-900">
              Appointments by Month
            </h2>
            <p class="text-sm text-slate-500">
              Booking trend based on appointment creation date.
            </p>
          </div>

          <apexchart
            v-if="monthItems.length"
            type="area"
            height="320"
            :options="monthChartOptions"
            :series="monthChartSeries"
          />

          <p v-else class="py-12 text-center text-sm text-slate-500">
            No monthly appointment data available.
          </p>
        </div>
      </section>

      <section class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div class="mb-4">
          <h2 class="text-lg font-bold text-slate-900">
            Top Specializations
          </h2>
          <p class="text-sm text-slate-500">
            Most requested specializations based on appointment count.
          </p>
        </div>

        <apexchart
          v-if="specializationItems.length"
          type="bar"
          height="340"
          :options="specializationChartOptions"
          :series="specializationChartSeries"
        />

        <p v-else class="py-12 text-center text-sm text-slate-500">
          No specialization data available.
        </p>
      </section>

      <!-- Doctor Performance Table -->
      <section class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div class="mb-4">
          <h2 class="text-lg font-bold text-slate-900">
            Doctor Performance
          </h2>
          <p class="text-sm text-slate-500">
            Count-based summary for doctors who have appointments.
          </p>
        </div>

        <div class="overflow-x-auto">
          <table class="w-full min-w-[900px] border-collapse">
            <thead>
              <tr class="border-b border-slate-200 bg-slate-50 text-left text-sm text-slate-600">
                <th class="px-4 py-3 font-semibold">Doctor</th>
                <th class="px-4 py-3 font-semibold">Specialization</th>
                <th class="px-4 py-3 font-semibold">Total</th>
                <th class="px-4 py-3 font-semibold">Confirmed</th>
                <th class="px-4 py-3 font-semibold">Checked-in</th>
                <th class="px-4 py-3 font-semibold">Completed</th>
                <th class="px-4 py-3 font-semibold">Cancelled</th>
                <th class="px-4 py-3 font-semibold">No-show</th>
              </tr>
            </thead>

            <tbody>
              <tr v-if="!doctorItems.length">
                <td colspan="8" class="px-4 py-8 text-center text-sm text-slate-500">
                  No doctor performance data available.
                </td>
              </tr>

              <tr
                v-for="doctor in doctorItems"
                :key="doctor.doctor_id"
                class="border-b border-slate-100 text-sm text-slate-700"
              >
                <td class="px-4 py-3 font-semibold text-slate-900">
                  {{ doctor.doctor_name }}
                </td>
                <td class="px-4 py-3">
                  {{ doctor.specialization }}
                </td>
                <td class="px-4 py-3">
                  {{ doctor.total_appointments }}
                </td>
                <td class="px-4 py-3">
                  {{ doctor.confirmed_count }}
                </td>
                <td class="px-4 py-3">
                  {{ doctor.checked_in_count }}
                </td>
                <td class="px-4 py-3">
                  {{ doctor.completed_count }}
                </td>
                <td class="px-4 py-3">
                  {{ doctor.cancelled_count }}
                </td>
                <td class="px-4 py-3">
                  {{ doctor.no_show_count }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </template>
  </div>
</template>