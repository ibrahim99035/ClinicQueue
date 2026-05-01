<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { loginUser, saveAuthData, clearAuthData } from "../../api/auth";
import useToast from "../../composables/useToast";

const router = useRouter();
const { showToast } = useToast();
const email = ref("");
const password = ref("");
const loading = ref(false);

async function handleLoginOfUser(event) {
  event?.preventDefault?.();
  event?.stopPropagation?.();

  if (!email.value) {
    showToast("Please enter your email.", "error");
    return;
  }

  if (!password.value) {
    showToast("Please enter your password.", "error");
    return;
  }

  loading.value = true;

  try {
    const response = await loginUser({
      email: email.value,
      password: password.value,
    });

    const data = response.data;

    saveAuthData(data);

    const userRoles = data.roles || [];

    if (userRoles.includes("Admins")) {
      router.push("/admin");
      return;
    }

    if (userRoles.includes("Doctors")) {
      router.push("/doctor");
      return;
    }

    if (userRoles.includes("Patients")) {
      router.push("/patient");
      return;
    }

    if (userRoles.includes("Receptionists")) {
      router.push("/receptionist");
      return;
    }

    clearAuthData();
    showToast("No valid role assigned to this account.", "error");
  } catch (error) {
    clearAuthData();

    let message = "Login failed. Please check your email and password.";

    const detail = error.response?.data?.detail;

    if (detail) {
      message = detail;
    }

    if (detail?.includes("No active account")) {
      message = "Your doctor account is pending admin approval.";
    }

    showToast(message, "error");
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-100 p-5">
    <div class="w-full max-w-[420px] bg-white rounded-2xl p-8 shadow-[0_10px_30px_rgba(0,0,0,0.08)]">
      <h1 class="m-0 text-3xl font-bold text-gray-800">
        Clinic Login
      </h1>

      <p class="mt-2 mb-6 text-gray-500">
        Clinic Appointment System Dashboard
      </p>

      <form @submit.prevent.stop novalidate>
        <div class="mb-5">
          <label class="mb-1.5 block font-semibold text-gray-700">
            Email
          </label>

          <input
            v-model="email"
            type="email"
            placeholder="Enter admin email"
            autocomplete="email"
            class="w-full box-border rounded-xl border border-gray-300 px-3.5 py-3 text-[15px] focus:border-blue-600 focus:outline-none"
          />
        </div>

        <div class="mb-5">
          <label class="mb-1.5 block font-semibold text-gray-700">
            Password
          </label>

          <input
            v-model="password"
            type="password"
            placeholder="Enter password"
            autocomplete="current-password"
            class="w-full box-border rounded-xl border border-gray-300 px-3.5 py-3 text-[15px] focus:border-blue-600 focus:outline-none"
          />
        </div>

         <button
          type="button"
          :disabled="loading"
          @click="handleLoginOfUser"
          class="w-full cursor-pointer rounded-xl border-none bg-blue-600 px-3.5 py-3 text-base font-semibold text-white disabled:cursor-not-allowed disabled:bg-blue-300"
        >
          {{ loading ? "Logging in..." : "Login" }}
        </button>
        <p class="text-sm text-slate-600 text-center mt-4">
  Don't have an account?
  <RouterLink to="/register" class="text-blue-600 font-semibold hover:underline">
    Create account
  </RouterLink>
</p>
      </form>
    </div>
  </div>
</template>
