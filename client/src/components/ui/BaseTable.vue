<template>
  <div class="overflow-hidden rounded border border-border bg-surface">
    <div v-if="title" class="flex items-center justify-between border-b border-border px-4 py-4">
      <h3 class="font-sans font-semibold text-base text-text1">{{ title }}</h3>
      <slot name="toolbar" />
    </div>

    <div v-if="loading" class="p-4">
      <slot name="loading">
        <div class="font-sans text-sm text-text2">Loading...</div>
      </slot>
    </div>

    <div v-else-if="items.length === 0" class="p-4">
      <slot name="empty">
        <div class="font-sans text-sm text-text2">No items found.</div>
      </slot>
    </div>

    <div v-else class="overflow-x-auto">
      <table :class="['w-full border-collapse text-left', tableClass]">
        <thead>
          <tr class="bg-surface2">
            <slot name="thead" />
          </tr>
        </thead>

        <tbody>
          <slot name="tbody" :items="items" />
        </tbody>
      </table>
    </div>

    <div v-if="$slots.pagination" class="border-t border-border px-4 py-4">
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
