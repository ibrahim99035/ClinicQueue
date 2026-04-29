import api from "./http";

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