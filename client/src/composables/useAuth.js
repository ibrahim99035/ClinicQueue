import { useAuthStore } from "../stores/auth";
import { storeToRefs } from "pinia";

export default function useAuth() {
  const store = useAuthStore();
  const refs = storeToRefs(store);
  return {
    ...refs,
    login: store.login,
    logout: store.logout,
    refreshAccessToken: store.refreshAccessToken,
    getMe: store.getMe,
  };
}
