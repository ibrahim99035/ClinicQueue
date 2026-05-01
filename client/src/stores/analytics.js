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

        this.overview = overview || {};
        this.appointmentsByStatus = normalizeListResponse(byStatus);
        this.appointmentsByMonth = normalizeListResponse(byMonth);
        this.topSpecializations = normalizeListResponse(topSpecializations);
        this.doctorPerformance = normalizeListResponse(doctorPerformance);
        this.lastLoadedAt = new Date().toISOString();
      } catch (error) {
        this.error = error?.response?.data?.detail || error?.message || "Failed to load analytics data";
        throw error;
      } finally {
        this.loading = false;
      }
    },

    clearError() {
      this.error = null;
    },
  },
});