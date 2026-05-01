<template>
  <div class="page">
    <div class="header">
      <h2>Consultation Details</h2>
      <button v-if="consultation" class="btn btn-primary" @click="goToEdit">
        Edit Consultation
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <p>Loading consultation...</p>
    </div>

    <!-- Error State -->
    <div v-if="error && !loading" class="message error">
      {{ error }}
    </div>

    <!-- Consultation Content -->
    <div v-if="consultation && !loading" class="content">
      <!-- Basic Info -->
      <div class="info-section">
        <div class="info-row">
          <span class="label">Consultation ID:</span>
          <span class="value">{{ consultation.id }}</span>
        </div>
        <div class="info-row">
          <span class="label">Appointment ID:</span>
          <span class="value">{{ consultation.appointment_id }}</span>
        </div>
        <div v-if="consultation.created_by" class="info-row">
          <span class="label">Created By:</span>
          <span class="value">{{ consultation.created_by }}</span>
        </div>
        <div v-if="consultation.created_at" class="info-row">
          <span class="label">Created:</span>
          <span class="value">{{ formatDate(consultation.created_at) }}</span>
        </div>
      </div>

      <!-- Diagnosis and Notes -->
      <div class="data-section">
        <h3>Medical Information</h3>
        
        <div class="field-group">
          <h4>Diagnosis</h4>
          <p class="field-value">{{ consultation.diagnosis }}</p>
        </div>

        <div class="field-group">
          <h4>Notes</h4>
          <p class="field-value">{{ consultation.notes || '—' }}</p>
        </div>
      </div>

      <!-- Prescription Items -->
      <div v-if="consultation.prescription_items && consultation.prescription_items.length > 0" class="data-section">
        <h3>Prescriptions</h3>
        
        <div v-for="(item, index) in consultation.prescription_items" :key="`rx-${index}`" class="item-card">
          <div class="item-content">
            <div class="item-row">
              <span class="item-label">Drug:</span>
              <span class="item-value">{{ item.drug_name }}</span>
            </div>
            <div class="item-row">
              <span class="item-label">Dose:</span>
              <span class="item-value">{{ item.dose }}</span>
            </div>
            <div class="item-row">
              <span class="item-label">Duration:</span>
              <span class="item-value">{{ item.duration }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Requested Tests -->
      <div v-if="consultation.requested_tests && consultation.requested_tests.length > 0" class="data-section">
        <h3>Requested Tests</h3>
        
        <div v-for="(test, index) in consultation.requested_tests" :key="`test-${index}`" class="item-card">
          <div class="item-content">
            <div class="item-row">
              <span class="item-label">Test:</span>
              <span class="item-value">{{ test.test_name }}</span>
            </div>
            <div v-if="test.notes" class="item-row">
              <span class="item-label">Notes:</span>
              <span class="item-value">{{ test.notes }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty States -->
      <div v-if="(!consultation.prescription_items || consultation.prescription_items.length === 0) && 
                (!consultation.requested_tests || consultation.requested_tests.length === 0)" 
           class="empty-message">
        No prescriptions or tests requested
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

<style scoped>
.page {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  gap: 20px;
}

h2 {
  margin: 0;
  flex: 1;
}

.loading-state {
  padding: 40px 20px;
  text-align: center;
  color: var(--text);
}

.message {
  padding: 15px;
  border-radius: 4px;
  border-left: 4px solid;
  margin-bottom: 20px;
}

.message.error {
  background: rgba(220, 38, 38, 0.1);
  border-color: #dc2626;
  color: #991b1b;
}

.content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.info-section {
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 15px;
  background: var(--code-bg);
}

.info-row {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid var(--border);
}

.info-row:last-child {
  border-bottom: none;
}

.label {
  font-weight: 500;
  color: var(--text-h);
  min-width: 150px;
}

.value {
  color: var(--text);
  text-align: right;
}

.data-section {
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 20px;
  background: var(--bg);
}

h3 {
  font-size: 18px;
  margin: 0 0 15px 0;
  color: var(--text-h);
}

.field-group {
  margin-bottom: 20px;
}

.field-group:last-child {
  margin-bottom: 0;
}

h4 {
  font-size: 14px;
  margin: 0 0 8px 0;
  color: var(--text-h);
  font-weight: 500;
}

.field-value {
  margin: 0;
  color: var(--text);
  padding: 10px;
  background: var(--code-bg);
  border-radius: 4px;
  border: 1px solid var(--border);
  white-space: pre-wrap;
}

.item-card {
  border: 1px solid var(--border);
  border-radius: 4px;
  padding: 15px;
  margin-bottom: 10px;
  background: var(--code-bg);
}

.item-card:last-child {
  margin-bottom: 0;
}

.item-content {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.item-row {
  display: flex;
  gap: 15px;
}

.item-label {
  font-weight: 500;
  color: var(--text-h);
  min-width: 100px;
}

.item-value {
  color: var(--text);
  flex: 1;
}

.empty-message {
  padding: 30px;
  text-align: center;
  color: var(--text);
  font-style: italic;
  border: 1px solid var(--border);
  border-radius: 6px;
  background: var(--code-bg);
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

.btn-primary {
  background: var(--accent);
  color: white;
}

.btn-primary:hover {
  opacity: 0.9;
}
</style>
