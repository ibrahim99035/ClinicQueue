<script setup>
import { ref } from "vue";
import { RouterLink, useRouter, useRoute } from "vue-router";
import { clearAuthData, getAuthUser } from "../api/auth";
import useTheme from "../composables/useTheme";
import {
  LayoutDashboard, ListChecks, CalendarDays, LogOut, Sun, Moon, Menu
} from "lucide-vue-next";

const router = useRouter();
const route = useRoute();
const { isDark, toggleTheme } = useTheme();

const sidebarOpen = ref(false);
const user = getAuthUser();
const userName = user?.first_name || user?.email?.split("@")[0] || "Doctor";

function logout() {
  clearAuthData();
  router.push("/login");
}

const navLinks = [
  { to: "/doctor", label: "Dashboard", icon: LayoutDashboard },
  { to: "/doctor/queue", label: "Appointment Queue", icon: ListChecks },
  { to: "/doctor/schedule", label: "My Schedule", icon: CalendarDays },
];

function isActive(path) {
  return route.path === path;
}
</script>

<template>
  <div class="flex h-screen bg-slate-50 dark:bg-slate-950">
    <!-- Mobile Overlay -->
    <Transition name="fade">
      <div v-if="sidebarOpen" class="fixed inset-0 z-40 bg-black/50 lg:hidden" @click="sidebarOpen = false" />
    </Transition>

    <!-- Sidebar -->
    <aside
      :class="[
        'fixed inset-y-0 left-0 z-50 flex w-64 flex-col border-r border-slate-200 bg-white transition-transform duration-200 dark:border-slate-800 dark:bg-slate-950 lg:static lg:translate-x-0',
        sidebarOpen ? 'translate-x-0' : '-translate-x-full'
      ]"
    >
      <div class="flex h-16 items-center gap-3 border-b border-slate-200 px-5 dark:border-slate-800">
        <div class="flex h-9 w-9 items-center justify-center rounded-xl bg-green-600 text-sm font-bold text-white">Dr</div>
        <div>
          <p class="text-sm font-bold text-slate-900 dark:text-slate-100">ClinicQueue</p>
          <p class="text-xs text-slate-500 dark:text-slate-400">Doctor Panel</p>
        </div>
      </div>

      <nav class="flex-1 space-y-1 overflow-y-auto px-3 py-4">
        <RouterLink
          v-for="link in navLinks" :key="link.to" :to="link.to" @click="sidebarOpen = false"
          :class="[
            'flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-all duration-150',
            isActive(link.to) ? 'bg-green-600 text-white shadow-sm' : 'text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800'
          ]"
        >
          <component :is="link.icon" class="h-5 w-5 flex-shrink-0" />
          <span>{{ link.label }}</span>
        </RouterLink>
      </nav>

      <div class="border-t border-slate-200 px-3 py-3 dark:border-slate-800">
        <button @click="logout" class="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium text-red-600 transition hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-950/30">
          <LogOut class="h-5 w-5" />
          <span>Logout</span>
        </button>
      </div>
    </aside>

    <!-- Main -->
    <div class="flex flex-1 flex-col overflow-hidden">
      <header class="flex h-16 items-center justify-between border-b border-slate-200 bg-white px-4 dark:border-slate-800 dark:bg-slate-950 lg:px-6">
        <div class="flex items-center gap-3">
          <button @click="sidebarOpen = !sidebarOpen" class="flex h-9 w-9 items-center justify-center rounded-lg text-slate-500 transition hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800 lg:hidden">
            <Menu class="h-5 w-5" />
          </button>
          <p class="text-sm font-medium text-slate-500 dark:text-slate-400">Welcome, <span class="font-semibold text-slate-900 dark:text-slate-100">Dr. {{ userName }}</span></p>
        </div>
        <div class="flex items-center gap-2">
          <button @click="toggleTheme" class="flex h-9 w-9 items-center justify-center rounded-lg text-slate-500 transition hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800">
            <Moon v-if="!isDark" class="h-5 w-5" /><Sun v-else class="h-5 w-5" />
          </button>
          <div class="flex h-9 w-9 items-center justify-center rounded-full bg-green-600 text-xs font-bold text-white">{{ userName.charAt(0).toUpperCase() }}</div>
        </div>
      </header>
      <main class="flex-1 overflow-y-auto p-4 lg:p-6"><router-view /></main>
    </div>
  </div>
</template>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
