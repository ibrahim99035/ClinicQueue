<template>
  <div class="page">
    <h2>Create Consultation</h2>

    <form @submit.prevent="submitConsultation">
      <!-- Diagnosis and Notes Section -->
      <div class="form-section">
        <h3>Medical Information</h3>
        
        <div class="form-group">
          <label for="diagnosis">Diagnosis *</label>
          <input 
            id="diagnosis"
            v-model="form.diagnosis" 
            type="text"
            placeholder="Enter diagnosis"
            required
          />
        </div>

        <div class="form-group">
          <label for="notes">Notes</label>
          <textarea 
            id="notes"
            v-model="form.notes"
            placeholder="Additional clinical notes"
            rows="4"
          ></textarea>
        </div>
      </div>

      <!-- Prescription Items Section -->
      <div class="form-section">
        <h3>Prescriptions</h3>
        
        <div v-if="form.prescription_items.length === 0" class="empty-state">
          No prescriptions added yet
        </div>

        <div
          v-for="(item, index) in form.prescription_items"
          :key="`prescription-${index}`"
          class="item-card"
        >
          <div class="item-fields">
            <div class="form-group">
              <label :for="`drug-${index}`">Drug Name</label>
              <input 
                :id="`drug-${index}`"
                v-model="item.drug_name" 
                type="text"
                placeholder="e.g., Paracetamol"
              />
            </div>

            <div class="form-group">
              <label :for="`dose-${index}`">Dose</label>
              <input 
                :id="`dose-${index}`"
                v-model="item.dose" 
                type="text"
                placeholder="e.g., 500 mg"
              />
            </div>

            <div class="form-group">
              <label :for="`duration-${index}`">Duration</label>
              <input 
                :id="`duration-${index}`"
                v-model="item.duration" 
                type="text"
                placeholder="e.g., 5 days"
              />
            </div>
          </div>

          <button type="button" @click="removePrescription(index)" class="btn btn-danger">
            Remove
          </button>
        </div>

        <button type="button" @click="addPrescription" class="btn btn-secondary">
          + Add Prescription
        </button>
      </div>

      <!-- Requested Tests Section -->
      <div class="form-section">
        <h3>Requested Tests</h3>

        <div v-if="form.requested_tests.length === 0" class="empty-state">
          No tests requested yet
        </div>

        <div
          v-for="(test, index) in form.requested_tests"
          :key="`test-${index}`"
          class="item-card"
        >
          <div class="item-fields">
            <div class="form-group">
              <label :for="`test-name-${index}`">Test Name</label>
              <input 
                :id="`test-name-${index}`"
                v-model="test.test_name" 
                type="text"
                placeholder="e.g., CBC"
              />
            </div>

            <div class="form-group">
              <label :for="`test-notes-${index}`">Notes</label>
              <input 
                :id="`test-notes-${index}`"
                v-model="test.notes" 
                type="text"
                placeholder="e.g., Check infection markers"
              />
            </div>
          </div>

          <button type="button" @click="removeTest(index)" class="btn btn-danger">
            Remove
          </button>
        </div>

        <button type="button" @click="addTest" class="btn btn-secondary">
          + Add Test
        </button>
      </div>

      <!-- Error Messages -->
      <div v-if="error" class="message error">
        {{ error }}
      </div>

      <!-- Form Actions -->
      <div class="form-actions">
        <button 
          type="submit" 
          :disabled="loading"
          class="btn btn-primary"
        >
          {{ loading ? "Creating..." : "Create Consultation" }}
        </button>
      </div>
    </form>
  </div>
</template>

<script>
import { createConsultation } from "../../api/emr";

export default {
  name: "ConsultationCreate",
  data() {
    return {
      loading: false,
      error: "",
      form: {
        appointment_id: parseInt(this.$route.params.appointmentId),
        diagnosis: "",
        notes: "",
        prescription_items: [],
        requested_tests: []
      }
    }
  },
  methods: {
    addPrescription() {
      this.form.prescription_items.push({
        drug_name: "",
        dose: "",
        duration: ""
      });
    },
    removePrescription(index) {
      this.form.prescription_items.splice(index, 1);
    },
    addTest() {
      this.form.requested_tests.push({
        test_name: "",
        notes: ""
      });
    },
    removeTest(index) {
      this.form.requested_tests.splice(index, 1);
    },
    async submitConsultation() {
      this.error = "";
      this.loading = true;

      try {
        const response = await createConsultation(this.form);
        const consultationId = response.data.id;
        
        this.$router.push(`/emr/consultations/${consultationId}/edit`);
      } catch (error) {
        if (error.response?.data) {
          const data = error.response.data;
          if (typeof data === 'object') {
            const messages = [];
            for (const [key, value] of Object.entries(data)) {
              if (Array.isArray(value)) {
                messages.push(`${key}: ${value.join(', ')}`);
              } else {
                messages.push(`${key}: ${value}`);
              }
            }
            this.error = messages.join('\n');
          } else {
            this.error = data.detail || data || "Failed to create consultation";
          }
        } else {
          this.error = error.message || "An unexpected error occurred";
        }
      } finally {
        this.loading = false;
      }
    }
  }
}
</script>

<style scoped>
.page {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

h2 {
  margin-bottom: 30px;
}

h3 {
  font-size: 18px;
  margin: 20px 0 15px 0;
}

form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-section {
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 20px;
  background: var(--bg);
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 15px;
}

.form-group:last-child {
  margin-bottom: 0;
}

label {
  font-weight: 500;
  color: var(--text-h);
  font-size: 14px;
}

input[type="text"],
input[type="email"],
textarea {
  padding: 10px;
  border: 1px solid var(--border);
  border-radius: 4px;
  font-family: var(--sans);
  font-size: 16px;
  background: var(--bg);
  color: var(--text-h);
}

input[type="text"]:focus,
textarea:focus {
  outline: none;
  border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-bg);
}

textarea {
  resize: vertical;
  min-height: 100px;
}

.item-card {
  border: 1px solid var(--border);
  border-radius: 4px;
  padding: 15px;
  margin-bottom: 10px;
  background: var(--code-bg);
}

.item-fields {
  display: grid;
  gap: 15px;
}

@media (min-width: 600px) {
  .item-fields {
    grid-template-columns: 1fr 1fr 1fr;
  }
}

.empty-state {
  color: var(--text);
  font-style: italic;
  padding: 15px;
  text-align: center;
  background: var(--code-bg);
  border-radius: 4px;
}

.message {
  padding: 15px;
  border-radius: 4px;
  border-left: 4px solid;
}

.message.error {
  background: rgba(220, 38, 38, 0.1);
  border-color: #dc2626;
  color: #991b1b;
  white-space: pre-wrap;
}

.message.success {
  background: rgba(34, 197, 94, 0.1);
  border-color: #22c55e;
  color: #166534;
}

.form-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  margin-top: 10px;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background: var(--accent);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  opacity: 0.9;
}

.btn-secondary {
  background: var(--border);
  color: var(--text-h);
}

.btn-secondary:hover:not(:disabled) {
  background: var(--accent-border);
}

.btn-danger {
  background: #ef4444;
  color: white;
  padding: 8px 12px;
  font-size: 14px;
}

.btn-danger:hover:not(:disabled) {
  background: #dc2626;
}
</style>
