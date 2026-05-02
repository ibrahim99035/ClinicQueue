<template>
  <div class="min-h-screen grid place-items-center bg-bg p-6 text-text1 font-sans">
    <div class="w-full max-w-md rounded border border-border bg-surface p-8 text-center">
      <p class="font-mono text-[11px] uppercase tracking-mono text-yellow-400">403</p>
      <h1 class="mt-2 font-sans text-2xl font-bold leading-tight tracking-tight text-text1">Unauthorized</h1>
      <p class="mt-3 font-sans text-sm text-text2">
        You do not have permission to access this page.
      </p>
      <router-link
        to="/"
        class="mt-6 inline-flex items-center justify-center rounded bg-accent px-4 py-2 font-mono text-[11px] uppercase tracking-mono-wide text-black transition-all duration-150 cursor-pointer hover:bg-accent-dim hover:-translate-y-px"
      >
        Go To Home
      </router-link>
    </div>
  </div>
</template>
