<script setup>
import { computed } from "vue";
import { ChevronLeft, ChevronRight } from "lucide-vue-next";

const props = defineProps({
  currentPage: {
    type: Number,
    default: 1,
  },
  totalPages: {
    type: Number,
    default: 1,
  },
});

const emit = defineEmits(["page-change"]);

const pages = computed(() => {
  const pagesArray = [];
  const currentPage = props.currentPage;
  const totalPages = props.totalPages;

  let start = Math.max(1, currentPage - 2);
  let end = Math.min(totalPages, currentPage + 2);

  if (end - start < 4) {
    if (start === 1) {
      end = Math.min(totalPages, start + 4);
    } else {
      start = Math.max(1, end - 4);
    }
  }

  for (let i = start; i <= end; i++) {
    pagesArray.push(i);
  }

  return pagesArray;
});
</script>

<template>
  <div class="flex flex-wrap items-center gap-2" v-if="totalPages > 1">
    <!-- Previous -->
    <button
      @click="emit('page-change', currentPage - 1)"
      :disabled="currentPage === 1"
      class="flex h-9 w-9 items-center justify-center rounded-lg border border-slate-200 text-slate-600 transition hover:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-40 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
    >
      <ChevronLeft class="h-4 w-4" />
    </button>

    <!-- Page numbers -->
    <button
      v-for="page in pages"
      :key="page"
      @click="emit('page-change', page)"
      :class="[
        'flex h-9 w-9 items-center justify-center rounded-lg text-sm font-semibold transition',
        page === currentPage
          ? 'bg-blue-600 text-white'
          : 'border border-slate-200 text-slate-600 hover:bg-slate-100 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800'
      ]"
    >
      {{ page }}
    </button>

    <!-- Next -->
    <button
      @click="emit('page-change', currentPage + 1)"
      :disabled="currentPage === totalPages"
      class="flex h-9 w-9 items-center justify-center rounded-lg border border-slate-200 text-slate-600 transition hover:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-40 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
    >
      <ChevronRight class="h-4 w-4" />
    </button>
  </div>
</template>
