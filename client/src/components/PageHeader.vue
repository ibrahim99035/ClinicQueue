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
  blue: 'bg-blue-100 text-blue-700',
  green: 'bg-green-100 text-green-700',
  red: 'bg-red-100 text-red-700',
  amber: 'bg-amber-100 text-amber-700',
  cyan: 'bg-cyan-100 text-cyan-700'
};
</script>

<template>
  <div class="flex flex-col gap-4 rounded-2xl border border-white/50 bg-white/80 p-6 shadow-sm backdrop-blur md:flex-row md:items-center md:justify-between">
    <div class="flex-1">
      <h1 class="text-2xl font-bold text-gray-900">
        {{ title }}
      </h1>

      <p v-if="subtitle" class="mt-2 text-sm leading-6 text-gray-600">
        {{ subtitle }}
      </p>
    </div>

    <div v-if="badge" class="flex items-center gap-2">
      <span
        class="inline-flex rounded-full px-4 py-2 text-sm font-semibold transition-transform duration-200 hover:scale-105"
        :class="badgeColorClasses[badgeColor]"
      >
        {{ badge }}
      </span>
    </div>
  </div>
</template>
