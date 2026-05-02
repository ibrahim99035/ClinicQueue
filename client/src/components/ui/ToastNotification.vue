<template>
  <div class="fixed top-4 right-4 z-50 flex flex-col gap-2 pointer-events-none">
    <transition-group name="toast" tag="div">
      <div
        v-for="toast in toasts"
        :key="toast.id"
        :class="[
          'pointer-events-auto rounded border px-4 py-3 font-sans text-sm',
          toastClasses[toast.type],
        ]"
      >
        {{ toast.message }}
      </div>
    </transition-group>
  </div>
</template>

<script setup>
import useToast from "../../composables/useToast.js";

const { toasts } = useToast();

const toastClasses = {
  success: "border-accent/40 bg-surface2 text-accent",
  error: "border-danger/40 bg-surface2 text-danger",
  info: "border-border bg-surface2 text-text1",
  warning: "border-yellow-400/40 bg-surface2 text-yellow-400",
};
</script>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(30px);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(30px);
}

.toast-move {
  transition: transform 0.3s ease;
}
</style>
