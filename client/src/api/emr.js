import api from "./client";

function normalizeListResponse(response) {
  const data = response.data;

  if (Array.isArray(data)) {
    return data;
  }

  if (Array.isArray(data.results)) {
    return data.results;
  }

  return [];
}

export async function listConsultations(params) {
  const response = await api.get("/emr/consultations/", { params });
  return normalizeListResponse(response);
}

export async function createConsultation(payload) {
  const response = await api.post("/emr/consultations/", payload);
  return response.data;
}

export async function updateConsultation(consultationId, payload) {
  const response = await api.put(`/emr/consultations/${consultationId}/`, payload);
  return response.data;
}

export async function getConsultationByAppointment(appointmentId) {
  const response = await api.get(`/emr/consultations/by-appointment/${appointmentId}/`);
  return response.data;
}

export async function getConsultationById(consultationId) {
  const response = await api.get(`/emr/consultations/${consultationId}/`);
  return response.data;
}