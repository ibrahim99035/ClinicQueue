<template>
  <div class="mx-auto max-w-5xl space-y-6 p-6">
    <div class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
  <div class="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
    <div>
      <h1 class="text-2xl font-bold text-slate-900">
        Create Consultation
      </h1>

      <p class="mt-2 text-sm text-slate-500">
        Document diagnosis, prescriptions, and requested tests for a checked-in appointment.
      </p>
    </div>

    <button
      type="button"
      @click="goBack"
      class="rounded-xl border border-slate-300 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-100"
    >
      Back
    </button>
  </div>
</div>

    <div class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <form class="space-y-6" @submit.prevent="submitConsultation">
        <section class="space-y-4">
          <div>
            <h3 class="text-lg font-bold text-slate-900">Medical Information</h3>
            <p class="mt-1 text-sm text-slate-500">Capture the key diagnosis and notes.</p>
          </div>

          <div class="grid gap-4">
            <div>
              <label class="mb-1.5 block text-sm font-semibold text-slate-700">Diagnosis *</label>
              <input
                v-model.trim="form.diagnosis"
                type="text"
                required
                placeholder="Enter diagnosis"
                class="w-full rounded-xl border border-slate-300 px-3 py-2.5 text-sm outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
              />
            </div>

            <div>
              <label class="mb-1.5 block text-sm font-semibold text-slate-700">Notes</label>
              <textarea
                v-model="form.notes"
                rows="4"
                placeholder="Additional clinical notes"
                class="w-full rounded-xl border border-slate-300 px-3 py-2.5 text-sm outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
              />
            </div>
          </div>
        </section>

        <section class="space-y-4">
          <div class="flex items-center justify-between gap-4">
            <div>
              <h3 class="text-lg font-bold text-slate-900">Prescriptions</h3>
              <p class="mt-1 text-sm text-slate-500">Add or remove drugs to prescribe.</p>
            </div>

            <button type="button" class="rounded-xl bg-slate-100 px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-200" @click="addPrescription">
              + Add Prescription
            </button>
          </div>

          <div v-if="form.prescription_items.length === 0" class="rounded-xl border border-dashed border-slate-300 bg-slate-50 px-4 py-5 text-sm text-slate-500">
            No prescriptions added yet.
          </div>

          <div v-for="(item, index) in form.prescription_items" :key="`prescription-${index}`" class="rounded-2xl border border-slate-200 bg-slate-50 p-4">
            <div class="grid gap-4 md:grid-cols-3">
              <div>
                <label class="mb-1.5 block text-sm font-semibold text-slate-700">Drug Name</label>
                <input v-model.trim="item.drug_name" type="text" placeholder="e.g., Paracetamol" class="w-full rounded-xl border border-slate-300 px-3 py-2.5 text-sm outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100" />
              </div>

              <div>
                <label class="mb-1.5 block text-sm font-semibold text-slate-700">Dose</label>
                <input v-model.trim="item.dose" type="text" placeholder="e.g., 500 mg" class="w-full rounded-xl border border-slate-300 px-3 py-2.5 text-sm outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100" />
              </div>

              <div>
                <label class="mb-1.5 block text-sm font-semibold text-slate-700">Duration</label>
                <input v-model.trim="item.duration" type="text" placeholder="e.g., 5 days" class="w-full rounded-xl border border-slate-300 px-3 py-2.5 text-sm outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100" />
              </div>
            </div>

            <div class="mt-3 flex justify-end">
              <button type="button" class="rounded-xl bg-red-100 px-4 py-2 text-sm font-semibold text-red-700 transition hover:bg-red-200" @click="removePrescription(index)">
                Remove
              </button>
            </div>
          </div>
        </section>

        <section class="space-y-4">
          <div class="flex items-center justify-between gap-4">
            <div>
              <h3 class="text-lg font-bold text-slate-900">Requested Tests</h3>
              <p class="mt-1 text-sm text-slate-500">Add lab or imaging requests.</p>
            </div>

            <button type="button" class="rounded-xl bg-slate-100 px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-200" @click="addTest">
              + Add Test
            </button>
          </div>

          <div v-if="form.requested_tests.length === 0" class="rounded-xl border border-dashed border-slate-300 bg-slate-50 px-4 py-5 text-sm text-slate-500">
            No tests requested yet.
          </div>

          <div v-for="(test, index) in form.requested_tests" :key="`test-${index}`" class="rounded-2xl border border-slate-200 bg-slate-50 p-4">
            <div class="grid gap-4 md:grid-cols-2">
              <div>
                <label class="mb-1.5 block text-sm font-semibold text-slate-700">Test Name</label>
                <input v-model.trim="test.test_name" type="text" placeholder="e.g., CBC" class="w-full rounded-xl border border-slate-300 px-3 py-2.5 text-sm outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100" />
              </div>

              <div>
                <label class="mb-1.5 block text-sm font-semibold text-slate-700">Notes</label>
                <input v-model.trim="test.notes" type="text" placeholder="e.g., Check infection markers" class="w-full rounded-xl border border-slate-300 px-3 py-2.5 text-sm outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100" />
              </div>
            </div>

            <div class="mt-3 flex justify-end">
              <button type="button" class="rounded-xl bg-red-100 px-4 py-2 text-sm font-semibold text-red-700 transition hover:bg-red-200" @click="removeTest(index)">
                Remove
              </button>
            </div>
          </div>
        </section>

        <div v-if="error" class="whitespace-pre-wrap rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {{ error }}
        </div>

        <div class="flex justify-end gap-3">
          <button type="button" class="rounded-xl bg-slate-100 px-5 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-200" @click="resetForm" :disabled="loading">
            Reset
          </button>
          <button type="submit" class="rounded-xl bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-slate-400" :disabled="loading">
            {{ loading ? "Creating..." : "Create Consultation" }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from "vue";
import { useRoute, useRouter } from "vue-router";

import { createConsultation } from "../../api/emr";

const route = useRoute();
const router = useRouter();

const loading = ref(false);
const error = ref("");

const form = reactive({
  appointment_id: Number(route.params.appointmentId),
  diagnosis: "",
  notes: "",
  prescription_items: [],
  requested_tests: [],
});

function goBack() {
  if (window.history.length > 1) {
    router.back();
    return;
  }

  router.push("/doctor/queue");
}

function addPrescription() {
  form.prescription_items.push({
    drug_name: "",
    dose: "",
    duration: "",
  });
}

function removePrescription(index) {
  form.prescription_items.splice(index, 1);
}

function addTest() {
  form.requested_tests.push({
    test_name: "",
    notes: "",
  });
}

function removeTest(index) {
  form.requested_tests.splice(index, 1);
}

function resetForm() {
  error.value = "";
  form.diagnosis = "";
  form.notes = "";
  form.prescription_items = [];
  form.requested_tests = [];
}

function normalizeApiError(err) {
  const data = err?.response?.data;

  if (!data) {
    return err?.message || "An unexpected error occurred";
  }

  if (typeof data === "string") {
    return data;
  }

  if (data.detail) {
    return data.detail;
  }

  const messages = [];

  for (const [key, value] of Object.entries(data)) {
    if (Array.isArray(value)) {
      messages.push(`${key}: ${value.join(", ")}`);
    } else if (value) {
      messages.push(`${key}: ${value}`);
    }
  }

  return messages.length ? messages.join("\n") : "Failed to create consultation";
}

async function submitConsultation() {
  loading.value = true;
  error.value = "";

  try {
    const payload = {
      appointment_id: form.appointment_id,
      diagnosis: form.diagnosis,
      notes: form.notes,
      prescription_items: form.prescription_items.filter(
        (item) => item.drug_name || item.dose || item.duration,
      ),
      requested_tests: form.requested_tests.filter(
        (item) => item.test_name || item.notes,
      ),
    };

    const consultation = await createConsultation(payload);
    router.push(`/emr/consultations/${consultation.id}/edit`);
  } catch (err) {
    error.value = normalizeApiError(err);
  } finally {
    loading.value = false;
  }
}
</script>