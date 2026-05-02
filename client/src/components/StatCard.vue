<script setup>
import { computed } from "vue";

const props = defineProps({
  label: {
    type: String,
    required: true
  },
  value: {
    type: [String, Number],
    required: true
  },
  icon: {
    type: String,
    default: null
  },
  color: {
    type: String,
    default: 'blue',
    validator: (value) => ['blue', 'green', 'red', 'amber', 'purple', 'cyan'].includes(value)
  }
});

const colorClasses = {
  blue: {
    iconBg: 'bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300',
  },
  green: {
    iconBg: 'bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300',
  },
  red: {
    iconBg: 'bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300',
  },
  amber: {
    iconBg: 'bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300',
  },
  purple: {
    iconBg: 'bg-purple-100 text-purple-700 dark:bg-purple-900/40 dark:text-purple-300',
  },
  cyan: {
    iconBg: 'bg-cyan-100 text-cyan-700 dark:bg-cyan-900/40 dark:text-cyan-300',
  }
};

const iconBgClass = computed(() => colorClasses[props.color]?.iconBg || colorClasses.blue.iconBg);
</script>

<template>
  <div
    class="group relative overflow-hidden rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition-all duration-200 hover:shadow-md dark:border-slate-800 dark:bg-slate-900"
  >
    <!-- Icon -->
    <div
      v-if="$slots.icon || icon"
      class="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-xl transition-transform duration-200 group-hover:scale-105"
      :class="iconBgClass"
    >
      <slot name="icon">
        <span class="text-lg font-bold">{{ icon }}</span>
      </slot>
    </div>

    <!-- Content -->
    <p class="text-sm font-semibold text-slate-500 dark:text-slate-400">
      {{ label }}
    </p>

    <p class="mt-2 text-3xl font-bold text-slate-900 dark:text-slate-100">
      {{ value }}
    </p>
  </div>
</template>
