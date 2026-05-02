<script setup>
import { ref, computed } from "vue";
import { RouterLink, useRouter, useRoute } from "vue-router";
import { clearAuthData, getAuthUser } from "../api/auth";
import useTheme from "../composables/useTheme";
import {
  LayoutDashboard, Users, UserRoundCheck, CalendarDays,
  ClipboardList, BarChart3, LogOut, Sun, Moon, Menu, X, ChevronRight
} from "lucide-vue-next";

const router = useRouter();
const route = useRoute();
const { isDark, toggleTheme } = useTheme();

const sidebarOpen = ref(false);
const user = getAuthUser();
const userName = user?.first_name || user?.email?.split("@")[0] || "Admin";

function logout() {
  clearAuthData();
  router.push("/login");
}

const navLinks = [
  { to: "/admin", label: "Dashboard", icon: LayoutDashboard },
  { to: "/admin/users", label: "Users", icon: Users },
  { to: "/admin/pending-doctors", label: "Pending Doctors", icon: UserRoundCheck },
  { to: "/admin/scheduling", label: "Scheduling", icon: CalendarDays },
  { to: "/admin/appointments", label: "Appointments", icon: ClipboardList },
  { to: "/admin/analytics", label: "Analytics", icon: BarChart3 },
];

function isActive(path) {
  return route.path === path;
}
</script>

<template>
  <div class="flex h-screen bg-slate-50 dark:bg-slate-950">
    <!-- Sidebar Overlay (mobile) -->
    <Transition name="fade">
      <div
        v-if="sidebarOpen"
        class="fixed inset-0 z-40 bg-black/50 lg:hidden"
        @click="sidebarOpen = false"
      ></div>
    </Transition>

    <!-- Sidebar -->
    <aside
      :class="[
        'fixed inset-y-0 left-0 z-50 flex w-64 flex-col border-r border-slate-200 bg-white transition-transform duration-200 dark:border-slate-800 dark:bg-slate-950 lg:static lg:translate-x-0',
        sidebarOpen ? 'translate-x-0' : '-translate-x-full'
      ]"
    >
      <!-- Logo -->
      <div class="flex h-16 items-center gap-3 border-b border-slate-200 px-5 dark:border-slate-800">
        <div class="flex h-9 w-9 items-center justify-center rounded-xl bg-blue-600 text-sm font-bold text-white">
          CQ
        </div>
        <div>
          <p class="text-sm font-bold text-slate-900 dark:text-slate-100">ClinicQueue</p>
          <p class="text-xs text-slate-500 dark:text-slate-400">Admin Panel</p>
        </div>
      </div>

      <!-- Nav Links -->
      <nav class="flex-1 space-y-1 overflow-y-auto px-3 py-4">
        <RouterLink
          v-for="link in navLinks"
          :key="link.to"
          :to="link.to"
          @click="sidebarOpen = false"
          :class="[
            'flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-all duration-150',
            isActive(link.to)
              ? 'bg-blue-600 text-white shadow-sm'
              : 'text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800'
          ]"
        >
          <component :is="link.icon" class="h-5 w-5 flex-shrink-0" />
          <span>{{ link.label }}</span>
        </RouterLink>
      </nav>

      <!-- Sidebar Footer -->
      <div class="border-t border-slate-200 px-3 py-3 dark:border-slate-800">
        <button
          @click="logout"
          class="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium text-red-600 transition-all duration-150 hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-950/30"
        >
          <LogOut class="h-5 w-5" />
          <span>Logout</span>
        </button>
      </div>
    </aside>

    <!-- Main Content -->
    <div class="flex flex-1 flex-col overflow-hidden">
      <!-- Top Bar -->
      <header class="flex h-16 items-center justify-between border-b border-slate-200 bg-white px-4 dark:border-slate-800 dark:bg-slate-950 lg:px-6">
        <div class="flex items-center gap-3">
          <button
            @click="sidebarOpen = !sidebarOpen"
            class="flex h-9 w-9 items-center justify-center rounded-lg text-slate-500 transition hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800 lg:hidden"
          >
            <Menu class="h-5 w-5" />
          </button>

          <p class="text-sm font-medium text-slate-500 dark:text-slate-400">
            Welcome back, <span class="font-semibold text-slate-900 dark:text-slate-100">{{ userName }}</span>
          </p>
        </div>

        <div class="flex items-center gap-2">
          <!-- Theme Toggle -->
          <button
            @click="toggleTheme"
            class="flex h-9 w-9 items-center justify-center rounded-lg text-slate-500 transition hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800"
            :title="isDark ? 'Switch to light mode' : 'Switch to dark mode'"
          >
            <Moon v-if="!isDark" class="h-5 w-5" />
            <Sun v-else class="h-5 w-5" />
          </button>

          <!-- User Avatar -->
          <div class="flex h-9 w-9 items-center justify-center rounded-full bg-blue-600 text-xs font-bold text-white">
            {{ userName.charAt(0).toUpperCase() }}
          </div>
        </div>
      </header>

      <!-- Page Content -->
      <main class="flex-1 overflow-y-auto p-4 lg:p-6">
        <router-view />
      </main>
    </div>
  </div>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>