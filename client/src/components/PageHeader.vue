<script setup>
defineProps({
  title: {
    type: String,
    required: true
  },
  subtitle: {
    type: String,
    default: null
  },
  badge: {
    type: String,
    default: null
  },
  badgeColor: {
    type: String,
    default: 'blue',
    validator: (value) => ['blue', 'green', 'red', 'amber', 'cyan'].includes(value)
  }
});

const badgeColorClasses = {
  blue: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300',
  green: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300',
  red: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300',
  amber: 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-300',
  cyan: 'bg-cyan-100 text-cyan-700 dark:bg-cyan-900/30 dark:text-cyan-300'
};
</script>

<template>
  <div class="flex flex-col gap-4 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900 md:flex-row md:items-center md:justify-between">
    <div class="flex-1">
      <h1 class="text-2xl font-bold leading-tight tracking-tight text-slate-900 dark:text-slate-100">
        {{ title }}
      </h1>

      <p v-if="subtitle" class="mt-2 text-sm text-slate-500 dark:text-slate-400">
        {{ subtitle }}
      </p>
    </div>

    <div v-if="badge" class="flex items-center gap-2">
      <span
        class="inline-flex rounded-xl px-4 py-2 text-xs font-bold"
        :class="badgeColorClasses[badgeColor]"
      >
        {{ badge }}
      </span>
    </div>
  </div>
</template>
