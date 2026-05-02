<script setup>
defineProps({
  items: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false,
  },
  title: {
    type: String,
    default: null,
  },
  tableClass: {
    type: String,
    default: '',
  },
});
</script>

<template>
  <div class="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-slate-900">
    <!-- Toolbar -->
    <div
      v-if="title || $slots.toolbar"
      class="flex flex-col gap-3 border-b border-slate-200 px-6 py-4 dark:border-slate-800 md:flex-row md:items-center md:justify-between"
    >
      <h3 v-if="title" class="text-lg font-bold text-slate-900 dark:text-slate-100">
        {{ title }}
      </h3>

      <div v-if="$slots.toolbar" class="flex items-center gap-3">
        <slot name="toolbar" />
      </div>
    </div>

    <!-- Table -->
    <div class="overflow-x-auto">
      <table class="w-full text-left text-sm" :class="tableClass">
        <thead>
          <tr class="border-b border-slate-200 bg-slate-50 text-xs uppercase tracking-wider text-slate-500 dark:border-slate-800 dark:bg-slate-950 dark:text-slate-400">
            <slot name="thead" />
          </tr>
        </thead>

        <tbody>
          <slot name="tbody" :items="items" />
        </tbody>
      </table>
    </div>

    <!-- Pagination Footer -->
    <div
      v-if="$slots.pagination"
      class="border-t border-slate-200 px-6 py-3 dark:border-slate-800"
    >
      <slot name="pagination" />
    </div>
  </div>
</template>
