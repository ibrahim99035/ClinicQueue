import api from "./http";

function normalizeListResponse(response) {
    const data = response.data;

    if( Array.isArray(data)){
        return data;
    }

    if(Array.isArray(data.results)) {
        return data.results;
    }

    return [];
}

export async function getWeeklySchedules() {
    const response = await api.get("/scheduling/weekly-schedule/");
    return normalizeListResponse(response);
}

export async function createWeeklySchedule(payload) {
    const response = await api.post("/scheduling/weekly-schedule/", payload);
    return response.data;
}


export async function deleteWeeklySchedule(scheduleId) {
  const response = await api.delete(`/scheduling/weekly-schedule/${scheduleId}/`);
  return response.data;
}

export async function getScheduleExceptions() {
  const response = await api.get("/scheduling/exceptions/");
  return normalizeListResponse(response);
}

export async function createScheduleException(payload) {
  const response = await api.post("/scheduling/exceptions/", payload);
  return response.data;
}

export async function deleteScheduleException(exceptionId) {
  const response = await api.delete(`/scheduling/exceptions/${exceptionId}/`);
  return response.data;
}

export async function generateSlots(payload) {
    const response = await api.post("/scheduling/generate-slots/",payload);
    return response.data;
}

export async function getAvailableSlots(params) {
  const response = await api.get("/scheduling/slots/", {
    params: params,
  });

  return normalizeListResponse(response);
}