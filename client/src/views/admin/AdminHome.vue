<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from "vue";
import { getAdminUsers, approveDoctor, getDashboardStats } from "../../api/admin";
import StatCard from "../../components/StatCard.vue";
import StatusBadge from "../../components/StatusBadge.vue";
import SkeletonCard from "../../components/SkeletonCard.vue";
import EmptyState from "../../components/EmptyState.vue";
import {
  Users, UserCheck, Stethoscope, Phone, Shield,
  CheckCircle, Pause, Clock, RefreshCcw, Activity
} from "lucide-vue-next";

const users = ref([]);
const errorMessage = ref("");
const successMessage = ref("");
const loading = ref(false);
const approvingId = ref(null);
const toast = ref({ show: false, type: "success", message: "" });

let toastTimer = null;

function showToast(message, type) {
  toast.value = { show: true, type, message };
  if (toastTimer) clearTimeout(toastTimer);
  toastTimer = setTimeout(() => {
    toast.value = { show: false, type: "success", message: "" };
    toastTimer = null;
  }, 4500);
}

function closeToast() {
  if (toastTimer) { clearTimeout(toastTimer); toastTimer = null; }
  toast.value = { show: false, type: "success", message: "" };
}

onBeforeUnmount(() => {
  if (toastTimer) { clearTimeout(toastTimer); toastTimer = null; }
});

function getUserGroups(user) { return user.groups || []; }

function getFullName(user) {
  const firstName = user.first_name || "";
  const lastName = user.last_name || "";
  const fullName = (firstName + " " + lastName).trim();
  return fullName || user.email || "Unknown";
}

function ApiErrorResponseFromBackend(error) {
  let data = null;
  if (error.response) data = error.response.data;
  if (!data) return error.message || "Something went wrong. Please try again.";
  if (data.detail) return data.detail;
  if (data.message) return data.message;
  if (Array.isArray(data.non_field_errors) && data.non_field_errors.length > 0)
    return data.non_field_errors[0];
  const firstError = Object.keys(data).find((key) => data[key]);
  if (firstError) {
    const errorValue = data[firstError];
    return Array.isArray(errorValue) ? errorValue[0] : errorValue;
  }
  return "Please check the form data.";
}

const totalUsers = computed(() => users.value.length);
const totalDoctors = computed(() => users.value.filter((u) => getUserGroups(u).includes("Doctors")).length);
const totalPatients = computed(() => users.value.filter((u) => getUserGroups(u).includes("Patients")).length);
const totalReceptionists = computed(() => users.value.filter((u) => getUserGroups(u).includes("Receptionists")).length);
const totalAdmins = computed(() => users.value.filter((u) => getUserGroups(u).includes("Admins")).length);
const activeUsers = computed(() => users.value.filter((u) => u.is_active === true).length);
const inactiveUsers = computed(() => users.value.filter((u) => u.is_active === false).length);
const pendingDoctors = computed(() =>
  users.value.filter((u) => getUserGroups(u).includes("Doctors") && u.is_active === false)
);
const recentUsers = computed(() => {
  const sorted = [...users.value].sort(
    (a, b) => new Date(b.date_joined || 0) - new Date(a.date_joined || 0)
  );
  return sorted.slice(0, 5);
});

async function loadDashboard() {
  loading.value = true;
  errorMessage.value = "";
  try {
    const usersResponse = await getAdminUsers();
    const usersData = usersResponse.data || usersResponse;
    users.value = Array.isArray(usersData) ? usersData : usersData.results || [];
  } catch (error) {
    errorMessage.value = ApiErrorResponseFromBackend(error);
    showToast(errorMessage.value, "error");
  } finally {
    loading.value = false;
  }
}

async function handleApproveDoctor(doctorProfile) {
  errorMessage.value = "";
  approvingId.value = doctorProfile.id;
  try {
    await approveDoctor(doctorProfile.doctor_profile?.id || doctorProfile.id);
    successMessage.value = getFullName(doctorProfile) + " approved successfully.";
    showToast(successMessage.value, "success");
    await loadDashboard();
  } catch (error) {
    errorMessage.value = ApiErrorResponseFromBackend(error);
    showToast(errorMessage.value, "error");
  } finally {
    approvingId.value = null;
  }
}

onMounted(() => { loadDashboard(); });
</script>

<template>
  <div class="flex flex-col gap-6">
    <!-- Toast -->
    <Transition name="toast-slide">
      <div
        v-if="toast.show"
        class="fixed right-6 top-6 z-50 w-full max-w-sm rounded-2xl border p-4 shadow-xl"
        :class="toast.type === 'success'
          ? 'border-green-200 bg-green-50 text-green-800 dark:border-green-800 dark:bg-green-950/50 dark:text-green-300'
          : 'border-red-200 bg-red-50 text-red-800 dark:border-red-800 dark:bg-red-950/50 dark:text-red-300'"
      >
        <div class="flex items-start justify-between gap-4">
          <div>
            <p class="text-sm font-bold">{{ toast.type === "success" ? "Success" : "Error" }}</p>
            <p class="mt-1 text-sm leading-6">{{ toast.message }}</p>
          </div>
          <button @click="closeToast" class="rounded-lg px-2 py-1 text-sm font-bold hover:opacity-70">×</button>
        </div>
      </div>
    </Transition>

    <!-- Welcome -->
    <div class="rounded-2xl border border-slate-200 bg-gradient-to-r from-blue-600 to-indigo-700 p-6 text-white shadow-sm dark:border-slate-700">
      <div class="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <p class="mb-1 text-sm font-semibold uppercase tracking-wide text-blue-200">Admin Dashboard</p>
          <h2 class="text-2xl font-bold">Welcome Back</h2>
          <p class="mt-2 max-w-2xl text-sm text-blue-100">Manage users, doctors, schedules, and monitor system health.</p>
        </div>
        <button
          @click="loadDashboard" :disabled="loading"
          class="w-fit rounded-xl bg-white px-5 py-2.5 text-sm font-bold text-blue-700 shadow-sm transition hover:bg-blue-50 disabled:cursor-not-allowed disabled:opacity-60"
        >
          <span class="flex items-center gap-2">
            <RefreshCcw class="h-4 w-4" :class="{ 'animate-spin': loading }" />
            {{ loading ? "Loading..." : "Refresh" }}
          </span>
        </button>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="grid gap-6 md:grid-cols-4">
      <SkeletonCard v-for="i in 4" :key="i" />
    </div>

    <!-- Stats -->
    <div v-else class="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      <StatCard label="Total Users" :value="totalUsers" color="blue">
        <template #icon><Users class="h-6 w-6" /></template>
      </StatCard>
      <StatCard label="Doctors" :value="totalDoctors" color="green">
        <template #icon><Stethoscope class="h-6 w-6" /></template>
      </StatCard>
      <StatCard label="Patients" :value="totalPatients" color="cyan">
        <template #icon><UserCheck class="h-6 w-6" /></template>
      </StatCard>
      <StatCard label="Active Users" :value="activeUsers" color="amber">
        <template #icon><Activity class="h-6 w-6" /></template>
      </StatCard>
    </div>

    <!-- Quick Access -->
    <div class="grid gap-4 md:grid-cols-3">
      <router-link to="/admin/users" class="group rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition-all duration-200 hover:shadow-md dark:border-slate-800 dark:bg-slate-900">
        <div class="mb-3 flex h-10 w-10 items-center justify-center rounded-xl bg-blue-100 text-blue-600 transition group-hover:scale-105 dark:bg-blue-900/30 dark:text-blue-400">
          <Users class="h-5 w-5" />
        </div>
        <h3 class="font-bold text-slate-900 dark:text-slate-100">Manage Users</h3>
        <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">View and manage all user accounts</p>
      </router-link>

      <router-link to="/admin/pending-doctors" class="group rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition-all duration-200 hover:shadow-md dark:border-slate-800 dark:bg-slate-900">
        <div class="mb-3 flex h-10 w-10 items-center justify-center rounded-xl bg-amber-100 text-amber-600 transition group-hover:scale-105 dark:bg-amber-900/30 dark:text-amber-400">
          <Clock class="h-5 w-5" />
        </div>
        <h3 class="font-bold text-slate-900 dark:text-slate-100">Pending Doctors</h3>
        <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">{{ pendingDoctors.length }} awaiting approval</p>
      </router-link>

      <router-link to="/admin/analytics" class="group rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition-all duration-200 hover:shadow-md dark:border-slate-800 dark:bg-slate-900">
        <div class="mb-3 flex h-10 w-10 items-center justify-center rounded-xl bg-purple-100 text-purple-600 transition group-hover:scale-105 dark:bg-purple-900/30 dark:text-purple-400">
          <Activity class="h-5 w-5" />
        </div>
        <h3 class="font-bold text-slate-900 dark:text-slate-100">Analytics</h3>
        <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">View system analytics and charts</p>
      </router-link>
    </div>

    <!-- Recent Users -->
    <div class="rounded-2xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <div class="border-b border-slate-200 px-6 py-4 dark:border-slate-800">
        <h3 class="text-lg font-bold text-slate-900 dark:text-slate-100">Recent Users</h3>
        <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">Latest registered users</p>
      </div>

      <div v-if="recentUsers.length === 0" class="p-6">
        <EmptyState title="No users found" description="No users have been registered yet." />
      </div>

      <div v-else class="divide-y divide-slate-100 dark:divide-slate-800">
        <div
          v-for="user in recentUsers" :key="user.id"
          class="flex items-center justify-between px-6 py-4 transition hover:bg-slate-50 dark:hover:bg-slate-800/50"
        >
          <div class="flex items-center gap-4">
            <div class="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-blue-500 to-indigo-500 text-xs font-bold text-white">
              {{ (getFullName(user).charAt(0) || "?").toUpperCase() }}
            </div>
            <div>
              <p class="font-semibold text-slate-900 dark:text-slate-100">{{ getFullName(user) }}</p>
              <p class="text-sm text-slate-500 dark:text-slate-400">{{ user.email }}</p>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <StatusBadge :status="user.is_active ? 'active' : 'inactive'" size="sm" />
            <span
              v-for="group in getUserGroups(user)" :key="group"
              class="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600 dark:bg-slate-800 dark:text-slate-300"
            >
              {{ group }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.toast-slide-enter-active, .toast-slide-leave-active { transition: all 0.25s ease; }
.toast-slide-enter-from, .toast-slide-leave-to { opacity: 0; transform: translateX(30px); }
</style>