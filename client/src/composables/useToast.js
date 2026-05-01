import { ref } from "vue";

const toasts = ref([]);
let toastId = 0;

export default function useToast() {
  function add(message, type = "info", duration = 3000) {
    const id = toastId++;
    const toast = { id, message, type };
    toasts.value.push(toast);

    if (duration > 0) {
      setTimeout(() => {
        remove(id);
      }, duration);
    }

    return id;
  }

  function remove(id) {
    toasts.value = toasts.value.filter((t) => t.id !== id);
  }

  function success(message, duration = 3000) {
    return add(message, "success", duration);
  }

  function error(message, duration = 4000) {
    return add(message, "error", duration);
  }

  function info(message, duration = 3000) {
    return add(message, "info", duration);
  }

  function warning(message, duration = 3000) {
    return add(message, "warning", duration);
  }

  return {
    toasts,
    add,
    remove,
    success,
    error,
    info,
    warning,
  };
}
