<template>
  <div class="space-y-8">
    <div class="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
      <div>
        <h1 class="text-3xl font-bold text-slate-900">Analytics</h1>
        <p class="mt-1 text-sm text-slate-600">
          Monitor clinic performance, appointment trends, and doctor activity.
        </p>
      </div>

      <button
        type="button"
        :disabled="analytics.loading"
        @click="refreshAnalytics"
        class="w-fit rounded-xl bg-gradient-to-r from-blue-600 to-cyan-500 px-5 py-2.5 text-sm font-semibold text-white shadow-md transition hover:shadow-lg disabled:cursor-not-allowed disabled:opacity-60"
      >
        {{ analytics.loading ? "Loading..." : "Refresh" }}
      </button>
    </div>

    <div
      v-if="analytics.error"
      class="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm font-medium text-red-700"
    >
      {{ analytics.error }}
    </div>

    <div
      v-if="analytics.loading && !analytics.hasData"
      class="rounded-xl border border-slate-200 bg-white px-4 py-6 text-center text-sm font-medium text-slate-600 shadow-sm"
    >
      Loading analytics data...
    </div>

    <template v-else>
      <section class="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Total Users" :value="overview.total_users || 0" color="blue" icon="U" />
        <StatCard label="Active Users" :value="overview.active_users || 0" color="green" icon="A" />
        <StatCard label="Pending Doctors" :value="overview.pending_doctors || 0" color="amber" icon="P" />
        <StatCard label="Waiting List" :value="overview.waiting_list || 0" color="cyan" icon="W" />
        <StatCard label="Total Appointments" :value="overview.total_appointments || 0" color="purple" icon="T" />
        <StatCard label="Completion Rate" :value="formatRate(overview.completion_rate)" color="green" icon="C" />
        <StatCard label="Cancellation Rate" :value="formatRate(overview.cancellation_rate)" color="red" icon="X" />
        <StatCard label="No-show Rate" :value="formatRate(overview.no_show_rate)" color="amber" icon="N" />
      </section>

      <section class="grid grid-cols-1 gap-6 xl:grid-cols-2">
        <div class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <div class="mb-4">
            <h2 class="text-lg font-bold text-slate-900">Appointments by Status</h2>
            <p class="text-sm text-slate-500">Distribution of appointments by lifecycle status.</p>
          </div>

          <apexchart
            v-if="statusItems.length"
            type="donut"
            height="320"
            :options="statusChartOptions"
            :series="statusChartSeries"
          />

          <p v-else class="py-12 text-center text-sm text-slate-500">No appointment status data available.</p>
        </div>

        <div class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <div class="mb-4">
            <h2 class="text-lg font-bold text-slate-900">Appointments by Month</h2>
            <p class="text-sm text-slate-500">Booking trend based on appointment creation date.</p>
          </div>

          <apexchart
            v-if="monthItems.length"
            type="area"
            height="320"
            :options="monthChartOptions"
            :series="monthChartSeries"
          />

          <p v-else class="py-12 text-center text-sm text-slate-500">No monthly appointment data available.</p>
        </div>
      </section>

      <section class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div class="mb-4">
          <h2 class="text-lg font-bold text-slate-900">Top Specializations</h2>
          <p class="text-sm text-slate-500">Most requested specializations based on appointment count.</p>
        </div>

        <apexchart
          v-if="specializationItems.length"
          type="bar"
          height="340"
          :options="specializationChartOptions"
          :series="specializationChartSeries"
        />

        <p v-else class="py-12 text-center text-sm text-slate-500">No specialization data available.</p>
      </section>

      <section class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div class="mb-4 flex items-end justify-between gap-4">
          <div>
            <h2 class="text-lg font-bold text-slate-900">Doctor Performance</h2>
            <p class="text-sm text-slate-500">Sortable summary of appointments per doctor.</p>
          </div>

          <div class="text-xs text-slate-500">
            Sorted by {{ sortLabel }}
          </div>
        </div>

        <BaseTable :items="sortedDoctorItems" :loading="analytics.loading" title="Doctor Performance" table-class="min-w-[960px] text-sm">
          <template #thead>
            <th class="px-4 py-3 font-semibold cursor-pointer" @click="setSort('doctor_name')">Doctor</th>
            <th class="px-4 py-3 font-semibold cursor-pointer" @click="setSort('specialization')">Specialization</th>
            <th class="px-4 py-3 font-semibold cursor-pointer" @click="setSort('total_appointments')">Total</th>
            <th class="px-4 py-3 font-semibold cursor-pointer" @click="setSort('confirmed_count')">Confirmed</th>
            <th class="px-4 py-3 font-semibold cursor-pointer" @click="setSort('checked_in_count')">Checked-in</th>
            <th class="px-4 py-3 font-semibold cursor-pointer" @click="setSort('completed_count')">Completed</th>
            <th class="px-4 py-3 font-semibold cursor-pointer" @click="setSort('cancelled_count')">Cancelled</th>
            <th class="px-4 py-3 font-semibold cursor-pointer" @click="setSort('no_show_count')">No-show</th>
          </template>

          <template #tbody="{ items }">
            <tr v-if="!items.length">
              <td colspan="8" class="px-4 py-8 text-center text-slate-500">No doctor performance data available.</td>
            </tr>

            <tr v-for="doctor in items" :key="doctor.doctor_id" class="border-b border-slate-100 text-slate-700">
              <td class="px-4 py-3 font-semibold text-slate-900">{{ doctor.doctor_name }}</td>
              <td class="px-4 py-3">{{ doctor.specialization }}</td>
              <td class="px-4 py-3">{{ doctor.total_appointments }}</td>
              <td class="px-4 py-3">{{ doctor.confirmed_count }}</td>
              <td class="px-4 py-3">{{ doctor.checked_in_count }}</td>
              <td class="px-4 py-3">{{ doctor.completed_count }}</td>
              <td class="px-4 py-3">{{ doctor.cancelled_count }}</td>
              <td class="px-4 py-3">{{ doctor.no_show_count }}</td>
            </tr>
          </template>
        </BaseTable>
      </section>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { useAnalyticsStore } from "../../stores/analytics";
import StatCard from "../../components/StatCard.vue";
import BaseTable from "../../components/ui/BaseTable.vue";

const analytics = useAnalyticsStore();

const sortKey = ref("total_appointments");
const sortDirection = ref("desc");

const overview = computed(() => analytics.overview || {});
const statusItems = computed(() => analytics.appointmentsByStatus || []);
const monthItems = computed(() => analytics.appointmentsByMonth || []);
const specializationItems = computed(() => analytics.topSpecializations || []);
const doctorItems = computed(() => analytics.doctorPerformance || []);

const sortedDoctorItems = computed(() => {
  const items = [...doctorItems.value];
  const key = sortKey.value;
  const direction = sortDirection.value === "asc" ? 1 : -1;

  return items.sort((left, right) => {
    const leftValue = left?.[key] ?? 0;
    const rightValue = right?.[key] ?? 0;

    if (typeof leftValue === "string" || typeof rightValue === "string") {
      return String(leftValue).localeCompare(String(rightValue)) * direction;
    }

    return (Number(leftValue) - Number(rightValue)) * direction;
  });
});

const sortLabel = computed(() => `${sortKey.value} (${sortDirection.value})`);

const statusChartSeries = computed(() => statusItems.value.map((item) => item.count || 0));
const statusChartOptions = computed(() => ({
  chart: { type: "donut", toolbar: { show: false } },
  labels: statusItems.value.map((item) => formatStatus(item.status)),
  legend: { position: "bottom" },
  dataLabels: { enabled: true },
}));

const monthChartSeries = computed(() => [
  {
    name: "Appointments",
    data: monthItems.value.map((item) => item.count || 0),
  },
]);

const monthChartOptions = computed(() => ({
  chart: { type: "area", toolbar: { show: false } },
  xaxis: { categories: monthItems.value.map((item) => item.month) },
  stroke: { curve: "smooth" },
  dataLabels: { enabled: false },
  tooltip: { y: { formatter: (value) => `${value} appointments` } },
}));

const specializationChartSeries = computed(() => [
  {
    name: "Appointments",
    data: specializationItems.value.map(
      (item) => item.count ?? item.appointment_count ?? 0
    ),
  },
]);

const specializationChartOptions = computed(() => ({
  chart: { type: "bar", toolbar: { show: false } },
  xaxis: { categories: specializationItems.value.map((item) => item.specialization) },
  plotOptions: { bar: { borderRadius: 6, columnWidth: "45%" } },
  dataLabels: { enabled: false },
  tooltip: { y: { formatter: (value) => `${value} appointments` } },
}));

async function refreshAnalytics() {
  await analytics.loadAnalytics();
}

function setSort(key) {
  if (sortKey.value === key) {
    sortDirection.value = sortDirection.value === "asc" ? "desc" : "asc";
    return;
  }

  sortKey.value = key;
  sortDirection.value = "desc";
}

function formatStatus(status) {
  if (!status) return "Unknown";

  return String(status)
    .toLowerCase()
    .split("_")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}

function formatRate(value) {
  if (value === null || value === undefined || value === "") return "0%";
  return typeof value === "number" ? `${value.toFixed(0)}%` : `${value}%`;
}

onMounted(() => {
  refreshAnalytics();
});
</script>