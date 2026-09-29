"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

import { apiError } from "@/lib/api";
import { useAuth } from "@/lib/auth";

export default function Login() {
  const { signIn } = useAuth();
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const u = await signIn(username.trim(), password);
      if (!u.is_staff && u.role !== "ADMIN") {
        setError("This portal is for society administrators only.");
        setLoading(false);
        return;
      }
      router.replace("/dashboard");
    } catch (err) {
      setError(apiError(err, "Login failed."));
      setLoading(false);
    }
  }

  return (
    <div className="login-wrap">
      <div className="login-card">
        <div className="login-brand">
          <h1>CERP</h1>
          <p>Administration Portal</p>
        </div>

        {error && <div className="banner banner-error">{error}</div>}

        <form onSubmit={submit}>
          <div className="field">
            <label>Username</label>
            <input value={username} onChange={(e) => setUsername(e.target.value)} autoFocus />
          </div>
          <div className="field">
            <label>Password</label>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
          </div>
          <button className="btn" style={{ width: "100%" }} disabled={loading}>
            {loading ? "Signing in..." : "Sign In"}
          </button>
        </form>
      </div>
    </div>
  );
}