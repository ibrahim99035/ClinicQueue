import axios from "axios";

const api = axios.create({
  baseURL: "/api",
  headers: {
    "Content-Type": "application/json",
  },
});

let isRefreshing = false;
let subscribers = [];

function onRefreshed(token) {
  subscribers.forEach((cb) => cb(token));
  subscribers = [];
}

function subscribeTokenRefresh(cb) {
  subscribers.push(cb);
}

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const { config, response } = error;

    if (!response) {
      return Promise.reject(error);
    }

    const requestUrl = config?.url || "";

    const isAuthRequest =
      requestUrl.includes("/accounts/login/") ||
      requestUrl.includes("/accounts/register/") ||
      requestUrl.includes("/accounts/token/refresh/");

    if (isAuthRequest) {
      return Promise.reject(error);
    }

    if (response.status !== 401) {
      return Promise.reject(error);
    }

    const originalRequest = config;

    if (originalRequest._retry) {
      return Promise.reject(error);
    }

    originalRequest._retry = true;

    const refreshToken = localStorage.getItem("refresh");

    if (!refreshToken) {
      localStorage.removeItem("access");
      localStorage.removeItem("refresh");
      localStorage.removeItem("user");
      localStorage.removeItem("roles");
      window.location = "/login";
      return Promise.reject(error);
    }

    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        subscribeTokenRefresh((token) => {
          originalRequest.headers.Authorization = `Bearer ${token}`;
          resolve(api(originalRequest));
        });
      });
    }

    isRefreshing = true;

    return axios
      .post("/api/accounts/token/refresh/", { refresh: refreshToken })
      .then((res) => {
        const newAccess = res.data.access;
        localStorage.setItem("access", newAccess);
        api.defaults.headers.common["Authorization"] = `Bearer ${newAccess}`;
        onRefreshed(newAccess);
        isRefreshing = false;
        originalRequest.headers.Authorization = `Bearer ${newAccess}`;
        return api(originalRequest);
      })
      .catch((err) => {
        isRefreshing = false;
        localStorage.removeItem("access");
        localStorage.removeItem("refresh");
        localStorage.removeItem("user");
        localStorage.removeItem("roles");
        window.location = "/login";
        return Promise.reject(err);
      });
  }
);
export default api;
