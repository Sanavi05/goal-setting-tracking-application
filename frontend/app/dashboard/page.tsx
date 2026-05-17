"use client";

import { useEffect, useState } from "react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { AppShell } from "@/components/AppShell";
import { Card } from "@/components/ui/card";
import api, { getStoredUser } from "@/lib/api";

export default function DashboardPage() {
  const [data, setData] = useState<any>(null);
  const [chart, setChart] = useState<any[]>([]);
  const user = getStoredUser();

  useEffect(() => {
    if (!user) return;
    const endpoint = user.role === "ADMIN" ? "/api/admin/dashboard" : user.role === "MANAGER" ? "/api/manager/dashboard" : "/api/employee/dashboard";
    api.get(endpoint).then((res) => setData(res.data));
    api.get("/api/analytics/goal-distribution").then((res) => setChart(res.data.status || []));
  }, []);

  return (
    <AppShell>
      <h1 className="page-title">{user?.role === "ADMIN" ? "Admin Dashboard" : user?.role === "MANAGER" ? "Manager Dashboard" : "Employee Dashboard"}</h1>
      {!data ? <div className="mt-4 text-sm text-slate-500">Loading dashboard...</div> : (
        <div className="mt-4 grid gap-4 md:grid-cols-4">
          {Object.entries(data).map(([key, value]) => (
            <Card key={key}>
              <div className="text-xs uppercase text-slate-500">{key.replaceAll("_", " ")}</div>
              <div className="mt-2 text-2xl font-semibold">{Array.isArray(value) ? value.join(", ") : String(value)}</div>
            </Card>
          ))}
        </div>
      )}
      <Card className="mt-4">
        <h2 className="text-base font-semibold">Goal Status Distribution</h2>
        <div className="mt-4 h-72">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chart}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis allowDecimals={false} />
              <Tooltip />
              <Bar dataKey="value" fill="#2563eb" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </Card>
    </AppShell>
  );
}
