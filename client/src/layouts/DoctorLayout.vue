<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <nav class="bg-white shadow-md">
      <div class="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
        <h1 class="text-2xl font-bold text-blue-600">ClinicQueue</h1>
        <div class="flex gap-4">
          <span class="text-gray-600">Dr. {{ userName }}</span>
          <button
            @click="logout"
            class="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600"
          >
            Logout
          </button>
        </div>
      </div>
    </nav>

    <!-- Sidebar + Main -->
    <div class="flex max-w-7xl mx-auto gap-6 p-6">
      <!-- Sidebar -->
      <aside class="w-64 bg-white rounded-lg shadow-md h-fit sticky top-20">
        <nav class="p-4 space-y-2">
          <router-link
            to="/doctor"
            class="block px-4 py-2 rounded-lg"
            :class="[
              $route.path === '/doctor'
                ? 'bg-blue-100 text-blue-700 font-semibold'
                : 'text-gray-700 hover:bg-gray-100',
            ]"
          >
            Dashboard
          </router-link>
          <router-link
            to="/doctor/queue"
            class="block px-4 py-2 rounded-lg"
            :class="[
              $route.path === '/doctor/queue'
                ? 'bg-blue-100 text-blue-700 font-semibold'
                : 'text-gray-700 hover:bg-gray-100',
            ]"
          >
            Appointment Queue
          </router-link>
          <router-link
            to="/doctor/schedule"
            class="block px-4 py-2 rounded-lg"
            :class="[
              $route.path === '/doctor/schedule'
                ? 'bg-blue-100 text-blue-700 font-semibold'
                : 'text-gray-700 hover:bg-gray-100',
            ]"
          >
            My Schedule
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

const userName = computed(() => user.value?.name || "Doctor");

function logout() {
  authLogout();
  router.push("/login");
}
</script>
