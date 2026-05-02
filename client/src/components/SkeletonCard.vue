<script setup>
defineProps({
  count: {
    type: Number,
    default: 1
  },
  type: {
    type: String,
    default: 'card',
    validator: (value) => ['card', 'row', 'text'].includes(value)
  },
  animated: {
    type: Boolean,
    default: true
  }
});
</script>

<template>
  <div class="space-y-3">
    <!-- Card Skeleton -->
    <div v-if="type === 'card'" class="space-y-3">
      <div
        v-for="n in count"
        :key="n"
        class="rounded-2xl border border-slate-200 bg-white p-6 dark:border-slate-800 dark:bg-slate-900"
        :class="{ 'animate-pulse': animated }"
      >
        <div class="mb-4 h-4 w-24 rounded bg-slate-200 dark:bg-slate-700"></div>
        <div class="mb-3 h-8 w-32 rounded bg-slate-200 dark:bg-slate-700"></div>
        <div class="h-3 w-48 rounded bg-slate-100 dark:bg-slate-800"></div>
      </div>
    </div>

    <!-- Row Skeleton (for tables) -->
    <div v-if="type === 'row'" class="space-y-3">
      <div
        v-for="n in count"
        :key="n"
        class="rounded-2xl border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-900"
        :class="{ 'animate-pulse': animated }"
      >
        <div class="flex gap-4">
          <div class="h-10 w-10 rounded-lg bg-slate-200 dark:bg-slate-700"></div>
          <div class="flex-1 space-y-2">
            <div class="h-4 w-1/3 rounded bg-slate-200 dark:bg-slate-700"></div>
            <div class="h-3 w-1/2 rounded bg-slate-100 dark:bg-slate-800"></div>
            <div class="h-3 w-1/4 rounded bg-slate-100 dark:bg-slate-800"></div>
          </div>
          <div class="space-y-2">
            <div class="h-4 w-16 rounded bg-slate-200 dark:bg-slate-700"></div>
            <div class="h-4 w-16 rounded bg-slate-100 dark:bg-slate-800"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Text Skeleton -->
    <div v-if="type === 'text'" class="space-y-2">
      <div
        v-for="n in count"
        :key="n"
        class="h-4 rounded bg-slate-200 dark:bg-slate-700"
        :class="{ 'animate-pulse': animated, 'w-3/4': n === count }"
      ></div>
    </div>
  </div>
</template>
