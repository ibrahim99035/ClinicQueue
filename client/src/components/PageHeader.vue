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
  blue: 'bg-surface2 text-accent',
  green: 'bg-surface2 text-accent',
  red: 'bg-surface2 text-danger',
  amber: 'bg-surface2 text-yellow-400',
  cyan: 'bg-surface2 text-text1'
};
</script>

<template>
  <div class="flex flex-col gap-4 rounded border border-border bg-surface p-4 md:flex-row md:items-center md:justify-between">
    <div class="flex-1">
      <h1 class="font-sans font-bold text-2xl leading-tight tracking-tight text-text1">
        {{ title }}
      </h1>

      <p v-if="subtitle" class="mt-2 font-sans text-sm text-text2">
        {{ subtitle }}
      </p>
    </div>

    <div v-if="badge" class="flex items-center gap-2">
      <span
        class="inline-flex rounded px-4 py-2 font-mono text-[11px] uppercase tracking-mono-wide transition-all duration-150 cursor-pointer"
        :class="badgeColorClasses[badgeColor]"
      >
        {{ badge }}
      </span>
    </div>
  </div>
</template>
