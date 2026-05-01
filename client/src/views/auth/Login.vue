<script setup>
import { ref } from "vue"
import { useRouter } from "vue-router"
import { loginUser, saveAuthData, clearAuthData } from "../../api/auth";

const router = useRouter();
const email = ref("");
const password = ref("");
const loading = ref(false);
const errorMessage = ref("")

async function handleLoginOfUser() {
    errorMessage.value = "";
    
if (!email.value) {
  errorMessage.value = "Please enter your email.";
  return;
    }

if (!password.value) {
  errorMessage.value = "Please enter your password.";
  return;
}

loading.value = true;
try{
const response = await loginUser({
    email: email.value,
    password: password.value,
});

const data = response.data;

const roles = data.roles || [];
saveAuthData(data);

if (roles.includes("Admins")) {
  router.push("/admin");
} else if (roles.includes("Doctors")) {
  router.push("/doctor");
} else if (roles.includes("Receptionists")) {
  router.push("/receptionist");
} else if (roles.includes("Patients")) {
  router.push("/patient");
} else {
  clearAuthData();
  errorMessage.value = "No valid role assigned to this account.";
}
} catch(error) {
    clearAuthData();
    errorMessage.value = "Login failed. Please check your email and password.";
    if (error.response && error.response.data && error.response.data.detail) {
        errorMessage.value = error.response.data.detail;
    }
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

      <form @submit.prevent="handleLoginOfUser">
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

        <p
          v-if="errorMessage"
          class="mb-4 rounded-lg bg-red-100 p-2.5 text-sm text-red-600"
        >
          {{ errorMessage }}
        </p>

        <button
          type="submit"
          :disabled="loading"
          class="w-full cursor-pointer rounded-xl border-none bg-blue-600 px-3.5 py-3 text-base font-semibold text-white disabled:cursor-not-allowed disabled:bg-blue-300"
        >
          {{ loading ? "Logging in..." : "Login" }}
        </button>
      </form>
    </div>
  </div>
</template>