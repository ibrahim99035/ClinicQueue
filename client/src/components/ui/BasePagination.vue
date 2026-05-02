<template>
  <div v-if="totalItems > 0" class="flex items-center justify-between border-t border-border px-4 py-4">
    <div class="font-sans text-sm text-text1">
      Page {{ currentPage }} of {{ totalPages }} ({{ totalItems }} item{{ totalItems !== 1 ? "s" : "" }})
    </div>

    <div class="flex gap-2">
      <button
        type="button"
        @click="previousPage"
        :disabled="currentPage === 1"
        class="rounded bg-transparent border border-border px-4 py-2 font-mono text-[11px] uppercase tracking-mono text-text2 hover:border-accent hover:text-text1 transition-all duration-150 cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed"
      >
        ← Previous
      </button>

      <div class="flex items-center gap-2 px-3 py-2">
        <input
          type="number"
          :value="currentPage"
          :min="1"
          :max="totalPages"
          @change="goToPage"
          class="w-12 rounded border border-border bg-surface px-2 py-1 text-center font-mono text-sm text-text1 outline-none transition-all duration-150 focus:border-accent focus:ring-2 focus:ring-accent/10"
        />
        <span class="font-sans text-sm text-text2">/ {{ totalPages }}</span>
      </div>

      <button
        type="button"
        @click="nextPage"
        :disabled="currentPage === totalPages"
        class="rounded bg-transparent border border-border px-4 py-2 font-mono text-[11px] uppercase tracking-mono text-text2 hover:border-accent hover:text-text1 transition-all duration-150 cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed"
      >
        Next →
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({
  currentPage: {
    type: Number,
    required: true,
  },
  itemsPerPage: {
    type: Number,
    required: true,
  },
  totalItems: {
    type: Number,
    required: true,
  },
});

const emit = defineEmits(["update:currentPage"]);

const totalPages = computed(() => Math.ceil(props.totalItems / props.itemsPerPage) || 1);

function previousPage() {
  if (props.currentPage > 1) {
    emit("update:currentPage", props.currentPage - 1);
  }
}

function nextPage() {
  if (props.currentPage < totalPages.value) {
    emit("update:currentPage", props.currentPage + 1);
  }
}

function goToPage(e) {
  const page = parseInt(e.target.value);
  if (page >= 1 && page <= totalPages.value) {
    emit("update:currentPage", page);
  }
}
</script>
