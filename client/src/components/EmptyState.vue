<script setup>
defineProps({
  icon: {
    type: String,
    default: '📭'
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
  <div class="flex flex-col items-center justify-center rounded-2xl border border-dashed border-gray-300 bg-gray-50/50 px-6 py-16 text-center transition-all duration-300 hover:border-gray-400 hover:bg-gray-50">
    <!-- Icon -->
    <div class="mb-4 text-5xl">
      {{ icon }}
    </div>

    <!-- Title -->
    <h3 class="mb-2 text-lg font-bold text-gray-900">
      {{ title }}
    </h3>

    <!-- Description -->
    <p v-if="description" class="mb-6 max-w-sm text-sm leading-6 text-gray-600">
      {{ description }}
    </p>

    <!-- Action Button -->
    <button
      v-if="actionLabel"
      @click="$emit('action')"
      class="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white transition-all duration-200 hover:bg-blue-700 hover:shadow-md active:scale-95"
    >
      <span v-if="actionIcon">{{ actionIcon }}</span>
      {{ actionLabel }}
    </button>
  </div>
</template>
