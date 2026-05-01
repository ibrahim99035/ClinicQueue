<template>
  <div class="mx-auto max-w-5xl space-y-6 p-6">
    <PageHeader
      title="Edit Consultation"
      subtitle="Update diagnosis, notes, prescriptions, and requested tests."
      :badge="consultation ? `#${consultation.id}` : null"
      badgeColor="blue"
    />

    <div v-if="loading" class="rounded-2xl border border-slate-200 bg-white p-6 text-center text-sm text-slate-600 shadow-sm">
      Loading consultation...
    </div>

    <div v-else-if="error" class="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
      {{ error }}
    </div>

    <template v-else-if="consultation">
      <div v-if="successMessage" class="rounded-xl border border-green-200 bg-green-50 px-4 py-3 text-sm text-green-700">
        {{ successMessage }}
      </div>

      <div class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div class="mb-6 grid gap-3 text-sm text-slate-600 md:grid-cols-2">
          <div><span class="font-semibold text-slate-900">Appointment:</span> #{{ consultation.appointment_id }}</div>
          <div><span class="font-semibold text-slate-900">Created:</span> {{ formatDate(consultation.created_at) }}</div>
        </div>

        <form class="space-y-6" @submit.prevent="submitUpdate">
          <section class="space-y-4">
            <div>
              <h3 class="text-lg font-bold text-slate-900">Medical Information</h3>
            </div>

            <div class="grid gap-4">
              <div>
                <label class="mb-1.5 block text-sm font-semibold text-slate-700">Diagnosis *</label>
                <input
                  v-model.trim="form.diagnosis"
                  type="text"
                  required
                  class="w-full rounded-xl border border-slate-300 px-3 py-2.5 text-sm outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                />
              </div>

              <div>
                <label class="mb-1.5 block text-sm font-semibold text-slate-700">Notes</label>
                <textarea
                  v-model="form.notes"
                  rows="4"
                  class="w-full rounded-xl border border-slate-300 px-3 py-2.5 text-sm outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                />
              </div>
            </div>
          </section>

          <section class="space-y-4">
            <div class="flex items-center justify-between gap-4">
              <div>
                <h3 class="text-lg font-bold text-slate-900">Prescriptions</h3>
              </div>

              <button type="button" class="rounded-xl bg-slate-100 px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-200" @click="addPrescription">
                + Add Prescription
              </button>
            </div>

            <div v-if="form.prescription_items.length === 0" class="rounded-xl border border-dashed border-slate-300 bg-slate-50 px-4 py-5 text-sm text-slate-500">
              No prescriptions added yet.
            </div>

            <div v-for="(item, index) in form.prescription_items" :key="item.id ?? `prescription-${index}`" class="rounded-2xl border border-slate-200 bg-slate-50 p-4">
              <div class="grid gap-4 md:grid-cols-3">
                <div>
                  <label class="mb-1.5 block text-sm font-semibold text-slate-700">Drug Name</label>
                  <input v-model.trim="item.drug_name" type="text" class="w-full rounded-xl border border-slate-300 px-3 py-2.5 text-sm outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100" />
                </div>

                <div>
                  <label class="mb-1.5 block text-sm font-semibold text-slate-700">Dose</label>
                  <input v-model.trim="item.dose" type="text" class="w-full rounded-xl border border-slate-300 px-3 py-2.5 text-sm outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100" />
                </div>

                <div>
                  <label class="mb-1.5 block text-sm font-semibold text-slate-700">Duration</label>
                  <input v-model.trim="item.duration" type="text" class="w-full rounded-xl border border-slate-300 px-3 py-2.5 text-sm outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100" />
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
              </div>

              <button type="button" class="rounded-xl bg-slate-100 px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-200" @click="addTest">
                + Add Test
              </button>
            </div>

            <div v-if="form.requested_tests.length === 0" class="rounded-xl border border-dashed border-slate-300 bg-slate-50 px-4 py-5 text-sm text-slate-500">
              No tests requested yet.
            </div>

            <div v-for="(test, index) in form.requested_tests" :key="test.id ?? `test-${index}`" class="rounded-2xl border border-slate-200 bg-slate-50 p-4">
              <div class="grid gap-4 md:grid-cols-2">
                <div>
                  <label class="mb-1.5 block text-sm font-semibold text-slate-700">Test Name</label>
                  <input v-model.trim="test.test_name" type="text" class="w-full rounded-xl border border-slate-300 px-3 py-2.5 text-sm outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100" />
                </div>

                <div>
                  <label class="mb-1.5 block text-sm font-semibold text-slate-700">Notes</label>
                  <input v-model.trim="test.notes" type="text" class="w-full rounded-xl border border-slate-300 px-3 py-2.5 text-sm outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100" />
                </div>
              </div>

              <div class="mt-3 flex justify-end">
                <button type="button" class="rounded-xl bg-red-100 px-4 py-2 text-sm font-semibold text-red-700 transition hover:bg-red-200" @click="removeTest(index)">
                  Remove
                </button>
              </div>
            </div>
          </section>

          <div v-if="error && !loading" class="whitespace-pre-wrap rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            {{ error }}
          </div>

          <div class="flex justify-end gap-3">
            <button type="button" class="rounded-xl bg-slate-100 px-5 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-200" @click="resetToLoaded">
              Reset
            </button>
            <button type="submit" class="rounded-xl bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-slate-400" :disabled="updating">
              {{ updating ? "Saving..." : "Save Changes" }}
            </button>
          </div>
        </form>
      </div>
    </template>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from "vue";
import { useRoute } from "vue-router";
import PageHeader from "../../components/PageHeader.vue";
import { getConsultationById, updateConsultation } from "../../api/emr";

const route = useRoute();

const loading = ref(true);
const updating = ref(false);
const error = ref("");
const successMessage = ref("");
const consultation = ref(null);

const form = reactive({
  diagnosis: "",
  notes: "",
  prescription_items: [],
  requested_tests: [],
});

function cloneArray(items) {
  return Array.isArray(items) ? items.map((item) => ({ ...item })) : [];
}

function applyConsultationToForm(record) {
  consultation.value = record;
  form.diagnosis = record?.diagnosis || "";
  form.notes = record?.notes || "";
  form.prescription_items = cloneArray(record?.prescription_items);
  form.requested_tests = cloneArray(record?.requested_tests);
}

function resetToLoaded() {
  if (consultation.value) {
    applyConsultationToForm(consultation.value);
  }
}

function addPrescription() {
  form.prescription_items.push({ drug_name: "", dose: "", duration: "" });
}

function removePrescription(index) {
  form.prescription_items.splice(index, 1);
}

function addTest() {
  form.requested_tests.push({ test_name: "", notes: "" });
}

function removeTest(index) {
  form.requested_tests.splice(index, 1);
}

function formatDate(value) {
  if (!value) return "-";
  return new Date(value).toLocaleString();
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

  return messages.length ? messages.join("\n") : "Failed to update consultation";
}

async function loadConsultation() {
  loading.value = true;
  error.value = "";

  try {
    const consultationId = route.params.consultationId;
    const record = await getConsultationById(consultationId);
    applyConsultationToForm(record);
  } catch (err) {
    error.value = normalizeApiError(err);
  } finally {
    loading.value = false;
  }
}

async function submitUpdate() {
  updating.value = true;
  error.value = "";
  successMessage.value = "";

  try {
    const payload = {
      diagnosis: form.diagnosis,
      notes: form.notes,
      prescription_items: form.prescription_items.filter(
        (item) => item.drug_name || item.dose || item.duration,
      ),
      requested_tests: form.requested_tests.filter(
        (item) => item.test_name || item.notes,
      ),
    };

    const consultationId = route.params.consultationId;
    const record = await updateConsultation(consultationId, payload);
    applyConsultationToForm(record);
    successMessage.value = "Consultation updated successfully.";
  } catch (err) {
    error.value = normalizeApiError(err);
  } finally {
    updating.value = false;
  }
}

onMounted(loadConsultation);
</script>