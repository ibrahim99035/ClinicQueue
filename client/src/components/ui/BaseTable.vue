<template>
  <div class="overflow-hidden rounded-2xl border border-white/50 bg-white/80 shadow-sm backdrop-blur">
    <div v-if="title" class="flex items-center justify-between border-b border-gray-200 px-6 py-5">
      <h3 class="text-lg font-bold text-gray-900">{{ title }}</h3>
      <slot name="toolbar" />
    </div>

    <div v-if="loading" class="p-6">
      <slot name="loading">
        <div class="text-sm text-gray-500">Loading...</div>
      </slot>
    </div>

    <div v-else-if="items.length === 0" class="p-6">
      <slot name="empty">
        <div class="text-sm text-gray-500">No items found.</div>
      </slot>
    </div>

    <div v-else class="overflow-x-auto">
      <table :class="['w-full border-collapse text-left', tableClass]">
        <thead>
          <tr class="border-b border-gray-200 bg-gradient-to-r from-slate-50 to-blue-50/50">
            <slot name="thead" />
          </tr>
        </thead>

        <tbody>
          <slot name="tbody" :items="items" />
        </tbody>
      </table>
    </div>

    <div v-if="$slots.pagination" class="border-t border-gray-200 bg-gray-50/50 px-6 py-4">
      <slot name="pagination" />
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  items: {
    type: Array,
    default: () => [],
  },
  loading: {
    type: Boolean,
    default: false,
  },
  title: {
    type: String,
    default: "",
  },
  tableClass: {
    type: String,
    default: "min-w-[900px]",
  },
});
</script>
