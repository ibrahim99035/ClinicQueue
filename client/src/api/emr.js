import api from "./http";

export function createConsultation(payload){
    return api.post("/emr/consultations/", payload);
}

export function updateConsultation(consultationId, payload) {
  return api.put(`/emr/consultations/${consultationId}/`, payload);
}

export function getConsultationByAppointment(appointmentId){
    return api.get(`/emr/consultations/by-appointment/${appointmentId}`)
}

export function getConsultationById(consultationId) {
  // TODO: Backend needs to support GET /emr/consultations/{id}/ endpoint
  // Currently only PUT is supported on this route. Add a GET method
  // to retrieve a single consultation by its ID for editing purposes.
  return api.get(`/emr/consultations/${consultationId}/`);
}