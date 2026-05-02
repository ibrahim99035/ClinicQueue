<script setup>
defineProps({
  icon: {
    type: String,
    default: null
  },
  title: {
    type: String,
    required: true
  },
  description: {
    type: String,
    default: null
  },
  actionLabel: {
    type: String,
    default: null
  },
  actionIcon: {
    type: String,
    default: null
  }
});

defineEmits(['action']);
</script>

<template>
  <div class="flex flex-col items-center justify-center rounded-2xl border border-dashed border-slate-300 bg-white px-6 py-16 text-center transition-all duration-150 dark:border-slate-700 dark:bg-slate-900">
    <!-- Icon slot -->
    <div class="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-slate-100 text-slate-400 dark:bg-slate-800 dark:text-slate-500">
      <slot name="icon">
        <span v-if="icon" class="text-2xl">{{ icon }}</span>
        <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-7 w-7" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 8V5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v3"/><path d="M21 16v3a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-3"/><path d="M4 12h16"/></svg>
      </slot>
    </div>

    <!-- Title -->
    <h3 class="mb-2 text-base font-semibold text-slate-900 dark:text-slate-100">
      {{ title }}
    </h3>

    <!-- Description -->
    <p v-if="description" class="mb-6 max-w-sm text-sm text-slate-500 dark:text-slate-400">
      {{ description }}
    </p>

    <!-- Action Button -->
    <button
      v-if="actionLabel"
      @click="$emit('action')"
      class="inline-flex items-center gap-2 rounded-xl bg-blue-600 px-4 py-2.5 text-sm font-bold text-white shadow-sm transition hover:bg-blue-700"
    >
      <slot name="actionIcon">
        <span v-if="actionIcon">{{ actionIcon }}</span>
      </slot>
      {{ actionLabel }}
    </button>
  </div>
</template>
