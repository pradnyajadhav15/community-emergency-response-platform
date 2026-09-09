import { createContext, useContext, useEffect, useState } from "react";
import * as SecureStore from "expo-secure-store";

import api from "./api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    restore();
  }, []);

  async function restore() {
    try {
      const token = await SecureStore.getItemAsync("access_token");
      if (token) {
        const { data } = await api.get("/auth/me/");
        setUser(data);
      }
    } catch {
      await SecureStore.deleteItemAsync("access_token");
      await SecureStore.deleteItemAsync("refresh_token");
    } finally {
      setLoading(false);
    }
  }

  async function signIn(username, password) {
    const { data } = await api.post("/auth/login/", { username, password });
    await SecureStore.setItemAsync("access_token", data.access);
    await SecureStore.setItemAsync("refresh_token", data.refresh);
    setUser(data.user);
    return data.user;
  }

  async function signUp(payload) {
    await api.post("/auth/register/", payload);
    return signIn(payload.username, payload.password);
  }

  async function signOut() {
    await SecureStore.deleteItemAsync("access_token");
    await SecureStore.deleteItemAsync("refresh_token");
    setUser(null);
  }

  async function refreshUser() {
    const { data } = await api.get("/auth/me/");
    setUser(data);
    return data;
  }

  return (
    <AuthContext.Provider value={{ user, loading, signIn, signUp, signOut, refreshUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used inside AuthProvider");
  return context;
}
