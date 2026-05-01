<template>
  <div v-if="totalItems > 0" class="flex items-center justify-between border-t border-gray-200 bg-gray-50/50 px-6 py-4">
    <div class="text-sm font-semibold text-gray-700">
      Page {{ currentPage }} of {{ totalPages }} ({{ totalItems }} item{{ totalItems !== 1 ? "s" : "" }})
    </div>

    <div class="flex gap-2">
      <button
        type="button"
        @click="previousPage"
        :disabled="currentPage === 1"
        class="rounded-lg bg-gray-300 px-4 py-2 text-sm font-semibold text-gray-700 hover:bg-gray-400 disabled:opacity-40 disabled:cursor-not-allowed transition-all duration-200"
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
          class="w-12 rounded-lg border border-gray-300 px-2 py-1 text-center text-sm text-gray-700 outline-none focus:ring-2 focus:ring-blue-200"
        />
        <span class="text-sm text-gray-600">/ {{ totalPages }}</span>
      </div>

      <button
        type="button"
        @click="nextPage"
        :disabled="currentPage === totalPages"
        class="rounded-lg bg-gray-300 px-4 py-2 text-sm font-semibold text-gray-700 hover:bg-gray-400 disabled:opacity-40 disabled:cursor-not-allowed transition-all duration-200"
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
