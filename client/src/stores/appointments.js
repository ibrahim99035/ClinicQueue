import { defineStore } from "pinia";
import * as appointmentApi from "../api/appointments";

export const useAppointmentsStore = defineStore("appointments", {
  state: () => ({
    list: [],
    total: 0,
    loading: false,
    error: null,
    filters: {
      page: 1,
      pageSize: 10,
      status: null,
    },
  }),
  getters: {
    sortedList: (state) => state.list,
    isEmpty: (state) => state.list.length === 0 && !state.loading,
  },
  actions: {
    async fetchAppointments(params = {}) {
      this.loading = true;
      this.error = null;
      try {
        const response = await appointmentApi.getAppointments({
          ...this.filters,
          ...params,
        });
        this.list = Array.isArray(response) ? response : response.results || [];
        this.total = response.count || this.list.length;
      } catch (err) {
        this.error = err.message || "Failed to fetch appointments";
      } finally {
        this.loading = false;
      }
    },

    async getAppointmentDetails(appointmentId) {
      try {
        return await appointmentApi.getAppointmentDetails(appointmentId);
      } catch (err) {
        this.error = err.message || "Failed to fetch appointment details";
        return null;
      }
    },

    async createAppointment(data) {
      this.loading = true;
      this.error = null;
      try {
        const result = await appointmentApi.createAppointment(data);
        await this.fetchAppointments();
        return result;
      } catch (err) {
        this.error = err.message || "Failed to create appointment";
        throw err;
      } finally {
        this.loading = false;
      }
    },

    async cancelAppointment(appointmentId) {
      this.loading = true;
      this.error = null;
      try {
        const result = await appointmentApi.cancelAppointment(appointmentId);
        await this.fetchAppointments();
        return result;
      } catch (err) {
        this.error = err.message || "Failed to cancel appointment";
        throw err;
      } finally {
        this.loading = false;
      }
    },

    async rescheduleAppointment(appointmentId, data) {
      this.loading = true;
      this.error = null;
      try {
        const result = await appointmentApi.rescheduleAppointment(
          appointmentId,
          data
        );
        await this.fetchAppointments();
        return result;
      } catch (err) {
        this.error = err.message || "Failed to reschedule appointment";
        throw err;
      } finally {
        this.loading = false;
      }
    },

    async checkInAppointment(appointmentId) {
      try {
        return await appointmentApi.checkInAppointment(appointmentId);
      } catch (err) {
        this.error = err.message || "Failed to check in";
        throw err;
      }
    },

    async markNoShowAppointment(appointmentId) {
      try {
        return await appointmentApi.markNoShowAppointment(appointmentId);
      } catch (err) {
        this.error = err.message || "Failed to mark no-show";
        throw err;
      }
    },

    async completeAppointment(appointmentId) {
      try {
        return await appointmentApi.completeAppointment(appointmentId);
      } catch (err) {
        this.error = err.message || "Failed to complete appointment";
        throw err;
      }
    },

    setFilters(filters) {
      this.filters = { ...this.filters, ...filters };
    },

    clearError() {
      this.error = null;
    },
  },
});
