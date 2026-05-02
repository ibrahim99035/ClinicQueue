<template>
  <div class="min-h-screen bg-slate-50 px-4 py-6 text-slate-900 dark:bg-slate-950 dark:text-slate-100 sm:px-6 lg:px-8">
    <div class="mx-auto max-w-5xl space-y-6">
      <div class="flex flex-col gap-4 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <button
            type="button"
            class="mb-4 inline-flex items-center rounded-xl border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-100 dark:border-slate-700 dark:text-slate-200 dark:hover:bg-slate-800"
            @click="goBack"
          >
            ← Back
          </button>

          <p class="text-sm font-medium text-blue-600 dark:text-blue-400">
            Medical Record
          </p>
          <h2 class="mt-1 text-2xl font-bold tracking-tight">
            Consultation Details
          </h2>
          <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">
            Review diagnosis, notes, prescriptions, and requested tests.
          </p>
        </div>

        <button
          v-if="consultation && canEditConsultation"
          type="button"
          class="inline-flex items-center justify-center rounded-xl bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-700"
          @click="goToEdit"
        >
          Edit Consultation
        </button>
      </div>

      <div
        v-if="loading"
        class="rounded-2xl border border-slate-200 bg-white p-10 text-center shadow-sm dark:border-slate-800 dark:bg-slate-900"
      >
        <div class="mx-auto mb-4 h-10 w-10 animate-spin rounded-full border-4 border-slate-200 border-t-blue-600 dark:border-slate-700 dark:border-t-blue-400"></div>
        <p class="text-sm font-medium text-slate-600 dark:text-slate-300">
          Loading consultation...
        </p>
      </div>

      <div
        v-if="error && !loading"
        class="rounded-2xl border border-red-200 bg-red-50 p-5 text-red-700 shadow-sm dark:border-red-900/60 dark:bg-red-950/40 dark:text-red-300"
      >
        <p class="text-sm font-semibold">
          {{ error }}
        </p>
      </div>

      <div v-if="consultation && !loading" class="space-y-6">
        <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <div class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
            <p class="text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
              Consultation ID
            </p>
            <p class="mt-2 text-lg font-bold">
              #{{ consultation.id }}
            </p>
          </div>

          <div class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
            <p class="text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
              Appointment ID
            </p>
            <p class="mt-2 text-lg font-bold">
              #{{ consultation.appointment_id }}
            </p>
          </div>

          <div
            v-if="consultation.created_by"
            class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900"
          >
            <p class="text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
              Created By
            </p>
            <p class="mt-2 text-lg font-bold">
              {{ consultation.created_by }}
            </p>
          </div>

          <div
            v-if="consultation.created_at"
            class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900"
          >
            <p class="text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
              Created
            </p>
            <p class="mt-2 text-sm font-semibold">
              {{ formatDate(consultation.created_at) }}
            </p>
          </div>
        </div>

        <div class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <div class="mb-5 border-b border-slate-200 pb-4 dark:border-slate-800">
            <h3 class="text-lg font-bold">
              Medical Information
            </h3>
            <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">
              Diagnosis and clinical notes recorded for this consultation.
            </p>
          </div>

          <div class="space-y-5">
            <div>
              <h4 class="mb-2 text-sm font-semibold text-slate-700 dark:text-slate-200">
                Diagnosis
              </h4>
              <div class="rounded-xl border border-slate-200 bg-slate-50 p-4 text-sm leading-6 text-slate-700 dark:border-slate-800 dark:bg-slate-950 dark:text-slate-200">
                {{ consultation.diagnosis || "—" }}
              </div>
            </div>

            <div>
              <h4 class="mb-2 text-sm font-semibold text-slate-700 dark:text-slate-200">
                Notes
              </h4>
              <div class="whitespace-pre-wrap rounded-xl border border-slate-200 bg-slate-50 p-4 text-sm leading-6 text-slate-700 dark:border-slate-800 dark:bg-slate-950 dark:text-slate-200">
                {{ consultation.notes || "—" }}
              </div>
            </div>
          </div>
        </div>

        <div
          v-if="consultation.prescription_items && consultation.prescription_items.length > 0"
          class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900"
        >
          <div class="mb-5 border-b border-slate-200 pb-4 dark:border-slate-800">
            <h3 class="text-lg font-bold">
              Prescriptions
            </h3>
            <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">
              Medication plan assigned during the consultation.
            </p>
          </div>

          <div class="grid gap-4 md:grid-cols-2">
            <div
              v-for="(item, index) in consultation.prescription_items"
              :key="`rx-${index}`"
              class="rounded-xl border border-slate-200 bg-slate-50 p-4 dark:border-slate-800 dark:bg-slate-950"
            >
              <div class="space-y-3">
                <div>
                  <p class="text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
                    Drug
                  </p>
                  <p class="mt-1 text-sm font-semibold">
                    {{ item.drug_name }}
                  </p>
                </div>

                <div>
                  <p class="text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
                    Dose
                  </p>
                  <p class="mt-1 text-sm">
                    {{ item.dose }}
                  </p>
                </div>

                <div>
                  <p class="text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
                    Duration
                  </p>
                  <p class="mt-1 text-sm">
                    {{ item.duration }}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div
          v-if="consultation.requested_tests && consultation.requested_tests.length > 0"
          class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900"
        >
          <div class="mb-5 border-b border-slate-200 pb-4 dark:border-slate-800">
            <h3 class="text-lg font-bold">
              Requested Tests
            </h3>
            <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">
              Lab or diagnostic tests requested by the doctor.
            </p>
          </div>

          <div class="grid gap-4 md:grid-cols-2">
            <div
              v-for="(test, index) in consultation.requested_tests"
              :key="`test-${index}`"
              class="rounded-xl border border-slate-200 bg-slate-50 p-4 dark:border-slate-800 dark:bg-slate-950"
            >
              <div class="space-y-3">
                <div>
                  <p class="text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
                    Test
                  </p>
                  <p class="mt-1 text-sm font-semibold">
                    {{ test.test_name }}
                  </p>
                </div>

                <div v-if="test.notes">
                  <p class="text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
                    Notes
                  </p>
                  <p class="mt-1 text-sm">
                    {{ test.notes }}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div
          v-if="(!consultation.prescription_items || consultation.prescription_items.length === 0) &&
            (!consultation.requested_tests || consultation.requested_tests.length === 0)"
          class="rounded-2xl border border-dashed border-slate-300 bg-white p-8 text-center shadow-sm dark:border-slate-700 dark:bg-slate-900"
        >
          <p class="text-sm font-medium text-slate-500 dark:text-slate-400">
            No prescriptions or tests requested.
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { getConsultationByAppointment } from "../../api/emr";

export default {
  name: "ConsultationDetails",
  data() {
    return {
      consultation: null,
      loading: true,
      error: "",
    };
  },
  computed: {
    canEditConsultation() {
      try {
        const roles = JSON.parse(localStorage.getItem("roles") || "[]");
        return roles.includes("Doctors");
      } catch (e) {
        return false;
      }
    },
  },
  mounted() {
    this.loadConsultation();
  },
  methods: {
    async loadConsultation() {
      this.loading = true;
      this.error = "";

      try {
        const appointmentId = this.$route.params.appointmentId;
        this.consultation = await getConsultationByAppointment(appointmentId);
      } catch (error) {
        if (error.response?.status === 403) {
          this.error = "You don't have permission to view this consultation.";
        } else if (error.response?.status === 404) {
          this.error = "Consultation not found.";
        } else if (error.response?.data?.detail) {
          this.error = error.response.data.detail;
        } else {
          this.error = error.message || "Failed to load consultation.";
        }
      } finally {
        this.loading = false;
      }
    },
    goBack() {
      if (window.history.length > 1) {
        this.$router.back();
        return;
      }

      try {
        const roles = JSON.parse(localStorage.getItem("roles") || "[]");

        if (roles.includes("Doctors")) {
          this.$router.push("/doctor");
        } else if (roles.includes("Patients")) {
          this.$router.push("/patient/appointments");
        } else {
          this.$router.push("/");
        }
      } catch (e) {
        this.$router.push("/");
      }
    },
    goToEdit() {
      if (this.consultation) {
        this.$router.push(`/emr/consultations/${this.consultation.id}/edit`);
      }
    },
    formatDate(dateString) {
      const date = new Date(dateString);
      return date.toLocaleString();
    },
  },
};
</script>