<template>
  <Teleport to="body">
    <Transition name="modal-overlay">
      <div
        v-if="modelValue"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
        @click.self="close"
      >
        <Transition name="modal-content">
          <div
            class="relative w-full max-w-md rounded-2xl border border-white/50 bg-white/95 shadow-2xl backdrop-blur"
          >
            <!-- Header -->
            <div class="flex items-center justify-between border-b border-gray-200 px-6 py-4">
              <h3 class="text-lg font-bold text-gray-900">
                <slot name="header">{{ title }}</slot>
              </h3>
              <button
                type="button"
                @click="close"
                class="rounded-lg p-1 text-gray-500 hover:bg-gray-100 transition-all duration-200"
              >
                ✕
              </button>
            </div>

            <!-- Content -->
            <div class="px-6 py-5">
              <slot />
            </div>

            <!-- Footer -->
            <div v-if="$slots.footer" class="border-t border-gray-200 px-6 py-4">
              <slot name="footer" />
            </div>
          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
defineProps({
  modelValue: {
    type: Boolean,
    required: true,
  },
  title: {
    type: String,
    default: "",
  },
});

const emit = defineEmits(["update:modelValue"]);

function close() {
  emit("update:modelValue", false);
}
</script>

<style scoped>
.modal-overlay-enter-active,
.modal-overlay-leave-active {
  transition: opacity 0.3s ease;
}

.modal-overlay-enter-from,
.modal-overlay-leave-to {
  opacity: 0;
}

.modal-content-enter-active,
.modal-content-leave-active {
  transition: all 0.3s ease;
}

.modal-content-enter-from,
.modal-content-leave-to {
  opacity: 0;
  transform: scale(0.95);
}
</style>
