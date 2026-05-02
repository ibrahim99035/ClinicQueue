import { computed, ref } from "vue";

const theme = ref(localStorage.getItem("theme") || "light");

function applyTheme() {
  if (theme.value === "dark") {
    document.documentElement.classList.add("dark");
  } else {
    document.documentElement.classList.remove("dark");
  }

  localStorage.setItem("theme", theme.value);
}

function setTheme(value) {
  theme.value = value === "dark" ? "dark" : "light";
  applyTheme();
}

function toggleTheme() {
  setTheme(theme.value === "dark" ? "light" : "dark");
}

const isDark = computed(() => theme.value === "dark");

applyTheme();

export default function useTheme() {
  return {
    theme,
    isDark,
    toggleTheme,
    setTheme,
    applyTheme,
  };
}
