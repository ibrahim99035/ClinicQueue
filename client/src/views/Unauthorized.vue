<template>
  <div class="min-h-screen grid place-items-center bg-slate-50 p-6 text-slate-900 dark:bg-slate-950 dark:text-slate-100">
    <div class="w-full max-w-md rounded-2xl border border-slate-200 bg-white p-8 text-center shadow-sm dark:border-slate-800 dark:bg-slate-900">
      <p class="text-xs font-bold uppercase tracking-wide text-amber-600 dark:text-amber-400">403</p>
      <h1 class="mt-2 text-2xl font-bold leading-tight tracking-tight text-slate-900 dark:text-slate-100">Unauthorized</h1>
      <p class="mt-3 text-sm text-slate-500 dark:text-slate-400">
        You do not have permission to access this page.
      </p>
      <router-link
        to="/"
        class="mt-6 inline-flex items-center justify-center rounded-xl bg-blue-600 px-4 py-2.5 text-sm font-bold text-white transition-all duration-150 hover:bg-blue-700 hover:-translate-y-px"
      >
        Go To Home
      </router-link>
    </div>
  </div>
</template>
