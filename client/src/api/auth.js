import api from "./client"

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
