import api from "./client";

function getListFromResponse(response) {
  const data = response.data;

  if (Array.isArray(data)) {
    return data;
  }

  if (Array.isArray(data.results)) {
    return data.results;
  }

  return [];
}

export async function getAppointments(params) {
  const response = await api.get("/appointments/appointments/", {
    params,
  });

  return getListFromResponse(response);
}

export async function getMyAppointments(params = {}) {
  const response = await api.get("/appointments/appointments/", {
    params,
  });
  return response.data;
}

export async function getAppointmentDetails(appointmentId) {
  const response = await api.get(
    "/appointments/appointments/" + appointmentId + "/"
  );

  return response.data;
}

export async function getAppointmentHistory(appointmentId) {
  const response = await api.get(
    "/appointments/appointments/" + appointmentId + "/history/"
  );

  return getListFromResponse(response);
}

export async function createAppointment(data) {
  const response = await api.post("/appointments/appointments/", data);
  return response.data;
}

export async function cancelAppointment(appointmentId) {
  const response = await api.post(
    `/appointments/appointments/${appointmentId}/cancel/`
  );
  return response.data;
}

export async function confirmAppointment(appointmentId) {
  const response = await api.post(
    `/appointments/appointments/${appointmentId}/confirm/`
  );
  return response.data;
}

export async function rescheduleAppointment(appointmentId, data) {
  const response = await api.post(
    `/appointments/appointments/${appointmentId}/reschedule/`,
    data
  );
  return response.data;
}

export async function checkInAppointment(appointmentId) {
  const response = await api.post(
    `/appointments/appointments/${appointmentId}/check_in/`
  );
  return response.data;
}

export async function markNoShowAppointment(appointmentId) {
  const response = await api.post(
    `/appointments/appointments/${appointmentId}/no_show/`
  );
  return response.data;
}

export async function markNoShow(appointmentId) {
  return markNoShowAppointment(appointmentId);
}

export async function completeAppointment(appointmentId) {
  const response = await api.post(
    `/appointments/appointments/${appointmentId}/complete/`
  );
  return response.data;
}

export async function getDoctorQueue() {
  const response = await api.get("/appointments/appointments/queue/");
  return response.data;
}

export async function joinWaitingList(data) {
  const response = await api.post("/appointments/waiting-list/", data);
  return response.data;
}

export async function getDoctorsList() {
  const response = await api.get("/accounts/doctors/");
  return getListFromResponse(response);
}
