"use client";

import axios from "axios";

export const BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

const api = axios.create({
  baseURL: `${BASE_URL}/api`,
  timeout: 15000,
  headers: { "Content-Type": "application/json" },
});

api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("cerp_access");
    if (token) config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (r) => r,
  async (error) => {
    const original = error.config;
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true;
      const refresh = localStorage.getItem("cerp_refresh");
      if (refresh) {
        try {
          const { data } = await axios.post(`${BASE_URL}/api/auth/refresh/`, { refresh });
          localStorage.setItem("cerp_access", data.access);
          original.headers.Authorization = `Bearer ${data.access}`;
          return api(original);
        } catch {
          localStorage.removeItem("cerp_access");
          localStorage.removeItem("cerp_refresh");
        }
      }
    }
    return Promise.reject(error);
  }
);

export function apiError(error, fallback = "Something went wrong.") {
  if (!error.response) return "Cannot reach the API. Is the Django server running?";
  const data = error.response.data;
  if (typeof data === "string") return data;
  if (data?.detail) return data.detail;
  const first = Object.values(data || {})[0];
  if (Array.isArray(first)) return first[0];
  if (typeof first === "string") return first;
  return fallback;
}

export default api;