"use client";

import axios from "axios";

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
});

api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("goalgrid_token");
    if (token) config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export type Role = "EMPLOYEE" | "MANAGER" | "ADMIN";

export type User = {
  id: number;
  name: string;
  email: string;
  role: Role;
  department: string;
  manager_id?: number;
};

export type Goal = {
  id?: number;
  goal_sheet_id?: number;
  thrust_area: string;
  title: string;
  description: string;
  uom_type: string;
  target_value?: number | null;
  target_date?: string | null;
  weightage: number;
  status?: string;
  is_shared?: boolean;
  is_readonly_title_target?: boolean;
};

export async function login(email: string, password: string) {
  const { data } = await api.post("/api/auth/login", { email, password });
  localStorage.setItem("goalgrid_token", data.access_token);
  localStorage.setItem("goalgrid_user", JSON.stringify(data.user));
  return data.user as User;
}

export function getStoredUser(): User | null {
  if (typeof window === "undefined") return null;
  const raw = localStorage.getItem("goalgrid_user");
  return raw ? JSON.parse(raw) : null;
}

export function logout() {
  localStorage.removeItem("goalgrid_token");
  localStorage.removeItem("goalgrid_user");
}

export default api;
