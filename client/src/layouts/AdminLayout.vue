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
  <div class="flex min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
    <!-- Sidebar -->
    <aside class="w-[260px] border-r border-slate-200 bg-gradient-to-b from-slate-900 to-slate-800 px-4.5 py-6 text-white shadow-lg">
      <div class="mb-8 px-2">
        <div class="mb-2 flex items-center gap-2">
          <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-blue-400 to-cyan-500 font-bold text-white">
            🏥
          </div>
          <h2 class="m-0 text-2xl font-bold">
            Clinic
          </h2>
        </div>
        <p class="mt-1.5 text-xs font-medium text-slate-400 uppercase tracking-wide">
          Admin Portal
        </p>
      </div>

      <nav class="flex flex-col gap-1">
        <RouterLink
          to="/admin"
          class="group relative overflow-hidden rounded-lg px-4 py-3 font-medium text-slate-300 transition-all duration-200 hover:bg-slate-700/50 hover:text-white"
          exact-active-class="bg-gradient-to-r from-blue-600 to-cyan-500 text-white shadow-lg shadow-blue-500/20"
        >
          <span class="flex items-center gap-3">
            <span class="text-lg">📊</span>
            <span>Dashboard</span>
          </span>
        </RouterLink>

        <RouterLink
          to="/admin/users"
          class="group relative overflow-hidden rounded-lg px-4 py-3 font-medium text-slate-300 transition-all duration-200 hover:bg-slate-700/50 hover:text-white"
          exact-active-class="bg-gradient-to-r from-blue-600 to-cyan-500 text-white shadow-lg shadow-blue-500/20"
        >
          <span class="flex items-center gap-3">
            <span class="text-lg">👥</span>
            <span>Users</span>
          </span>
        </RouterLink>

        <RouterLink
          to="/admin/pending-doctors"
          class="group relative overflow-hidden rounded-lg px-4 py-3 font-medium text-slate-300 transition-all duration-200 hover:bg-slate-700/50 hover:text-white"
          exact-active-class="bg-gradient-to-r from-blue-600 to-cyan-500 text-white shadow-lg shadow-blue-500/20"
        >
          <span class="flex items-center gap-3">
            <span class="text-lg">⚕️</span>
            <span>Pending Doctors</span>
          </span>
        </RouterLink>

        <RouterLink
        to="/admin/scheduling"
        class="group relative overflow-hidden rounded-lg px-4 py-3 font-medium text-slate-300 transition-all duration-200 hover:bg-slate-700/50 hover:text-white"
          exact-active-class="bg-gradient-to-r from-blue-600 to-cyan-500 text-white shadow-lg shadow-blue-500/20"
        >
          <span class="text-lg">📅 </span>
          <span>Scheduling</span>
        </RouterLink>
         

        <RouterLink 
        to="/admin/appointments" 
        class="group relative overflow-hidden rounded-lg px-4 py-3 font-medium text-slate-300 transition-all duration-200 hover:bg-slate-700/50 hover:text-white"
          exact-active-class="bg-gradient-to-r from-blue-600 to-cyan-500 text-white shadow-lg shadow-blue-500/20"
        >
          <span class="text-lg">📋</span>
          <span>Appointments</span>
        </RouterLink>
        
      </nav>

      <!-- Sidebar Footer -->
      <div class="absolute bottom-0 left-0 right-0 border-t border-slate-700 bg-slate-900/50 px-4.5 py-4">
        <p class="text-[11px] font-medium uppercase tracking-wider text-slate-500">
          Clinic Management System v1.0
        </p>
      </div>
    </aside>

    <!-- Main Content -->
    <main class="min-w-0 flex-1">
      <!-- Header -->
      <header class="border-b border-white/20 bg-white/40 backdrop-blur-md shadow-sm">
        <div class="flex h-[70px] items-center justify-between px-8">
          <!-- Left Side -->
          <div class="flex-1">
            <h1 class="m-0 text-xl font-bold text-gray-900">
              Admin Dashboard
            </h1>
            <p class="mt-0.5 text-xs font-medium text-gray-600">
              Clinic Appointment System
            </p>
          </div>

          <!-- Right Side - User Info & Logout -->
          <div class="flex items-center gap-6">
            <div class="hidden flex-col items-end md:flex">
              <strong class="text-sm font-semibold text-gray-900">
                {{ user.first_name || "Admin" }} {{ user.last_name || "" }}
              </strong>
              <span class="text-[12px] font-medium text-gray-600">
                {{ user.email }}
              </span>
            </div>

            <div class="h-10 w-10 rounded-full bg-gradient-to-br from-blue-400 to-cyan-500 flex items-center justify-center text-white font-bold text-sm">
              {{ (user.first_name?.[0] || "A") + (user.last_name?.[0] || "") }}
            </div>

            <button
              @click="logout"
              class="rounded-lg bg-gradient-to-r from-red-500 to-pink-500 px-4 py-2 text-sm font-semibold text-white shadow-md transition-all duration-200 hover:shadow-lg hover:scale-105 active:scale-95"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      <!-- Page Content -->
      <section class="overflow-y-auto bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 p-8">
        <RouterView />
      </section>
    </main>
  </div>
</template>