<template>
  <button
    :type="type"
    :disabled="disabled || loading"
    :class="[
      'inline-flex items-center justify-center gap-2 rounded px-4 py-2.5 font-mono text-[11px] uppercase tracking-mono-wide transition-all duration-150 cursor-pointer disabled:opacity-60 disabled:cursor-not-allowed focus:outline-none',
      variantClasses,
      sizeClasses,
    ]"
    @click="$emit('click')"
  >
    <span v-if="loading" class="inline mr-2 font-mono text-[11px] uppercase tracking-mono-wide">⏳</span>
    <slot />
  </button>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({
  variant: {
    type: String,
    default: "primary",
    validator: (val) => ["primary", "secondary", "danger", "success", "ghost"].includes(val),
  },
  size: {
    type: String,
    default: "md",
    validator: (val) => ["sm", "md", "lg"].includes(val),
  },
  type: {
    type: String,
    default: "button",
  },
  disabled: {
    type: Boolean,
    default: false,
  },
  loading: {
    type: Boolean,
    default: false,
  },
});

defineEmits(["click"]);

const variantClasses = computed(() => {
  const variants = {
    primary: "bg-gradient-to-r from-blue-600 to-cyan-500 text-white shadow-md hover:shadow-lg focus:ring-blue-300",
    secondary: "bg-gray-200 text-gray-700 hover:bg-gray-300 focus:ring-gray-300",
    danger: "bg-red-600 text-white shadow-md hover:bg-red-700 hover:shadow-lg focus:ring-red-300",
    success: "bg-gradient-to-r from-green-600 to-emerald-500 text-white shadow-md hover:shadow-lg focus:ring-green-300",
    ghost: "bg-transparent text-gray-700 hover:bg-gray-100 focus:ring-gray-300",
  };
  return variants[props.variant] || variants.primary;
});

const sizeClasses = computed(() => {
  const sizes = {
    sm: "px-3 py-1.5 text-xs",
    md: "px-4 py-2.5 text-sm",
    lg: "px-6 py-3 text-base",
  };
  return sizes[props.size] || sizes.md;
});
</script>
