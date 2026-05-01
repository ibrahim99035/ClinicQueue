<script setup>
import useToast from "./composables/useToast";

const { toastMessage, toastType, closeToast } = useToast();
</script>

<template>
  <div>
    <div
      v-if="toastMessage"
      class="fixed top-6 right-6 z-[9999] w-[420px] rounded-xl border px-5 py-4 shadow-xl"
      :class="toastType === 'error'
        ? 'border-red-200 bg-red-50 text-red-700'
        : 'border-green-200 bg-green-50 text-green-700'"
    >
      <div class="flex items-start gap-3">
        <div class="flex-1">
          <p class="font-bold">
            {{ toastType === "error" ? "Login Error" : "Success" }}
          </p>

          <p class="mt-1 text-sm leading-relaxed">
            {{ toastMessage }}
          </p>

          <p class="mt-2 text-xs opacity-70">
            This message will disappear after 30 seconds.
          </p>
        </div>

        <button
          type="button"
          class="text-xl font-bold opacity-70 hover:opacity-100"
          @click="closeToast"
        >
          ×
        </button>
      </div>
    </div>

    <router-view />
  </div>
</template>
