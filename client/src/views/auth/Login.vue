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
  <div class="relative min-h-screen overflow-hidden bg-bg text-text1 font-sans">
    <div class="pointer-events-none absolute inset-0">
      <div class="absolute -left-24 top-0 h-80 w-80 rounded-full bg-accent/10 blur-3xl"></div>
      <div class="absolute right-0 top-1/3 h-96 w-96 rounded-full bg-surface2 blur-3xl"></div>
      <div class="absolute bottom-0 left-1/3 h-80 w-80 rounded-full bg-border blur-3xl"></div>
    </div>

    <div class="relative mx-auto flex min-h-screen w-full max-w-7xl items-center px-6 py-8 md:px-12">
      <div class="grid w-full overflow-hidden rounded border border-border bg-surface lg:grid-cols-2">
        <section class="hidden lg:flex lg:flex-col lg:justify-between lg:p-12">
          <div>
            <p class="inline-flex items-center gap-2 rounded border border-accent/40 bg-surface2 px-4 py-1.5 font-mono text-[11px] uppercase tracking-mono-wide text-accent">
              Smart Clinic Queue
            </p>
            <h1 class="mt-6 font-sans text-5xl font-bold leading-tight tracking-tight text-text1">
              Your Clinic,
              <span class="text-accent">Always In Flow</span>
            </h1>
            <p class="mt-5 max-w-lg font-sans text-sm text-text2">
              Manage appointments, schedules, and patient journeys from one control center designed for real-world front desks and care teams.
            </p>
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div class="rounded border border-border bg-surface2 p-4">
              <p class="font-mono text-[11px] uppercase tracking-mono text-text2">Scheduling</p>
              <p class="mt-2 font-sans text-sm text-text1">Automated slot generation and conflict-safe booking windows.</p>
            </div>
            <div class="rounded border border-border bg-surface2 p-4">
              <p class="font-mono text-[11px] uppercase tracking-mono text-text2">Consultations</p>
              <p class="mt-2 font-sans text-sm text-text1">Fast EMR workflow for notes, prescriptions, and follow-ups.</p>
            </div>
          </div>
        </section>

        <section class="p-6 sm:p-8 lg:p-12">
          <div class="mx-auto w-full max-w-md">
            <div class="mb-8">
              <p class="font-mono text-[11px] uppercase tracking-mono text-accent">Welcome Back</p>
              <h2 class="mt-2 font-sans text-3xl font-bold leading-tight tracking-tight text-text1 sm:text-4xl">Sign In</h2>
              <p class="mt-3 font-sans text-sm text-text2">Use your clinic account to access role-based dashboards and workflows.</p>
            </div>

            <form @submit.prevent="handleLoginOfUser" novalidate class="space-y-5">
              <div>
                <label for="email" class="mb-1.5 block font-mono text-[11px] uppercase tracking-mono text-text2">Email Address</label>
                <input
                  id="email"
                  v-model="email"
                  type="email"
                  placeholder="name@clinic.com"
                  autocomplete="email"
                  class="w-full rounded border border-border bg-surface px-3 py-2 font-mono text-sm text-text1 placeholder:text-text3 outline-none transition-all duration-150 focus:border-accent focus:ring-2 focus:ring-accent/10"
                />
              </div>

              <div>
                <label for="password" class="mb-1.5 block font-mono text-[11px] uppercase tracking-mono text-text2">Password</label>
                <input
                  id="password"
                  v-model="password"
                  type="password"
                  placeholder="Enter your password"
                  autocomplete="current-password"
                  class="w-full rounded border border-border bg-surface px-3 py-2 font-mono text-sm text-text1 placeholder:text-text3 outline-none transition-all duration-150 focus:border-accent focus:ring-2 focus:ring-accent/10"
                />
              </div>

              <button
                type="submit"
                :disabled="loading"
                class="group inline-flex w-full items-center justify-center gap-2 rounded bg-accent px-4 py-3 font-mono text-[11px] uppercase tracking-mono-wide text-black transition-all duration-150 cursor-pointer hover:bg-accent-dim hover:-translate-y-px disabled:cursor-not-allowed disabled:opacity-60"
              >
                <span>{{ loading ? "Signing In..." : "Enter Dashboard" }}</span>
                <svg class="h-4 w-4 transition group-hover:translate-x-0.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M5 12h14"></path>
                  <path d="m12 5 7 7-7 7"></path>
                </svg>
              </button>

              <p class="pt-1 text-center font-sans text-sm text-text2">
                New here?
                <RouterLink to="/register" class="font-mono text-[11px] uppercase tracking-mono-wide text-accent transition-all duration-150 cursor-pointer hover:text-accent-dim">
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
