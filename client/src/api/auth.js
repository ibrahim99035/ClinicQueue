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

export function getAccessToken() {
  return localStorage.getItem("access");
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


export function hasAnyRole(allowedRoles = []) {
  const userRoles = getStoredRoleOfUser();

  if (allowedRoles.length === 0) {
    return true;
  }

  const userHasAllowedRole = allowedRoles.some((role) => {
    return userRoles.includes(role);
  });

  return userHasAllowedRole;
}


export function isAdminUser() {
    const roles = getStoredRoleOfUser();
    return roles.includes("Admins");
}


export function getDefaultRouteByRole() {
  const roles = getStoredRoleOfUser();

  if (roles.includes("Admins")) {
    return "/admin";
  }

  if (roles.includes("Doctors")) {
    return "/doctor";
  }

  if (roles.includes("Receptionists")) {
    return "/receptionist";
  }

  if (roles.includes("Patients")) {
    return "/patient";
  }

  return "/login";
}