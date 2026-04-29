<script setup>
defineProps({
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
    bg: 'bg-blue-50',
    icon: 'bg-blue-100 text-blue-700',
    text: 'text-blue-600'
  },
  green: {
    bg: 'bg-green-50',
    icon: 'bg-green-100 text-green-700',
    text: 'text-green-600'
  },
  red: {
    bg: 'bg-red-50',
    icon: 'bg-red-100 text-red-700',
    text: 'text-red-600'
  },
  amber: {
    bg: 'bg-amber-50',
    icon: 'bg-amber-100 text-amber-700',
    text: 'text-amber-600'
  },
  purple: {
    bg: 'bg-purple-50',
    icon: 'bg-purple-100 text-purple-700',
    text: 'text-purple-600'
  },
  cyan: {
    bg: 'bg-cyan-50',
    icon: 'bg-cyan-100 text-cyan-700',
    text: 'text-cyan-600'
  }
};
</script>

<template>
  <div 
    class="group relative overflow-hidden rounded-2xl border border-white/50 bg-white/80 p-6 shadow-sm backdrop-blur transition-all duration-300 hover:-translate-y-1 hover:shadow-lg hover:border-white/70"
    :class="colorClasses[color].bg"
  >
    <!-- Decorative gradient background -->
    <div class="absolute inset-0 -z-10 opacity-0 transition-opacity duration-300 group-hover:opacity-5"
      :class="colorClasses[color].text"
    ></div>

    <!-- Icon -->
    <div
      v-if="icon"
      class="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-xl font-bold text-lg transition-transform duration-300 group-hover:scale-110"
      :class="colorClasses[color].icon"
    >
      {{ icon }}
    </div>

    <!-- Content -->
    <div class="flex flex-col gap-3">
      <span class="text-sm font-semibold text-gray-600">
        {{ label }}
      </span>

      <strong class="text-3xl font-bold text-gray-900">
        {{ value }}
      </strong>
    </div>

    <!-- Animated border on hover -->
    <div class="absolute inset-0 -z-10 rounded-2xl border border-transparent transition-colors duration-300 group-hover:border-current"
      :class="colorClasses[color].text"
    ></div>
  </div>
</template>

<style scoped>
@keyframes subtle-float {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-2px);
  }
}

.group:hover {
  animation: subtle-float 3s ease-in-out infinite;
}
</style>
