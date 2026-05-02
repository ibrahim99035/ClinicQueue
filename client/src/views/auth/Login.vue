<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { loginUser, saveAuthData, clearAuthData } from "../../api/auth";
import useToast from "../../composables/useToast";
import useTheme from "../../composables/useTheme";
import { Sun, Moon, ArrowRight } from "lucide-vue-next";

const router = useRouter();
const { showToast } = useToast();
const { isDark, toggleTheme } = useTheme();
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
      router.push("/reception");
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
  <div class="relative min-h-screen overflow-hidden bg-slate-50 text-slate-900 dark:bg-slate-950 dark:text-slate-100">
    <!-- Theme toggle -->
    <button
      @click="toggleTheme"
      class="fixed right-6 top-6 z-10 flex h-9 w-9 items-center justify-center rounded-lg border border-slate-200 bg-white text-slate-500 shadow-sm transition hover:bg-slate-100 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-400 dark:hover:bg-slate-800"
    >
      <Moon v-if="!isDark" class="h-5 w-5" />
      <Sun v-else class="h-5 w-5" />
    </button>

    <!-- Background accents -->
    <div class="pointer-events-none absolute inset-0">
      <div class="absolute -left-24 top-0 h-80 w-80 rounded-full bg-blue-200/30 blur-3xl dark:bg-blue-900/20"></div>
      <div class="absolute right-0 top-1/3 h-96 w-96 rounded-full bg-indigo-100/30 blur-3xl dark:bg-indigo-950/20"></div>
    </div>

    <div class="relative mx-auto flex min-h-screen w-full max-w-7xl items-center px-6 py-8 md:px-12">
      <div class="grid w-full overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900 lg:grid-cols-2">
        <!-- Left panel -->
        <section class="hidden lg:flex lg:flex-col lg:justify-between lg:p-12">
          <div>
            <p class="inline-flex items-center gap-2 rounded-lg bg-blue-100 px-4 py-1.5 text-xs font-bold uppercase tracking-wide text-blue-700 dark:bg-blue-900/30 dark:text-blue-300">
              Smart Clinic Queue
            </p>
            <h1 class="mt-6 text-5xl font-bold leading-tight tracking-tight text-slate-900 dark:text-slate-100">
              Your Clinic,
              <span class="text-blue-600 dark:text-blue-400">Always In Flow</span>
            </h1>
            <p class="mt-5 max-w-lg text-sm text-slate-500 dark:text-slate-400">
              Manage appointments, schedules, and patient journeys from one control center designed for real-world front desks and care teams.
            </p>
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div class="rounded-xl border border-slate-200 bg-slate-50 p-4 dark:border-slate-800 dark:bg-slate-800">
              <p class="text-xs font-bold uppercase tracking-wide text-slate-500 dark:text-slate-400">Scheduling</p>
              <p class="mt-2 text-sm text-slate-900 dark:text-slate-100">Automated slot generation and conflict-safe booking windows.</p>
            </div>
            <div class="rounded-xl border border-slate-200 bg-slate-50 p-4 dark:border-slate-800 dark:bg-slate-800">
              <p class="text-xs font-bold uppercase tracking-wide text-slate-500 dark:text-slate-400">Consultations</p>
              <p class="mt-2 text-sm text-slate-900 dark:text-slate-100">Fast EMR workflow for notes, prescriptions, and follow-ups.</p>
            </div>
          </div>
        </section>

        <!-- Right panel (login form) -->
        <section class="p-6 sm:p-8 lg:p-12">
          <div class="mx-auto w-full max-w-md">
            <div class="mb-8">
              <p class="text-xs font-bold uppercase tracking-wide text-blue-600 dark:text-blue-400">Welcome Back</p>
              <h2 class="mt-2 text-3xl font-bold leading-tight tracking-tight text-slate-900 dark:text-slate-100 sm:text-4xl">Sign In</h2>
              <p class="mt-3 text-sm text-slate-500 dark:text-slate-400">Use your clinic account to access role-based dashboards and workflows.</p>
            </div>

            <form @submit.prevent="handleLoginOfUser" novalidate class="space-y-5">
              <div>
                <label for="email" class="mb-1.5 block text-xs font-bold uppercase tracking-wide text-slate-500 dark:text-slate-400">Email Address</label>
                <input
                  id="email"
                  v-model="email"
                  type="email"
                  placeholder="name@clinic.com"
                  autocomplete="email"
                  class="w-full rounded-xl border border-slate-300 bg-white px-3 py-2.5 text-sm text-slate-900 placeholder:text-slate-400 outline-none transition-all duration-150 focus:border-blue-500 focus:ring-2 focus:ring-blue-100 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100 dark:placeholder:text-slate-500 dark:focus:ring-blue-900/30"
                />
              </div>

              <div>
                <label for="password" class="mb-1.5 block text-xs font-bold uppercase tracking-wide text-slate-500 dark:text-slate-400">Password</label>
                <input
                  id="password"
                  v-model="password"
                  type="password"
                  placeholder="Enter your password"
                  autocomplete="current-password"
                  class="w-full rounded-xl border border-slate-300 bg-white px-3 py-2.5 text-sm text-slate-900 placeholder:text-slate-400 outline-none transition-all duration-150 focus:border-blue-500 focus:ring-2 focus:ring-blue-100 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100 dark:placeholder:text-slate-500 dark:focus:ring-blue-900/30"
                />
              </div>

              <button
                type="submit"
                :disabled="loading"
                class="group inline-flex w-full items-center justify-center gap-2 rounded-xl bg-blue-600 px-4 py-3 text-sm font-bold text-white transition-all duration-150 cursor-pointer hover:bg-blue-700 hover:-translate-y-px disabled:cursor-not-allowed disabled:opacity-60"
              >
                <span>{{ loading ? "Signing In..." : "Enter Dashboard" }}</span>
                <ArrowRight class="h-4 w-4 transition group-hover:translate-x-0.5" />
              </button>

              <p class="pt-1 text-center text-sm text-slate-500 dark:text-slate-400">
                New here?
                <RouterLink to="/register" class="font-semibold text-blue-600 transition-all duration-150 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300">
                  Create account
                </RouterLink>
              </p>
            </form>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>
