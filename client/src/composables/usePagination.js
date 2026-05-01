import { ref, computed } from "vue";

export default function usePagination(fetchFn, initialPageSize = 10) {
  const page = ref(1);
  const pageSize = ref(initialPageSize);
  const items = ref([]);
  const total = ref(0);
  const loading = ref(false);
  const error = ref(null);

  const totalPages = computed(() => Math.ceil(total.value / pageSize.value));
  const hasNextPage = computed(() => page.value < totalPages.value);
  const hasPrevPage = computed(() => page.value > 1);

  async function fetch() {
    loading.value = true;
    error.value = null;
    try {
      const result = await fetchFn({
        page: page.value,
        page_size: pageSize.value,
      });

      if (result.results) {
        items.value = result.results;
        total.value = result.count || 0;
      } else if (Array.isArray(result)) {
        items.value = result;
        total.value = result.length;
      } else {
        items.value = [];
        total.value = 0;
      }
    } catch (err) {
      error.value = err.message || "Failed to fetch data";
      items.value = [];
    } finally {
      loading.value = false;
    }
  }

  async function next() {
    if (hasNextPage.value) {
      page.value++;
      await fetch();
    }
  }

  async function prev() {
    if (hasPrevPage.value) {
      page.value--;
      await fetch();
    }
  }

  async function goToPage(p) {
    page.value = Math.max(1, Math.min(p, totalPages.value));
    await fetch();
  }

  return {
    page,
    pageSize,
    items,
    total,
    loading,
    error,
    totalPages,
    hasNextPage,
    hasPrevPage,
    fetch,
    next,
    prev,
    goToPage,
  };
}
