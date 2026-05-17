"use client";

import { useEffect, useState } from "react";
import { AppShell } from "@/components/AppShell";
import { DataTable } from "@/components/DataTable";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import api from "@/lib/api";

export default function CyclesPage() {
  const [cycles, setCycles] = useState<any[]>([]);
  const [form, setForm] = useState({ name: "FY27 Performance Cycle", year: 2027, status: "DRAFT", goal_setting_open_date: "2027-05-01", q1_open_date: "2027-07-01", q2_open_date: "2027-10-01", q3_open_date: "2028-01-01", q4_open_date: "2028-03-15" });
  const load = () => api.get("/api/admin/cycles").then((res) => setCycles(res.data));
  useEffect(() => { load(); }, []);
  async function create() {
    await api.post("/api/admin/cycles", form);
    load();
  }
  return (
    <AppShell>
      <h1 className="page-title">Cycle Management</h1>
      <Card className="mt-4">
        <div className="grid gap-3 md:grid-cols-4">
          <Input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
          <Input type="number" value={form.year} onChange={(e) => setForm({ ...form, year: Number(e.target.value) })} />
          <Input type="date" value={form.goal_setting_open_date} onChange={(e) => setForm({ ...form, goal_setting_open_date: e.target.value })} />
          <Button onClick={create}>Create Cycle</Button>
        </div>
        <p className="mt-3 text-sm text-slate-600">Default windows: Goal Setting May 1, Q1 July, Q2 October, Q3 January, Q4 March/April.</p>
      </Card>
      <div className="mt-4"><DataTable data={cycles} columns={[{ header: "Name", accessorKey: "name" }, { header: "Year", accessorKey: "year" }, { header: "Status", accessorKey: "status" }, { header: "Goal Setting Opens", accessorKey: "goal_setting_open_date" }]} /></div>
    </AppShell>
  );
}
