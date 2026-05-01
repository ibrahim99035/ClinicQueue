import api from "./client"

export async function getAdminOverview() {
  const response = await api.get("/analytics/admin-overview/");
  return response.data;
}

export async function getAppointmentsByStatus() {
  const response = await api.get("/analytics/appointments-by-status/");
  return response.data;
}

export async function getAppointmentsByMonth() {
  const response = await api.get("/analytics/appointments-by-month/");
  return response.data;
}

export async function getTopSpecializations() {
  const response = await api.get("/analytics/top-specializations/");
  return response.data;
}

export async function getDoctorPerformance() {
  const response = await api.get("/analytics/doctor-performance/");
  return response.data;
}