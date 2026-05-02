<script setup>
import { computed } from "vue";
import { useRouter } from "vue-router";
import { clearAuthData } from "../api/auth"

const router = useRouter();

const user = computed(()=>{
    try{
        return JSON.parse(localStorage.getItem("user") || "{}");
    }catch{
        return {};
    }
});

function logout() {
    clearAuthData();
    router.push("/login");
}
</script>
<template>
  <div class="flex min-h-screen bg-bg text-text1 font-sans">
    <!-- Sidebar -->
    <aside class="w-[260px] border-r border-border bg-surface px-4 py-6 text-text1">
      <div class="mb-8 px-2">
        <div class="mb-2 flex items-center gap-2">
          <div class="flex h-10 w-10 items-center justify-center rounded bg-surface2 font-mono text-[11px] uppercase tracking-mono-wide text-accent">
            🏥
          </div>
          <h2 class="m-0 font-sans text-2xl font-bold leading-tight tracking-tight text-text1">
            Clinic
          </h2>
        </div>
        <p class="mt-1.5 font-mono text-[11px] uppercase tracking-mono text-text2">
          Admin Portal
        </p>
      </div>

      <nav class="flex flex-col gap-0.5">
        <RouterLink
          to="/admin"
          class="flex items-center gap-2 rounded px-3 py-2 font-mono text-[11px] uppercase tracking-mono text-text2 transition-all duration-150 cursor-pointer hover:bg-surface2 hover:text-text1"
          exact-active-class="bg-gradient-to-r from-blue-600 to-cyan-500 text-white shadow-lg shadow-blue-500/20"
        >
          <span class="flex items-center gap-3">
            <span class="text-lg">📊</span>
            <span>Dashboard</span>
          </span>
        </RouterLink>

        <RouterLink
          to="/admin/users"
          class="flex items-center gap-2 rounded px-3 py-2 font-mono text-[11px] uppercase tracking-mono text-text2 transition-all duration-150 cursor-pointer hover:bg-surface2 hover:text-text1"
          exact-active-class="bg-gradient-to-r from-blue-600 to-cyan-500 text-white shadow-lg shadow-blue-500/20"
        >
          <span class="flex items-center gap-3">
            <span class="text-lg">👥</span>
            <span>Users</span>
          </span>
        </RouterLink>

        <RouterLink
          to="/admin/pending-doctors"
          class="flex items-center gap-2 rounded px-3 py-2 font-mono text-[11px] uppercase tracking-mono text-text2 transition-all duration-150 cursor-pointer hover:bg-surface2 hover:text-text1"
          exact-active-class="bg-gradient-to-r from-blue-600 to-cyan-500 text-white shadow-lg shadow-blue-500/20"
        >
          <span class="flex items-center gap-3">
            <span class="text-lg">⚕️</span>
            <span>Pending Doctors</span>
          </span>
        </RouterLink>

        <RouterLink
        to="/admin/scheduling"
        class="flex items-center gap-2 rounded px-3 py-2 font-mono text-[11px] uppercase tracking-mono text-text2 transition-all duration-150 cursor-pointer hover:bg-surface2 hover:text-text1"
          exact-active-class="bg-gradient-to-r from-blue-600 to-cyan-500 text-white shadow-lg shadow-blue-500/20"
        >
          <span class="text-lg">📅 </span>
          <span>Scheduling</span>
        </RouterLink>
         

        <RouterLink 
        to="/admin/appointments" 
        class="flex items-center gap-2 rounded px-3 py-2 font-mono text-[11px] uppercase tracking-mono text-text2 transition-all duration-150 cursor-pointer hover:bg-surface2 hover:text-text1"
          exact-active-class="bg-gradient-to-r from-blue-600 to-cyan-500 text-white shadow-lg shadow-blue-500/20"
        >
          <span class="text-lg">📋</span>
          <span>Appointments</span>
        </RouterLink>

        <RouterLink
        to="/admin/analytics"
        class="flex items-center gap-2 rounded px-3 py-2 font-mono text-[11px] uppercase tracking-mono text-text2 transition-all duration-150 cursor-pointer hover:bg-surface2 hover:text-text1"
        exact-active-class="bg-gradient-to-r from-blue-600 to-cyan-500 text-white shadow-lg shadow-blue-500/20"
      >
        <span class="flex items-center gap-3">
          <span class="text-lg">📈</span>
          <span>Analytics</span>
        </span>
      </RouterLink>

      </nav>
    </aside>

    <!-- Main Content -->
    <main class="min-w-0 flex-1">
      <!-- Header -->
      <header class="border-b border-border bg-surface">
        <div class="flex h-[70px] items-center justify-between px-6 md:px-8">
          <!-- Left Side -->
          <div class="flex-1">
            <h1 class="m-0 font-sans text-xl font-bold leading-tight tracking-tight text-text1">
              Admin Dashboard
            </h1>
            <p class="mt-0.5 font-mono text-[11px] uppercase tracking-mono text-text2">
              Clinic Appointment System
            </p>
          </div>

          <!-- Right Side - User Info & Logout -->
          <div class="flex items-center gap-6">
            <div class="hidden flex-col items-end md:flex">
              <strong class="font-sans text-sm font-semibold text-text1">
                {{ user.first_name || "Admin" }} {{ user.last_name || "" }}
              </strong>
              <span class="font-mono text-[11px] uppercase tracking-mono text-text2">
                {{ user.email }}
              </span>
            </div>

            <div class="flex h-10 w-10 items-center justify-center rounded bg-surface2 font-mono text-[11px] uppercase tracking-mono-wide text-accent">
              {{ (user.first_name?.[0] || "A") + (user.last_name?.[0] || "") }}
            </div>

            <button
              @click="logout"
              class="rounded border border-danger px-4 py-2 font-mono text-[11px] uppercase tracking-mono-wide text-danger transition-all duration-150 cursor-pointer hover:bg-danger/10"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      <!-- Page Content -->
      <section class="overflow-y-auto bg-bg px-6 py-8 md:px-12">
        <RouterView />
      </section>
    </main>
  </div>
</template>