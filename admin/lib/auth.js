"use client";

import { createContext, useContext, useEffect, useState } from "react";

import api from "./api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("cerp_access");
    if (!token) {
      setLoading(false);
      return;
    }
    api
      .get("/auth/me/")
      .then(({ data }) => setUser(data))
      .catch(() => {
        localStorage.removeItem("cerp_access");
        localStorage.removeItem("cerp_refresh");
      })
      .finally(() => setLoading(false));
  }, []);

  async function signIn(username, password) {
    const { data } = await api.post("/auth/login/", { username, password });
    localStorage.setItem("cerp_access", data.access);
    localStorage.setItem("cerp_refresh", data.refresh);
    setUser(data.user);
    return data.user;
  }

  function signOut() {
    localStorage.removeItem("cerp_access");
    localStorage.removeItem("cerp_refresh");
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, loading, signIn, signOut }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside AuthProvider");
  return ctx;
}