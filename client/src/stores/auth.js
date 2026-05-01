import { defineStore } from "pinia";
import api from "../api/client";
import * as authApi from "../api/auth";

export const useAuthStore = defineStore("auth", {
  state: () => ({
    user: null,
    access: localStorage.getItem("access") || null,
    refresh: localStorage.getItem("refresh") || null,
    roles: (() => {
      try {
        return JSON.parse(localStorage.getItem("roles") || "[]");
      } catch (e) {
        return [];
      }
    })(),
  }),
  getters: {
    isAuthenticated: (state) => !!state.access,
    isPatient: (state) => state.roles.includes("Patients"),
    isDoctor: (state) => state.roles.includes("Doctors"),
    isReceptionist: (state) => state.roles.includes("Receptionists"),
    isAdmin: (state) => state.roles.includes("Admins"),
  },
  actions: {
    setAuthData({ access, refresh, user, roles }) {
      this.access = access;
      this.refresh = refresh;
      this.user = user || null;
      this.roles = roles || [];

      if (access) localStorage.setItem("access", access);
      if (refresh) localStorage.setItem("refresh", refresh);
      if (user) localStorage.setItem("user", JSON.stringify(user));
      if (roles) localStorage.setItem("roles", JSON.stringify(roles));
    },

    clearAuth() {
      this.user = null;
      this.access = null;
      this.refresh = null;
      this.roles = [];
      localStorage.removeItem("access");
      localStorage.removeItem("refresh");
      localStorage.removeItem("user");
      localStorage.removeItem("roles");
    },

    async login(email, password) {
      const response = await authApi.loginUser({ email, password });
      const data = response.data;
      // backend expected to return { access, refresh, user, roles }
      this.setAuthData({ access: data.access, refresh: data.refresh, user: data.user, roles: data.roles || [] });
      return data;
    },

    logout() {
      this.clearAuth();
    },

    async refreshAccessToken() {
      if (!this.refresh) {
        this.logout();
        return null;
      }
      try {
        const res = await api.post("/accounts/token/refresh/", { refresh: this.refresh });
        const newAccess = res.data.access;
        this.access = newAccess;
        localStorage.setItem("access", newAccess);
        return newAccess;
      } catch (err) {
        this.logout();
        return null;
      }
    },

    async getMe() {
      try {
        const res = await api.get("/accounts/profile/");
        this.user = res.data;
        // try to keep roles synced if returned here
        if (res.data.roles) {
          this.roles = res.data.roles;
          localStorage.setItem("roles", JSON.stringify(res.data.roles));
        }
        return res.data;
      } catch (err) {
        return null;
      }
    },
  },
});
