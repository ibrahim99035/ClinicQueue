// Ensures that list API responses always return an array.
// Some backend endpoints return the list directly as response.data,
// while paginated DRF endpoints return the list inside response.data.results.
// If the response format is unexpected, return an empty array to keep the UI safe.
import api from "./http";

function normalizeListResponseFromBackend(response) {
    const data = response.data;
    //response as array 
    if (Array.isArray(data)) {
        return data;
    }
    //response pagination
    if(Array.isArray(data.results)) {
        return data.results;
    }

    return [];
}
"get all users"
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