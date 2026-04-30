<script setup>
import {computed, onMounted, onBeforeUnmount, ref} from "vue";
import { getAdminUsers, getPendingDoctors, approveDoctor } from "../../api/admin";
import StatusBadge from "../../components/StatusBadge.vue";
import SkeletonCard from "../../components/SkeletonCard.vue";
import EmptyState from "../../components/EmptyState.vue";

const pendingDoctors = ref([]);
const users = ref([]);
const loading = ref(false);
const approvingId = ref(null);
const errorMessage = ref("");
const successMessage = ref("");
const pendingCount = computed(()=> pendingDoctors.value.length);

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

function ApiErrorResponseFromBackend(error) {
  let data = null;

  if (error.response) {
    data = error.response.data;
  }

  if (!data) {
    return error.message || "Something went wrong. Please try again.";
  }

  if (data.detail) {
    return data.detail;
  }

  if (data.message) {
    return data.message;
  }

  if (Array.isArray(data.non_field_errors) && data.non_field_errors.length > 0) {
    return data.non_field_errors[0];
  }

  if (data.specialization) {
    return Array.isArray(data.specialization) ? data.specialization[0] : data.specialization;
  }

  if (data.consultationDuration) {
    return Array.isArray(data.consultationDuration) ? data.consultationDuration[0] : data.consultationDuration;
  }

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
    if (!doctorProfile) {
        return null;
    }
    
    const user = doctorProfile.user;
    
    if (!user) {
        return null;
    }
    
    // If user is already an object with user data
    if (typeof user === 'object' && (user.id || user.first_name || user.email)) {
        return user;
    }
    
    // If user is just an ID number, try to look it up
    if (typeof user === 'number') {
        return getUserById(user);
    }
    
    if (typeof user === "string") {
        return getUserById(Number(user));
    }
    
    return null;
}

function getDoctorName(doctorProfile) {
    const user = getDoctorUser(doctorProfile);

    if (!user) {
        return "Unknown doctor";
    }
    
    const firstName = user.first_name || "";
    const lastName = user.last_name || "";
    const fullName = (firstName + " " + lastName).trim();
    
    if (fullName) {
        return fullName;
    }
    
    if (user.email) {
        return user.email;
    }
    
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
    if (!doctorProfile || !doctorProfile.specialization) {
        return "—";
    }
    
    const spec = String(doctorProfile.specialization).trim();
    return spec || "—";
}

async function loadPendingDoctors() {
    loading.value = true;
    errorMessage.value = "";
    successMessage.value = "";

    try{
        const doctorsData = await getPendingDoctors();
        const usersData = await getAdminUsers();
        
        users.value = usersData;
        pendingDoctors.value = doctorsData;
    }catch (error) {
        console.log(error.response?.status);
        console.log(error.response?.data);
        errorMessage.value = ApiErrorResponseFromBackend(error);
        showToast(errorMessage.value, "error");
    }finally{
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
    } 
    catch(error) {
        console.log(error.response?.status);
        console.log(error.response?.data);
        errorMessage.value = ApiErrorResponseFromBackend(error);
        showToast(errorMessage.value, "error");
    } finally {
        approvingId.value = null;
    }
}
onMounted(() => {
  loadPendingDoctors();
});
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

    <!-- Header -->
    <div class="overflow-hidden rounded-2xl border border-white/50 bg-gradient-to-r from-blue-600 via-blue-600 to-cyan-500 p-8 shadow-lg backdrop-blur">
      <div class="flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
        <div>
          <p class="mb-2 text-sm font-semibold uppercase tracking-wide text-blue-100">
            ⚕️ Doctor Approval
          </p>

          <h2 class="mb-2 text-3xl font-bold text-white">
            Pending Doctors
          </h2>

          <p class="mt-2 max-w-2xl text-sm leading-6 text-blue-50">
            Review newly registered doctors and approve their accounts before they can access the system.
          </p>
        </div>

        <button
          type="button"
          @click="loadPendingDoctors"
          :disabled="loading"
          class="w-fit rounded-xl bg-white px-5 py-3 text-sm font-bold text-blue-700 shadow-md transition-all duration-200 hover:shadow-lg hover:scale-105 active:scale-95 disabled:cursor-not-allowed disabled:opacity-60 whitespace-nowrap"
        >
          {{ loading ? "⏳ Loading..." : "🔄 Refresh" }}
        </button>
      </div>
    </div>


    <!-- Summary Cards -->
    <div class="grid gap-6 md:grid-cols-3">
      <div class="group relative overflow-hidden rounded-2xl border border-white/50 bg-white/80 p-6 shadow-sm backdrop-blur transition-all duration-300 hover:-translate-y-1 hover:shadow-md">
        <div class="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-xl bg-amber-100 font-bold text-lg text-amber-700 transition-transform duration-300 group-hover:scale-110">
          ⏳
        </div>
        <span class="text-sm font-semibold text-gray-600">
          Pending Approval
        </span>
        <strong class="mt-3 block text-3xl font-bold text-gray-900">
          {{ pendingCount }}
        </strong>
      </div>

      <div class="group relative overflow-hidden rounded-2xl border border-white/50 bg-white/80 p-6 shadow-sm backdrop-blur transition-all duration-300 hover:-translate-y-1 hover:shadow-md">
        <div class="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-xl bg-blue-100 font-bold text-lg text-blue-700 transition-transform duration-300 group-hover:scale-110">
          👨‍💼
        </div>
        <span class="text-sm font-semibold text-gray-600">
          Required Permission
        </span>
        <strong class="mt-3 block text-3xl font-bold text-gray-900">
          Admin
        </strong>
      </div>

      <div class="group relative overflow-hidden rounded-2xl border border-white/50 bg-white/80 p-6 shadow-sm backdrop-blur transition-all duration-300 hover:-translate-y-1 hover:shadow-md">
        <div class="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-xl bg-green-100 font-bold text-lg text-green-700 transition-transform duration-300 group-hover:scale-110">
          ✅
        </div>
        <span class="text-sm font-semibold text-gray-600">
          After Approval
        </span>
        <strong class="mt-3 block text-3xl font-bold text-gray-900">
          Approved
        </strong>
      </div>
    </div>

    <!-- Table Card -->
    <div class="overflow-hidden rounded-2xl border border-white/50 bg-white/90 shadow-sm backdrop-blur">
      <div class="flex flex-col gap-3 border-b border-gray-200 px-6 py-5 md:flex-row md:items-center md:justify-between">
        <div>
          <h3 class="text-lg font-bold text-gray-900">
            Doctor Requests
          </h3>
          <p class="mt-1 text-sm text-gray-600">
            Doctors waiting for admin approval.
          </p>
        </div>

        <span class="w-fit rounded-full bg-amber-100 px-4 py-2 text-sm font-bold text-amber-800">
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
          icon="✅"
          title="No pending doctors"
          description="All doctor registration requests have already been reviewed. Great job!"
        />
      </div>

      <!-- Table -->
      <div v-else class="overflow-x-auto">
        <table class="w-full min-w-[1000px] border-collapse text-left">
          <thead>
            <tr class="border-b border-gray-200 bg-gradient-to-r from-slate-50 to-blue-50/50">
              <th class="px-6 py-4 font-bold text-gray-700">Doctor</th>
              <th class="px-6 py-4 font-bold text-gray-700">Contact</th>
              <th class="px-6 py-4 font-bold text-gray-700">Specialization</th>
              <th class="px-6 py-4 font-bold text-gray-700">Duration</th>
              <th class="px-6 py-4 font-bold text-gray-700">Status</th>
              <th class="w-48 px-6 py-4 font-bold text-gray-700">Action</th>
            </tr>
          </thead>

          <tbody>
            <tr
              v-for="(doctor, index) in pendingDoctors"
              :key="doctor.id"
              class="group border-b border-gray-100 transition-all duration-200 hover:bg-blue-50/50"
              :style="{ animationDelay: `${index * 50}ms` }"
            >
              <td class="px-6 py-5">
                <div class="flex items-center gap-4">
                  <div class="flex h-11 w-11 items-center justify-center rounded-lg bg-gradient-to-br from-blue-400 to-cyan-500 font-bold text-white text-sm">
                    {{ (getDoctorName(doctor).split(' ')[0]?.[0] || 'D') + (getDoctorName(doctor).split(' ')[1]?.[0] || '') }}
                  </div>

                  <div class="flex flex-col gap-1">
                    <strong class="font-bold text-gray-900">
                      {{ getDoctorName(doctor) }}
                    </strong>

                    <span class="text-xs font-medium text-gray-500">
                      ID: {{ doctor.id }}
                    </span>
                  </div>
                </div>
              </td>

              <td class="px-6 py-5">
                <div class="flex flex-col gap-1">
                  <span class="font-semibold text-gray-800">
                    {{ getDoctorEmail(doctor) }}
                  </span>

                  <small class="text-sm text-gray-600">
                    {{ getDoctorPhone(doctor) }}
                  </small>
                </div>
              </td>

              <td class="px-6 py-5">
                <span class="font-medium text-gray-800">
                  {{ getDoctorSpecialization(doctor) }}
                </span>
              </td>

              <td class="px-6 py-5">
                <span class="inline-flex rounded-full bg-slate-100 px-3 py-1.5 text-xs font-bold text-slate-700">
                  ⏱️ {{ doctor.consultationDuration }} min
                </span>
              </td>

              <td class="px-6 py-5">
                <StatusBadge status="pending" size="sm" />
              </td>

              <td class="px-6 py-5">
                <button
                  type="button"
                  @click="handleApproveDoctor(doctor)"
                  :disabled="approvingId === doctor.id"
                  class="rounded-lg bg-gradient-to-r from-green-600 to-emerald-500 px-4 py-2.5 text-xs font-bold text-white shadow-md transition-all duration-200 hover:shadow-lg hover:scale-105 active:scale-95 disabled:opacity-60 disabled:cursor-not-allowed whitespace-nowrap"
                >
                  {{ approvingId === doctor.id ? "⏳ Approving..." : "✅ Approve" }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<style scoped>
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