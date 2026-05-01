import { defineStore } from "pinia";
import * as analyticsApi from "../api/analytics";

function normalizeListResponse(payload) {
  if (Array.isArray(payload)) {
    return payload;
  }

  if (Array.isArray(payload?.results)) {
    return payload.results;
  }

  return [];
}

/** Maps nested admin-overview JSON to flat fields used by AdminAnalytics.vue */
function flattenAdminOverview(payload) {
  if (!payload || typeof payload !== "object") {
    return {};
  }
  const u = payload.users || {};
  const d = payload.doctors || {};
  const a = payload.appointments || {};
  const w = payload.waiting_list || {};
  const r = payload.rates || {};
  return {
    nested: payload,
    total_users: u.total ?? 0,
    active_users: u.active ?? 0,
    inactive_users: u.inactive ?? 0,
    pending_doctors: d.pending ?? 0,
    waiting_list: w.total ?? 0,
    total_appointments: a.total ?? 0,
    completion_rate: r.completion_rate ?? 0,
    cancellation_rate: r.cancellation_rate ?? 0,
    no_show_rate: r.no_show_rate ?? 0,
  };
}

export const useAnalyticsStore = defineStore("analytics", {
  state: () => ({
    overview: {},
    appointmentsByStatus: [],
    appointmentsByMonth: [],
    topSpecializations: [],
    doctorPerformance: [],
    loading: false,
    error: null,
    lastLoadedAt: null,
  }),
  getters: {
    hasData: (state) =>
      Boolean(
        state.lastLoadedAt ||
          state.appointmentsByStatus.length ||
          state.appointmentsByMonth.length ||
          state.doctorPerformance.length
      ),
  },
  actions: {
    async loadAnalytics() {
      this.loading = true;
      this.error = null;

      try {
        const [overview, byStatus, byMonth, topSpecializations, doctorPerformance] =
          await Promise.all([
            analyticsApi.getAdminOverview(),
            analyticsApi.getAppointmentsByStatus(),
            analyticsApi.getAppointmentsByMonth(),
            analyticsApi.getTopSpecializations(),
            analyticsApi.getDoctorPerformance(),
          ]);

        this.overview = flattenAdminOverview(overview);
        this.appointmentsByStatus = normalizeListResponse(byStatus);
        this.appointmentsByMonth = normalizeListResponse(byMonth);
        this.topSpecializations = normalizeListResponse(topSpecializations);
        this.doctorPerformance = normalizeListResponse(doctorPerformance);
        this.lastLoadedAt = new Date().toISOString();
      } catch (error) {
        this.overview = {};
        this.appointmentsByStatus = [];
        this.appointmentsByMonth = [];
        this.topSpecializations = [];
        this.doctorPerformance = [];
        this.lastLoadedAt = null;
        this.error =
          error?.response?.data?.detail || error?.message || "Failed to load analytics data";
      } finally {
        this.loading = false;
      }
    },

    clearError() {
      this.error = null;
    },
  },
});