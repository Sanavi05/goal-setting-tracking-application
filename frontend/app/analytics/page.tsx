"use client";

import { useEffect, useState } from "react";
import { Bar, BarChart, CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { AppShell } from "@/components/AppShell";
import { Card } from "@/components/ui/card";
import api from "@/lib/api";

export default function AnalyticsPage() {
  const [trends, setTrends] = useState<any[]>([]);
  const [managers, setManagers] = useState<any[]>([]);
  useEffect(() => {
    api.get("/api/analytics/qoq-trends").then((res) => setTrends(res.data));
    api.get("/api/analytics/manager-effectiveness").then((res) => setManagers(res.data));
  }, []);
  return (
    <AppShell>
      <h1 className="page-title">Analytics</h1>
      <div className="mt-4 grid gap-4 lg:grid-cols-2">
        <Card>
          <h2 className="text-base font-semibold">QoQ Achievement Trends</h2>
          <div className="mt-4 h-72">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={trends}><CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="quarter" /><YAxis /><Tooltip /><Line type="monotone" dataKey="score" stroke="#2563eb" strokeWidth={2} /></LineChart>
            </ResponsiveContainer>
          </div>
        </Card>
        <Card>
          <h2 className="text-base font-semibold">Manager Effectiveness</h2>
          <div className="mt-4 h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={managers}><CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="manager" /><YAxis allowDecimals={false} /><Tooltip /><Bar dataKey="approved" fill="#2563eb" /><Bar dataKey="team_size" fill="#64748b" /></BarChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>
    </AppShell>
  );
}
