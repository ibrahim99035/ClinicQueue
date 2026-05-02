<script setup>
import { X, CheckCircle, AlertTriangle, Info } from "lucide-vue-next";

defineProps({
  message: {
    type: String,
    required: true,
  },
  type: {
    type: String,
    default: 'success',
    validator: (value) => ['success', 'error', 'info', 'warning'].includes(value),
  },
  show: {
    type: Boolean,
    default: false,
  }
});

defineEmits(['close']);

const typeConfig = {
  success: {
    classes: 'border-green-200 bg-green-50 text-green-800 dark:border-green-800 dark:bg-green-950/50 dark:text-green-300',
    icon: CheckCircle,
  },
  error: {
    classes: 'border-red-200 bg-red-50 text-red-800 dark:border-red-800 dark:bg-red-950/50 dark:text-red-300',
    icon: AlertTriangle,
  },
  warning: {
    classes: 'border-amber-200 bg-amber-50 text-amber-800 dark:border-amber-800 dark:bg-amber-950/50 dark:text-amber-300',
    icon: AlertTriangle,
  },
  info: {
    classes: 'border-blue-200 bg-blue-50 text-blue-800 dark:border-blue-800 dark:bg-blue-950/50 dark:text-blue-300',
    icon: Info,
  }
};
</script>

<template>
  <Transition name="toast-slide">
    <div
      v-if="show"
      class="fixed right-6 top-6 z-[9999] w-full max-w-sm rounded-2xl border p-4 shadow-xl"
      :class="typeConfig[type]?.classes"
    >
      <div class="flex items-start gap-3">
        <component :is="typeConfig[type]?.icon" class="mt-0.5 h-5 w-5 flex-shrink-0" />

        <div class="flex-1">
          <p class="text-sm font-bold">
            {{ type === 'success' ? 'Success' : type === 'error' ? 'Error' : type === 'warning' ? 'Warning' : 'Info' }}
          </p>
          <p class="mt-1 text-sm leading-6 opacity-90">
            {{ message }}
          </p>
        </div>

        <button
          type="button"
          @click="$emit('close')"
          class="flex h-6 w-6 items-center justify-center rounded-lg transition hover:opacity-70"
        >
          <X class="h-4 w-4" />
        </button>
      </div>
    </div>
  </Transition>
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
