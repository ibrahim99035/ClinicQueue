<script setup>
import useToast from "./composables/useToast";

const { toastMessage, toastType, closeToast } = useToast();
</script>

<template>
  <div>
    <div
      v-if="toastMessage"
      class="fixed top-6 right-6 z-[9999] w-[420px] rounded border px-4 py-4"
      :class="toastType === 'error'
        ? 'border-danger/40 bg-surface text-danger'
        : 'border-accent/40 bg-surface text-accent'"
    >
      <div class="flex items-start gap-3">
        <div class="flex-1">
          <p class="font-mono text-[11px] uppercase tracking-mono-wide">
            {{ toastType === "error" ? "Login Error" : "Success" }}
          </p>

          <p class="mt-1 font-sans text-sm text-text1">
            {{ toastMessage }}
          </p>

          <p class="mt-2 font-mono text-[10px] text-text3">
            This message will disappear after 30 seconds.
          </p>
        </div>

        <button
          type="button"
          class="p-2 rounded bg-transparent text-text2 hover:text-text1 hover:bg-surface2 transition-all duration-150 cursor-pointer"
          @click="closeToast"
        >
          ×
        </button>
      </div>
    </div>

    <router-view />
  </div>
</template>
