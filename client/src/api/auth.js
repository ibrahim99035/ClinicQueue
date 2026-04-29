/*
  Authentication service utilities.

  This file contains the main frontend authentication helpers:
  - Sends login requests to the backend using the configured API instance.
  - Saves authentication data in localStorage after a successful login.
  - Clears authentication data from localStorage during logout.
  - Reads stored user roles safely and returns an empty array if roles are missing or invalid.
  - Provides a helper to check whether the current user has the "Admins" role.

  Notes:
  - access and refresh tokens are stored as plain strings.
  - user and roles are converted to JSON strings before saving because localStorage only stores strings.
  - The role name "Admins" must exactly match the role value returned from the backend.
*/

import api from "./http"

export function loginUser(credentials) {
    return api.post("/accounts/login/", credentials)
}

export function saveAuthData(data) {
    localStorage.setItem("access", data.access);
    localStorage.setItem("refresh", data.refresh);
    localStorage.setItem("user", JSON.stringify(data.user));
    localStorage.setItem("roles", JSON.stringify(data.roles));
}

export function clearAuthData(){
  localStorage.removeItem("access");
  localStorage.removeItem("refresh");
  localStorage.removeItem("user");
  localStorage.removeItem("roles");
}

export function getStoredRoleOfUser() {
    const roles = localStorage.getItem("roles");
    if (!roles) {
        return []
        }
    try {
        return JSON.parse(roles);
    }catch{
        return []
    }
}

export function isAdminUser() {
    const roles = getStoredRoleOfUser();
    return roles.includes("Admins");
}
