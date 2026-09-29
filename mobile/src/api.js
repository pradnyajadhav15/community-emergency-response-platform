import axios from "axios";
import * as SecureStore from "expo-secure-store";

// Your laptop's LAN IP. Update this if your network changes.
export const BASE_URL = "https://community-emergency-response-platform.onrender.com";

const api = axios.create({
  baseURL: `${BASE_URL}/api`,
  timeout: 15000,
  headers: { "Content-Type": "application/json" },
});

api.interceptors.request.use(async (config) => {
  const token = await SecureStore.getItemAsync("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config;
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true;
      const refresh = await SecureStore.getItemAsync("refresh_token");
      if (refresh) {
        try {
          const { data } = await axios.post(`${BASE_URL}/api/auth/refresh/`, { refresh });
          await SecureStore.setItemAsync("access_token", data.access);
          original.headers.Authorization = `Bearer ${data.access}`;
          return api(original);
        } catch {
          await SecureStore.deleteItemAsync("access_token");
          await SecureStore.deleteItemAsync("refresh_token");
        }
      }
    }
    return Promise.reject(error);
  }
);

export function apiError(error, fallback = "Something went wrong.") {
  if (error.code === "ECONNABORTED") return "Request timed out. Is the server running?";
  if (!error.response) return "Cannot reach the server. Check WiFi and the server address.";
  const data = error.response.data;
  if (typeof data === "string") return data;
  if (data?.detail) return data.detail;
  const first = Object.values(data || {})[0];
  if (Array.isArray(first)) return first[0];
  if (typeof first === "string") return first;
  return fallback;
}

export default api;
