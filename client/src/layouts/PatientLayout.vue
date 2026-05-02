<template>
  <div class="min-h-screen bg-bg text-text1 font-sans">
    <!-- Header -->
    <nav class="border-b border-border bg-surface">
      <div class="mx-auto flex max-w-7xl items-center justify-between px-6 py-4 md:px-12">
        <h1 class="font-sans text-2xl font-bold leading-tight tracking-tight text-text1">ClinicQueue</h1>
        <div class="flex items-center gap-4">
          <span class="font-mono text-[11px] uppercase tracking-mono text-text2">{{ userName }}</span>
          <button
            @click="logout"
            class="rounded border border-danger px-4 py-2 font-mono text-[11px] uppercase tracking-mono-wide text-danger transition-all duration-150 cursor-pointer hover:bg-danger/10"
          >
            Logout
          </button>
        </div>
      </div>
    </nav>

    <!-- Sidebar + Main -->
    <div class="mx-auto flex max-w-7xl gap-6 px-6 py-8 md:px-12">
      <!-- Sidebar -->
      <aside class="w-64 h-fit sticky top-20 rounded border border-border bg-surface">
        <nav class="flex flex-col gap-0.5 p-4">
          <router-link
            to="/patient"
            class="block rounded px-3 py-2 font-mono text-[11px] uppercase tracking-mono text-text2 transition-all duration-150 cursor-pointer hover:bg-surface2 hover:text-text1"
            :class="[
              $route.path === '/patient'
                ? 'bg-blue-100 text-blue-700 font-semibold'
                : 'text-gray-700 hover:bg-gray-100',
            ]"
          >
            Dashboard
          </router-link>
          <router-link
            to="/patient/book"
            class="block rounded px-3 py-2 font-mono text-[11px] uppercase tracking-mono text-text2 transition-all duration-150 cursor-pointer hover:bg-surface2 hover:text-text1"
            :class="[
              $route.path === '/patient/book'
                ? 'bg-blue-100 text-blue-700 font-semibold'
                : 'text-gray-700 hover:bg-gray-100',
            ]"
          >
            Book Appointment
          </router-link>
          <router-link
            to="/patient/appointments"
            class="block rounded px-3 py-2 font-mono text-[11px] uppercase tracking-mono text-text2 transition-all duration-150 cursor-pointer hover:bg-surface2 hover:text-text1"
            :class="[
              $route.path === '/patient/appointments'
                ? 'bg-blue-100 text-blue-700 font-semibold'
                : 'text-gray-700 hover:bg-gray-100',
            ]"
          >
            My Appointments
          </router-link>
          <router-link
            to="/patient/waiting-list"
            class="block rounded px-3 py-2 font-mono text-[11px] uppercase tracking-mono text-text2 transition-all duration-150 cursor-pointer hover:bg-surface2 hover:text-text1"
            :class="[
              $route.path === '/patient/waiting-list'
                ? 'bg-blue-100 text-blue-700 font-semibold'
                : 'text-gray-700 hover:bg-gray-100',
            ]"
          >
            Waiting List
          </router-link>
          <router-link
            to="/patient/consultations"
            class="block rounded px-3 py-2 font-mono text-[11px] uppercase tracking-mono text-text2 transition-all duration-150 cursor-pointer hover:bg-surface2 hover:text-text1"
            :class="[
              $route.path === '/patient/consultations'
                ? 'bg-blue-100 text-blue-700 font-semibold'
                : 'text-gray-700 hover:bg-gray-100',
            ]"
          >
            My Consultations
          </router-link>
        </nav>
      </aside>

      <!-- Main Content -->
      <main class="flex-1">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue";
import useAuth from "../composables/useAuth";
import { useRouter } from "vue-router";

const { user, logout: authLogout } = useAuth();
const router = useRouter();

const userName = computed(() => user.value?.name || "Patient");

function logout() {
  authLogout();
  router.push("/login");
}
</script>
