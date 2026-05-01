<script setup>
import { computed } from "vue";

const props = defineProps({
  status: {
    type: String,
    required: true
  },
  size: {
    type: String,
    default: 'md',
    validator: (value) => ['sm', 'md', 'lg'].includes(value)
  }
});

const statusConfig = {
  active: {
    bg: 'bg-green-100',
    text: 'text-green-700',
    dot: 'bg-green-500'
  },
  inactive: {
    bg: 'bg-red-100',
    text: 'text-red-700',
    dot: 'bg-red-500'
  },
  pending: {
    bg: 'bg-amber-100',
    text: 'text-amber-700',
    dot: 'bg-amber-500'
  },
  approved: {
    bg: 'bg-green-100',
    text: 'text-green-700',
    dot: 'bg-green-500'
  },
  cancelled: {
    bg: 'bg-gray-100',
    text: 'text-gray-700',
    dot: 'bg-gray-500'
  },
  confirmed: {
    bg: 'bg-blue-100',
    text: 'text-blue-700',
    dot: 'bg-blue-500'
  },
  checked_in: {
    bg: 'bg-cyan-100',
    text: 'text-cyan-700',
    dot: 'bg-cyan-500'
  },
  done: {
    bg: 'bg-green-100',
    text: 'text-green-700',
    dot: 'bg-green-500'
  },
  no_show: {
    bg: 'bg-red-100',
    text: 'text-red-700',
    dot: 'bg-red-500'
  },
  expired: {
    bg: 'bg-gray-100',
    text: 'text-gray-700',
    dot: 'bg-gray-500'
  }
};

const sizeClasses = {
  sm: 'px-2.5 py-1 text-xs',
  md: 'px-3 py-1.5 text-sm',
  lg: 'px-4 py-2 text-base'
};

const config = computed(() =>
  statusConfig[String(props.status || "").toLowerCase()] || statusConfig.pending
);

const displayStatus = computed(() => {
  const status = String(props.status || "pending");
  return status.charAt(0).toUpperCase() + status.slice(1).replaceAll('_', ' ');
});
</script>

<template>
  <div
    class="inline-flex items-center gap-2 rounded-full font-semibold transition-all duration-200 hover:shadow-sm"
    :class="[config.bg, config.text, sizeClasses[props.size]]"
  >
    <span class="inline-block h-2 w-2 rounded-full" :class="config.dot"></span>
    <span>{{ displayStatus }}</span>
  </div>
</template>
