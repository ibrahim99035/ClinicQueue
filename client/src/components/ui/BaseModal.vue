<template>
  <Teleport to="body">
    <Transition name="modal-overlay">
      <div
        v-if="modelValue"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm"
        @click.self="close"
      >
        <Transition name="modal-content">
          <div
            class="relative w-full max-w-md rounded border border-border bg-surface text-text1"
          >
            <!-- Header -->
            <div class="flex items-center justify-between border-b border-border px-4 py-4">
              <h3 class="font-sans font-semibold text-base text-text1">
                <slot name="header">{{ title }}</slot>
              </h3>
              <button
                type="button"
                @click="close"
                class="p-2 rounded bg-transparent text-text2 hover:text-text1 hover:bg-surface2 transition-all duration-150 cursor-pointer"
              >
                ✕
              </button>
            </div>

            <!-- Content -->
            <div class="px-4 py-4">
              <slot />
            </div>

            <!-- Footer -->
            <div v-if="$slots.footer" class="border-t border-border px-4 py-4">
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
