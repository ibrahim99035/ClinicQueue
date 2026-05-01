import api from "./http";

function normalizeListResponseFromBackend(response) {
    const data = response.data;
 
    if (Array.isArray(data)) {
        return data;
    }

    if(Array.isArray(data.results)) {
        return data.results;
    }

    return [];
}

export async function getAdminUsers() {
    const response = await api.get("/accounts/users/");
    console.log(response.data);
    return normalizeListResponseFromBackend(response);
}

export async function getPendingDoctors() {
    const response = await api.get("/accounts/admin/pending-doctors/");
    return normalizeListResponseFromBackend(response);
}

export async function approveDoctor(doctorProfileId) {
    const response = await api.post(`/accounts/admin/approve-doctor/${doctorProfileId}/`);
    return response.data;
}

export async function createStaffUser(payload) {
    const response = await api.post("/accounts/admin/create-staff/", payload);
    return response.data;
}

export async function updateUser(userId, payload) {
    const response = await api.put(`/accounts/users/${userId}/`, payload);
    return response.data;
}

export async function deleteUser(userId) {
  const response = await api.delete(`/accounts/users/${userId}/`);
  return response.data;
}