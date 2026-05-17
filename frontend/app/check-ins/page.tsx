"use client";

import { useEffect, useState } from "react";
import { AppShell } from "@/components/AppShell";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input, Textarea } from "@/components/ui/input";
import api, { getStoredUser } from "@/lib/api";

export default function CheckInsPage() {
  const [sheet, setSheet] = useState<any>(null);
  const [managerRows, setManagerRows] = useState<any[]>([]);
  const [adminRows, setAdminRows] = useState<any[]>([]);
  const [values, setValues] = useState<Record<number, any>>({});
  const [message, setMessage] = useState("");
  const user = getStoredUser();
  useEffect(() => {
    if (user?.role === "MANAGER") {
      api.get("/api/manager/check-ins").then((res) => setManagerRows(res.data)).catch(() => setManagerRows([]));
      return;
    }
    if (user?.role === "ADMIN") {
      api.get("/api/admin/completion-dashboard").then((res) => setAdminRows(res.data)).catch(() => setAdminRows([]));
      return;
    }
    api.get("/api/goal-sheets/current").then((res) => setSheet(res.data)).catch(() => setSheet({ goals: [] }));
  }, []);
  async function submit(goalId: number) {
    const payload = values[goalId] || {};
    await api.post("/api/check-ins", { goal_id: goalId, quarter: payload.quarter || "Q1", actual_value: Number(payload.actual_value || 0), status: payload.status || "ON_TRACK", employee_comment: payload.employee_comment || "" });
    setMessage("Check-in saved.");
  }
  async function comment(checkInId: number) {
    const payload = values[checkInId] || {};
    await api.post(`/api/manager/check-ins/${checkInId}/comment`, { manager_comment: payload.manager_comment || "" });
    setMessage("Manager comment saved.");
  }
  return (
    <AppShell>
      <h1 className="page-title">Quarterly Check-ins</h1>
      {message && <div className="mt-3 rounded-md border border-border bg-white px-3 py-2 text-sm">{message}</div>}
      {user?.role === "MANAGER" && (
        <div className="mt-4 space-y-3">
          {managerRows.map((row) => (
            <Card key={`${row.goal_id}-${row.quarter}`}>
              <div className="grid gap-3 md:grid-cols-[1fr_120px_120px_120px_1fr_90px]">
                <div>
                  <div className="font-semibold">{row.employee}</div>
                  <div className="text-sm text-slate-600">{row.goal}</div>
                </div>
                <div className="text-sm">Target: {row.target ?? "-"}</div>
                <div className="text-sm">Actual: {row.actual ?? "-"}</div>
                <div className="text-sm">Score: {row.score ?? 0}</div>
                <Input disabled={!row.check_in_id} placeholder={row.manager_comment || "Manager comment"} onChange={(e) => setValues({ ...values, [row.check_in_id]: { manager_comment: e.target.value } })} />
                <Button disabled={!row.check_in_id} onClick={() => comment(row.check_in_id)}>Save</Button>
              </div>
            </Card>
          ))}
          {!managerRows.length && <Card className="text-sm text-slate-500">No approved team goals or check-ins available.</Card>}
        </div>
      )}
      {user?.role === "ADMIN" && (
        <div className="mt-4 grid gap-3 md:grid-cols-4">
          {adminRows.map((row) => (
            <Card key={row.status}>
              <div className="text-xs uppercase text-slate-500">{row.status}</div>
              <div className="mt-2 text-2xl font-semibold">{row.count}</div>
            </Card>
          ))}
          {!adminRows.length && <Card className="text-sm text-slate-500">No completion data available.</Card>}
        </div>
      )}
      {user?.role === "EMPLOYEE" && (
      <div className="mt-4 space-y-3">
        {(sheet?.goals || []).map((goal: any) => (
          <Card key={goal.id}>
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <div className="font-semibold">{goal.title}</div>
                <div className="text-sm text-slate-600">Target: {goal.target_value} · Weightage: {goal.weightage}%</div>
              </div>
              <div className="grid w-full gap-2 md:w-auto md:grid-cols-4">
                <select className="h-9 rounded-md border border-border px-3 text-sm" onChange={(e) => setValues({ ...values, [goal.id]: { ...values[goal.id], quarter: e.target.value } })}><option>Q1</option><option>Q2</option><option>Q3</option><option>Q4</option></select>
                <Input type="number" placeholder="Actual" onChange={(e) => setValues({ ...values, [goal.id]: { ...values[goal.id], actual_value: e.target.value } })} />
                <select className="h-9 rounded-md border border-border px-3 text-sm" onChange={(e) => setValues({ ...values, [goal.id]: { ...values[goal.id], status: e.target.value } })}><option>ON_TRACK</option><option>NOT_STARTED</option><option>COMPLETED</option><option>AT_RISK</option></select>
                <Button onClick={() => submit(goal.id)}>Save</Button>
                <Textarea className="md:col-span-4" placeholder="Employee comment" onChange={(e) => setValues({ ...values, [goal.id]: { ...values[goal.id], employee_comment: e.target.value } })} />
              </div>
            </div>
          </Card>
        ))}
        {!sheet?.goals?.length && <Card className="text-sm text-slate-500">No approved goals available for check-in.</Card>}
      </div>
      )}
    </AppShell>
  );
}
