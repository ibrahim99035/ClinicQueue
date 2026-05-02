<script setup>
import {computed, onMounted, onBeforeUnmount, ref} from "vue";
import { getAdminUsers, getPendingDoctors, approveDoctor } from "../../api/admin";
import StatusBadge from "../../components/StatusBadge.vue";
import SkeletonCard from "../../components/SkeletonCard.vue";
import EmptyState from "../../components/EmptyState.vue";
import BaseTable from "../../components/ui/BaseTable.vue";
import BaseButton from "../../components/ui/BaseButton.vue";
import { Clock, Shield, CheckCircle, RefreshCcw, Timer, Inbox } from "lucide-vue-next";

const pendingDoctors = ref([]);
const users = ref([]);
const loading = ref(false);
const approvingId = ref(null);
const errorMessage = ref("");
const successMessage = ref("");
const pendingCount = computed(()=> pendingDoctors.value.length);

const toast = ref({ show: false, type: "success", message: "" });
let toastTimer = null;

function showToast(message, type) {
  toast.value = { show: true, type, message };
  if (toastTimer) clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { toast.value.show = false; }, 30000);
}

function closeToast() {
  toast.value.show = false;
  if (toastTimer) clearTimeout(toastTimer);
}

onBeforeUnmount(() => { if (toastTimer) clearTimeout(toastTimer); });

function ApiErrorResponseFromBackend(error) {
  let data = null;
  if (error.response) data = error.response.data;
  if (!data) return error.message || "Something went wrong. Please try again.";
  if (data.detail) return data.detail;
  if (data.message) return data.message;
  if (Array.isArray(data.non_field_errors) && data.non_field_errors.length > 0) return data.non_field_errors[0];
  if (data.specialization) return Array.isArray(data.specialization) ? data.specialization[0] : data.specialization;
  if (data.consultationDuration) return Array.isArray(data.consultationDuration) ? data.consultationDuration[0] : data.consultationDuration;
  const firstError = Object.keys(data).find(key => data[key]);
  if (firstError) {
    const errorValue = data[firstError];
    return Array.isArray(errorValue) ? errorValue[0] : errorValue;
  }
  return "Please check the form data.";
}

function getUserById(userId) {
  return users.value.find((user)=> user.id === userId) || null;
}

function getDoctorUser(doctorProfile) {
  if (!doctorProfile) return null;
  const user = doctorProfile.user;
  if (!user) return null;
  if (typeof user === 'object' && (user.id || user.first_name || user.email)) return user;
  if (typeof user === 'number') return getUserById(user);
  if (typeof user === "string") return getUserById(Number(user));
  return null;
}

function getDoctorName(doctorProfile) {
  const user = getDoctorUser(doctorProfile);
  if (!user) return "Unknown doctor";
  const firstName = user.first_name || "";
  const lastName = user.last_name || "";
  const fullName = (firstName + " " + lastName).trim();
  if (fullName) return fullName;
  if (user.email) return user.email;
  return "Unknown doctor";
}

function getDoctorEmail(doctorProfile) {
  const user = getDoctorUser(doctorProfile);
  return user && user.email ? user.email : "-";
}

function getDoctorPhone(doctorProfile) {
  const user = getDoctorUser(doctorProfile);
  return user && user.phone ? user.phone : "-";
}

function getDoctorSpecialization(doctorProfile) {
  if (!doctorProfile || !doctorProfile.specialization) return "—";
  const spec = String(doctorProfile.specialization).trim();
  return spec || "—";
}

async function loadPendingDoctors() {
  loading.value = true;
  errorMessage.value = "";
  successMessage.value = "";
  try {
    const doctorsData = await getPendingDoctors();
    const usersData = await getAdminUsers();
    users.value = usersData;
    pendingDoctors.value = doctorsData;
  } catch (error) {
    errorMessage.value = ApiErrorResponseFromBackend(error);
    showToast(errorMessage.value, "error");
  } finally {
    loading.value = false;
  }
}

async function handleApproveDoctor(doctorProfile) {
  errorMessage.value = "";
  successMessage.value = "";
  approvingId.value = doctorProfile.id;
  try {
    await approveDoctor(doctorProfile.id);
    const doctorName = getDoctorName(doctorProfile);
    successMessage.value = doctorName + " approved successfully.";
    showToast(successMessage.value, "success");
    await loadPendingDoctors();
  } catch(error) {
    errorMessage.value = ApiErrorResponseFromBackend(error);
    showToast(errorMessage.value, "error");
  } finally {
    approvingId.value = null;
  }
}

onMounted(() => { loadPendingDoctors(); });
</script>

<template>
  <div class="flex flex-col gap-8">
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

    <!-- Header -->
    <div class="overflow-hidden rounded-2xl border border-slate-200 bg-gradient-to-r from-blue-600 via-blue-600 to-cyan-500 p-8 shadow-sm dark:border-slate-700">
      <div class="flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
        <div>
          <p class="mb-2 text-sm font-semibold uppercase tracking-wide text-blue-200">Doctor Approval</p>
          <h2 class="mb-2 text-3xl font-bold text-white">Pending Doctors</h2>
          <p class="mt-2 max-w-2xl text-sm leading-6 text-blue-50">
            Review newly registered doctors and approve their accounts before they can access the system.
          </p>
        </div>
        <button
          @click="loadPendingDoctors" :disabled="loading"
          class="flex w-fit items-center gap-2 rounded-xl bg-white px-5 py-3 text-sm font-bold text-blue-700 shadow-md transition-all duration-200 hover:shadow-lg hover:scale-105 active:scale-95 disabled:cursor-not-allowed disabled:opacity-60 whitespace-nowrap"
        >
          <RefreshCcw class="h-4 w-4" :class="{ 'animate-spin': loading }" />
          {{ loading ? "Loading..." : "Refresh" }}
        </button>
      </div>
    </div>

    <!-- Summary Cards -->
    <div class="grid gap-6 md:grid-cols-3">
      <div class="group relative overflow-hidden rounded-2xl border border-slate-200 bg-white p-6 shadow-sm transition-all duration-300 hover:-translate-y-1 hover:shadow-md dark:border-slate-800 dark:bg-slate-900">
        <div class="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-xl bg-amber-100 text-amber-700 transition-transform duration-300 group-hover:scale-110 dark:bg-amber-900/30 dark:text-amber-400">
          <Clock class="h-6 w-6" />
        </div>
        <span class="text-sm font-semibold text-slate-500 dark:text-slate-400">Pending Approval</span>
        <strong class="mt-3 block text-3xl font-bold text-slate-900 dark:text-slate-100">{{ pendingCount }}</strong>
      </div>

      <div class="group relative overflow-hidden rounded-2xl border border-slate-200 bg-white p-6 shadow-sm transition-all duration-300 hover:-translate-y-1 hover:shadow-md dark:border-slate-800 dark:bg-slate-900">
        <div class="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-xl bg-blue-100 text-blue-700 transition-transform duration-300 group-hover:scale-110 dark:bg-blue-900/30 dark:text-blue-400">
          <Shield class="h-6 w-6" />
        </div>
        <span class="text-sm font-semibold text-slate-500 dark:text-slate-400">Required Permission</span>
        <strong class="mt-3 block text-3xl font-bold text-slate-900 dark:text-slate-100">Admin</strong>
      </div>

      <div class="group relative overflow-hidden rounded-2xl border border-slate-200 bg-white p-6 shadow-sm transition-all duration-300 hover:-translate-y-1 hover:shadow-md dark:border-slate-800 dark:bg-slate-900">
        <div class="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-xl bg-green-100 text-green-700 transition-transform duration-300 group-hover:scale-110 dark:bg-green-900/30 dark:text-green-400">
          <CheckCircle class="h-6 w-6" />
        </div>
        <span class="text-sm font-semibold text-slate-500 dark:text-slate-400">After Approval</span>
        <strong class="mt-3 block text-3xl font-bold text-slate-900 dark:text-slate-100">Approved</strong>
      </div>
    </div>

    <!-- Table Card -->
    <div class="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <div class="flex flex-col gap-3 border-b border-slate-200 px-6 py-5 md:flex-row md:items-center md:justify-between dark:border-slate-800">
        <div>
          <h3 class="text-lg font-bold text-slate-900 dark:text-slate-100">Doctor Requests</h3>
          <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">Doctors waiting for admin approval.</p>
        </div>
        <span class="w-fit rounded-full bg-amber-100 px-4 py-2 text-sm font-bold text-amber-800 dark:bg-amber-900/30 dark:text-amber-300">
          {{ pendingCount }} pending doctor(s)
        </span>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="p-6">
        <SkeletonCard type="row" :count="3" />
      </div>

      <!-- Empty State -->
      <div v-else-if="pendingDoctors.length === 0" class="p-6">
        <EmptyState
          title="No pending doctors"
          description="All doctor registration requests have already been reviewed. Great job!"
        >
          <template #icon><Inbox class="h-7 w-7" /></template>
        </EmptyState>
      </div>

      <BaseTable :items="pendingDoctors" :loading="loading" title="Doctor Requests" table-class="min-w-[1000px]">
        <template #toolbar>
          <span class="w-fit rounded-full bg-amber-100 px-4 py-2 text-sm font-bold text-amber-800 dark:bg-amber-900/30 dark:text-amber-300">{{ pendingCount }} pending doctor(s)</span>
        </template>

        <template #thead>
          <th class="px-6 py-4 font-bold text-slate-700 dark:text-slate-300">Doctor</th>
          <th class="px-6 py-4 font-bold text-slate-700 dark:text-slate-300">Contact</th>
          <th class="px-6 py-4 font-bold text-slate-700 dark:text-slate-300">Specialization</th>
          <th class="px-6 py-4 font-bold text-slate-700 dark:text-slate-300">Duration</th>
          <th class="px-6 py-4 font-bold text-slate-700 dark:text-slate-300">Status</th>
          <th class="w-48 px-6 py-4 font-bold text-slate-700 dark:text-slate-300">Action</th>
        </template>

        <template #tbody="{ items }">
          <tr v-for="(doctor, index) in items" :key="doctor.id" class="group border-b border-slate-100 transition-all duration-200 hover:bg-blue-50/50 dark:border-slate-800 dark:hover:bg-slate-800/50" :style="{ animationDelay: `${index * 50}ms` }">
            <td class="px-6 py-5">
              <div class="flex items-center gap-4">
                <div class="flex h-11 w-11 items-center justify-center rounded-lg bg-gradient-to-br from-blue-400 to-cyan-500 font-bold text-white text-sm">{{ (getDoctorName(doctor).split(' ')[0]?.[0] || 'D') + (getDoctorName(doctor).split(' ')[1]?.[0] || '') }}</div>
                <div class="flex flex-col gap-1">
                  <strong class="font-bold text-slate-900 dark:text-slate-100">{{ getDoctorName(doctor) }}</strong>
                  <span class="text-xs font-medium text-slate-500 dark:text-slate-400">ID: {{ doctor.id }}</span>
                </div>
              </div>
            </td>
            <td class="px-6 py-5">
              <div class="flex flex-col gap-1">
                <span class="font-semibold text-slate-800 dark:text-slate-200">{{ getDoctorEmail(doctor) }}</span>
                <small class="text-sm text-slate-500 dark:text-slate-400">{{ getDoctorPhone(doctor) }}</small>
              </div>
            </td>
            <td class="px-6 py-5"><span class="font-medium text-slate-800 dark:text-slate-200">{{ getDoctorSpecialization(doctor) }}</span></td>
            <td class="px-6 py-5">
              <span class="inline-flex items-center gap-1.5 rounded-full bg-slate-100 px-3 py-1.5 text-xs font-bold text-slate-700 dark:bg-slate-800 dark:text-slate-300">
                <Timer class="h-3.5 w-3.5" /> {{ doctor.consultationDuration }} min
              </span>
            </td>
            <td class="px-6 py-5"><StatusBadge status="pending" size="sm" /></td>
            <td class="px-6 py-5">
              <BaseButton size="sm" variant="success" :loading="approvingId === doctor.id" @click="handleApproveDoctor(doctor)">
                {{ approvingId === doctor.id ? 'Approving...' : 'Approve' }}
              </BaseButton>
            </td>
          </tr>
        </template>
      </BaseTable>
    </div>
  </div>
</template>

<style scoped>
.toast-slide-enter-active, .toast-slide-leave-active { transition: all 0.25s ease; }
.toast-slide-enter-from, .toast-slide-leave-to { opacity: 0; transform: translateX(30px); }
</style>