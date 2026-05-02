<script setup>
import { X, CheckCircle, AlertTriangle } from "lucide-vue-next";
import useToast from "./composables/useToast";

const { toastMessage, toastType, closeToast } = useToast();
</script>

<template>
  <div class="min-h-screen bg-slate-50 text-slate-900 dark:bg-slate-950 dark:text-slate-100">
    <!-- Global Toast -->
    <Transition name="toast-slide">
      <div
        v-if="toastMessage"
        class="fixed top-6 right-6 z-[9999] w-full max-w-sm rounded-2xl border p-4 shadow-xl"
        :class="toastType === 'error'
          ? 'border-red-200 bg-red-50 text-red-800 dark:border-red-800 dark:bg-red-950/50 dark:text-red-300'
          : 'border-green-200 bg-green-50 text-green-800 dark:border-green-800 dark:bg-green-950/50 dark:text-green-300'"
      >
        <div class="flex items-start gap-3">
          <component :is="toastType === 'error' ? AlertTriangle : CheckCircle" class="mt-0.5 h-5 w-5 flex-shrink-0" />

          <div class="flex-1">
            <p class="text-sm font-bold">
              {{ toastType === "error" ? "Error" : "Success" }}
            </p>

            <p class="mt-1 text-sm leading-6 opacity-90">
              {{ toastMessage }}
            </p>
          </div>

          <button
            type="button"
            class="flex h-6 w-6 items-center justify-center rounded-lg transition hover:opacity-70"
            @click="closeToast"
          >
            <X class="h-4 w-4" />
          </button>
        </div>
      </div>
    </Transition>

    <router-view />
  </div>
</template>

<style scoped>
.toast-slide-enter-active,
.toast-slide-leave-active {
  transition: all 0.25s ease;
}

.toast-slide-enter-from,
.toast-slide-leave-to {
  opacity: 0;
  transform: translateX(30px);
}
</style>
