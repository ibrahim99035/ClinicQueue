import { ref } from "vue";

const toastMessage = ref("");
const toastType = ref("error");
let toastTimer = null;

export default function useToast() {
  function showToast(message, type = "error") {
    toastMessage.value = message;
    toastType.value = type;

    if (toastTimer) {
      clearTimeout(toastTimer);
    }

    toastTimer = setTimeout(() => {
      toastMessage.value = "";
    }, 30000);
  }

  function closeToast() {
    if (toastTimer) {
      clearTimeout(toastTimer);
    }

    toastMessage.value = "";
  }

  function success(message) {
    showToast(message, "success");
  }

  function error(message) {
    showToast(message, "error");
  }

  function info(message) {
    showToast(message, "info");
  }

  function warning(message) {
    showToast(message, "warning");
  }

  return {
    toastMessage,
    toastType,
    showToast,
    closeToast,
    success,
    error,
    info,
    warning,
  };
}
