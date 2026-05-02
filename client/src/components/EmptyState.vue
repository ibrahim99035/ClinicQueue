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
  <div class="flex flex-col items-center justify-center rounded border border-dashed border-border bg-surface px-6 py-16 text-center transition-all duration-150 hover:border-accent/30">
    <!-- Icon -->
    <div class="mb-4 text-5xl">
      {{ icon }}
    </div>

    <!-- Title -->
    <h3 class="mb-2 font-sans font-semibold text-base text-text1">
      {{ title }}
    </h3>

    <!-- Description -->
    <p v-if="description" class="mb-6 max-w-sm font-sans text-sm text-text2">
      {{ description }}
    </p>

    <!-- Action Button -->
    <button
      v-if="actionLabel"
      @click="$emit('action')"
      class="inline-flex items-center gap-2 rounded bg-accent px-4 py-2 font-mono text-[11px] uppercase tracking-mono-wide text-black transition-all duration-150 cursor-pointer hover:bg-accent-dim hover:-translate-y-px"
    >
      <span v-if="actionIcon">{{ actionIcon }}</span>
      {{ actionLabel }}
    </button>
  </div>
</template>
