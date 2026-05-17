"use client";

import { useEffect, useState } from "react";
import { AppShell } from "@/components/AppShell";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input, Textarea } from "@/components/ui/input";
import api, { getStoredUser } from "@/lib/api";

export default function SharedGoalsPage() {
  const [users, setUsers] = useState<any[]>([]);
  const [message, setMessage] = useState("");
  const [form, setForm] = useState({ title: "Department KPI: Improve forecast accuracy", description: "Shared KPI assigned to selected employees", thrust_area: "Department KPI", uom_type: "PERCENT_MIN", target_value: 90, primary_owner_id: 0 });
  useEffect(() => {
    const user = getStoredUser();
    api.get(user?.role === "ADMIN" ? "/api/admin/users" : "/api/manager/team").then((res) => {
      setUsers(res.data);
      const firstEmployee = res.data.find((item: any) => item.role === "EMPLOYEE");
      if (firstEmployee) setForm((current) => ({ ...current, primary_owner_id: firstEmployee.id }));
    });
  }, []);
  async function createAndAssign() {
    setMessage("");
    const employee_ids = users.filter((u) => u.role === "EMPLOYEE").slice(0, 3).map((u) => u.id);
    const primary_owner_id = form.primary_owner_id || employee_ids[0];
    if (!primary_owner_id || !employee_ids.length) {
      setMessage("No employees available to assign this shared goal.");
      return;
    }
    const { data } = await api.post("/api/admin/shared-goals", { ...form, primary_owner_id });
    if (!data?.id) {
      setMessage("Shared goal was created but the response did not include an id.");
      return;
    }
    await api.post(`/api/admin/shared-goals/${data.id}/assign`, { employee_ids, weightage: 10 });
    setMessage("Shared departmental KPI assigned. Recipients can adjust weightage only.");
  }
  return (
    <AppShell>
      <h1 className="page-title">Shared Goals</h1>
      {message && <div className="mt-3 rounded-md border border-border bg-white px-3 py-2 text-sm">{message}</div>}
      <Card className="mt-4">
        <div className="grid gap-3 md:grid-cols-2">
          <Input value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} />
          <Input value={form.thrust_area} onChange={(e) => setForm({ ...form, thrust_area: e.target.value })} />
          <Input type="number" value={form.target_value} onChange={(e) => setForm({ ...form, target_value: Number(e.target.value) })} />
          <select className="h-9 rounded-md border border-border px-3 text-sm" value={form.primary_owner_id} onChange={(e) => setForm({ ...form, primary_owner_id: Number(e.target.value) })}>{users.filter((u) => u.role === "EMPLOYEE").map((user) => <option key={user.id} value={user.id}>{user.name}</option>)}</select>
          <Textarea className="md:col-span-2" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
          <Button onClick={createAndAssign}>Create and Assign to First 3 Employees</Button>
        </div>
      </Card>
    </AppShell>
  );
}
