<template>
  <div class="min-h-screen grid place-items-center bg-gray-50 p-6">
    <div class="w-full max-w-md rounded-2xl border border-gray-200 bg-white p-8 shadow-sm text-center">
      <p class="text-sm font-semibold uppercase tracking-wide text-amber-700">403</p>
      <h1 class="mt-2 text-2xl font-bold text-gray-900">Unauthorized</h1>
      <p class="mt-3 text-gray-600">
        You do not have permission to access this page.
      </p>
      <router-link
        to="/"
        class="mt-6 inline-block rounded-lg bg-blue-600 px-4 py-2 font-medium text-white hover:bg-blue-700"
      >
        Go To Home
      </router-link>
    </div>
  </div>
</template>
