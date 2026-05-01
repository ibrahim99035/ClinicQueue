<script setup>
import { useRouter } from "vue-router";
import { clearAuthData } from "../../api/auth";
import { computed, onMounted, onBeforeUnmount, ref } from "vue";
import { getAdminOverview } from "../../api/analytics";
import StatCard from "../../components/StatCard.vue";
import SkeletonCard from "../../components/SkeletonCard.vue";
import EmptyState from "../../components/EmptyState.vue";
import BaseButton from "../../components/ui/BaseButton.vue";

const router = useRouter();
const user = JSON.parse(localStorage.getItem("user")|| "{}");
const adminOverview = ref(null);
const loading = ref(false);
const errorMessage = ref("");

const toast = ref({
  show: false,
  type: "success",
  message: "",
});

let toastTimer = null;

function showToast(message, type) {
  toast.value = {
    show: true,
    type: type,
    message: message,
  };

  if (toastTimer) {
    clearTimeout(toastTimer);
  }

  toastTimer = setTimeout(() => {
    toast.value.show = false;
  }, 30000);
}

function closeToast() {
  toast.value.show = false;

  if (toastTimer) {
    clearTimeout(toastTimer);
  }
}

onBeforeUnmount(() => {
  if (toastTimer) {
    clearTimeout(toastTimer);
  }
});

const totalUsers = computed(() => adminOverview.value?.users?.total ?? 0);
const totalPatients = computed(() => adminOverview.value?.users?.patients ?? 0);
const totalDoctors = computed(() => adminOverview.value?.users?.doctors ?? 0);
const totalReceptionists = computed(() => adminOverview.value?.users?.receptionists ?? 0);
const totalAdmins = computed(() => adminOverview.value?.users?.admins ?? 0);
const activeUsers = computed(() => adminOverview.value?.users?.active ?? 0);
const inactiveUsers = computed(() => adminOverview.value?.users?.inactive ?? 0);
const pendingDoctorCount = computed(() => adminOverview.value?.doctors?.pending ?? 0);

async function fetchDashboardData() {
  loading.value = true;
  errorMessage.value = "";
  try {
    adminOverview.value = await getAdminOverview();
  } catch (error) {
    adminOverview.value = null;
    if (error.response?.status === 401) {
      errorMessage.value = "You are not authenticated. Please login again.";
      showToast(errorMessage.value, "error");
    } else if (error.response?.status === 403) {
      errorMessage.value = "You do not have permission to view dashboard data.";
      showToast(errorMessage.value, "error");
    } else {
      errorMessage.value = "Failed to load dashboard data.";
      showToast(errorMessage.value, "error");
    }
  } finally {
    loading.value = false;
  }
}

onMounted(async () => {
  await fetchDashboardData();
});

function logout() {
    clearAuthData();
    router.push("/login")
}
</script>

<template>
  <div class="flex flex-col gap-8">
    <!-- Toast Notification -->
    <Transition name="toast-slide">
      <div
        v-if="toast.show"
        class="fixed right-6 top-6 z-50 w-full max-w-sm rounded-2xl border p-4 shadow-2xl"
        :class="
          toast.type === 'success'
            ? 'border-green-200 bg-green-50 text-green-800'
            : 'border-red-200 bg-red-50 text-red-800'
        "
      >
        <div class="flex items-start justify-between gap-4">
          <div>
            <p class="text-sm font-bold">
              {{ toast.type === "success" ? "Success" : "Error" }}
            </p>

            <p class="mt-1 text-sm leading-6">
              {{ toast.message }}
            </p>
          </div>

          <button
            type="button"
            @click="closeToast"
            class="rounded-lg px-2 py-1 text-sm font-bold hover:bg-black/5"
          >
            ×
          </button>
        </div>
      </div>
    </Transition>

    <!-- Welcome Hero Card -->
    <div class="group relative overflow-hidden rounded-3xl border border-white/50 bg-gradient-to-br from-white/80 via-blue-50/80 to-cyan-50/80 p-8 shadow-lg backdrop-blur transition-all duration-300 hover:shadow-xl">
      <div class="absolute inset-0 -z-10 opacity-0 transition-opacity duration-300 group-hover:opacity-10">
        <div class="absolute -right-32 -top-32 h-64 w-64 rounded-full bg-blue-400 blur-3xl"></div>
      </div>

      <div class="flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
        <div>
          <h2 class="mb-3 text-3xl font-bold text-gray-900">
            Welcome back, {{ user.first_name || "Admin" }} 👋
          </h2>

          <p class="max-w-2xl text-base leading-7 text-gray-700">
            This dashboard provides a quick overview of your clinic's system. Monitor users, pending doctor approvals, and system status in real-time.
          </p>
        </div>

        <BaseButton variant="primary" :loading="loading" @click="fetchDashboardData">
          <span v-if="!loading">🔄 Refresh</span>
          <span v-else>Loading...</span>
        </BaseButton>
      </div>
    </div>

    <!-- Error Message -->
    <transition name="fade">
      <div
        v-if="errorMessage"
        class="rounded-2xl border border-red-200 bg-red-50/80 px-6 py-4 text-sm font-semibold text-red-700 shadow-sm backdrop-blur"
      >
        ⚠️ {{ errorMessage }}
      </div>
    </transition>

    <!-- Loading Skeleton -->
    <div v-if="loading" class="space-y-6">
      <SkeletonCard type="card" :count="2" />
      <SkeletonCard type="card" :count="3" />
    </div>

    <!-- Stats Grid -->
    <div v-else class="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-4">
      <div class="animate-fade-in" style="animation-delay: 0ms">
        <StatCard label="Total Users" :value="totalUsers" icon="👥" color="blue" />
      </div>
      <div class="animate-fade-in" style="animation-delay: 100ms">
        <StatCard label="Patients" :value="totalPatients" icon="🩺" color="green" />
      </div>
      <div class="animate-fade-in" style="animation-delay: 200ms">
        <StatCard label="Doctors" :value="totalDoctors" icon="⚕️" color="cyan" />
      </div>
      <div class="animate-fade-in" style="animation-delay: 300ms">
        <StatCard label="Receptionists" :value="totalReceptionists" icon="📞" color="amber" />
      </div>
      <div class="animate-fade-in" style="animation-delay: 400ms">
        <StatCard label="Admins" :value="totalAdmins" icon="👨‍💼" color="purple" />
      </div>
      <div class="animate-fade-in" style="animation-delay: 500ms">
        <StatCard label="Active Users" :value="activeUsers" icon="✅" color="green" />
      </div>
      <div class="animate-fade-in" style="animation-delay: 600ms">
        <StatCard label="Inactive Users" :value="inactiveUsers" icon="⏸️" color="red" />
      </div>
      <div class="animate-fade-in" style="animation-delay: 700ms">
        <StatCard label="Pending Doctors" :value="pendingDoctorCount" icon="⏳" color="amber" />
      </div>
    </div>

    <!-- Quick Links Section -->
    <div v-if="!loading" class="space-y-4">
      <h3 class="text-lg font-bold text-gray-900">
        Quick Access
      </h3>
      
      <div class="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
        <RouterLink
          to="/admin/users"
          class="group flex items-center gap-4 overflow-hidden rounded-2xl border border-white/50 bg-white/80 p-6 shadow-sm backdrop-blur transition-all duration-300 hover:-translate-y-1 hover:shadow-md hover:bg-white"
        >
          <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-blue-100 text-xl transition-transform duration-300 group-hover:scale-110">
            👥
          </div>
          <div>
            <h4 class="font-bold text-gray-900">Users</h4>
            <p class="text-sm text-gray-600">Manage users</p>
          </div>
          <span class="ml-auto text-2xl transition-transform duration-300 group-hover:translate-x-2">→</span>
        </RouterLink>

        <RouterLink
          to="/admin/pending-doctors"
          class="group flex items-center gap-4 overflow-hidden rounded-2xl border border-white/50 bg-white/80 p-6 shadow-sm backdrop-blur transition-all duration-300 hover:-translate-y-1 hover:shadow-md hover:bg-white"
        >
          <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-amber-100 text-xl transition-transform duration-300 group-hover:scale-110">
            ⚕️
          </div>
          <div>
            <h4 class="font-bold text-gray-900">Doctor Approval</h4>
            <p class="text-sm text-gray-600">Pending requests</p>
          </div>
          <span class="ml-auto text-2xl transition-transform duration-300 group-hover:translate-x-2">→</span>
        </RouterLink>

        <RouterLink
          to="/admin/scheduling"
          class="group flex items-center gap-4 overflow-hidden rounded-2xl border border-white/50 bg-white/80 p-6 shadow-sm backdrop-blur transition-all duration-300 hover:-translate-y-1 hover:shadow-md hover:bg-white"
        >
          <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-green-100 text-xl transition-transform duration-300 group-hover:scale-110">
            📅
          </div>
          <div>
            <h4 class="font-bold text-gray-900">Scheduling</h4>
            <p class="text-sm text-gray-600">Manage schedules</p>
          </div>
          <span class="ml-auto text-2xl transition-transform duration-300 group-hover:translate-x-2">→</span>
        </RouterLink>

        <RouterLink
          to="/admin/appointments"
          class="group flex items-center gap-4 overflow-hidden rounded-2xl border border-white/50 bg-white/80 p-6 shadow-sm backdrop-blur transition-all duration-300 hover:-translate-y-1 hover:shadow-md hover:bg-white"
        >
          <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-cyan-100 text-xl transition-transform duration-300 group-hover:scale-110">
            📋
          </div>
          <div>
            <h4 class="font-bold text-gray-900">Appointments</h4>
            <p class="text-sm text-gray-600">View & manage</p>
          </div>
          <span class="ml-auto text-2xl transition-transform duration-300 group-hover:translate-x-2">→</span>
        </RouterLink>
      </div>
    </div>
  </div>
</template>

<style scoped>
@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in {
  animation: fade-in 0.6s ease-out forwards;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.toast-slide-enter-active,
.toast-slide-leave-active {
  transition: all 0.25s ease;
}

.toast-slide-enter-from,
.toast-slide-leave-to {
  opacity: 0;
  transform: translateX(30px);
}
</style>