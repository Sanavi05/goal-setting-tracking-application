"use client";

import { useEffect, useState } from "react";
import { Check, RotateCcw } from "lucide-react";
import { AppShell } from "@/components/AppShell";
import { DataTable } from "@/components/DataTable";
import { ConfirmModal } from "@/components/ui/modal";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import api from "@/lib/api";

export default function ApprovalsPage() {
  const [rows, setRows] = useState<any[]>([]);
  const [confirm, setConfirm] = useState<any>(null);
  const load = () => api.get("/api/manager/approvals").then((res) => setRows(res.data));
  useEffect(() => { load(); }, []);
  async function act(type: "approve" | "return", id: number) {
    if (type === "approve") await api.post(`/api/manager/goal-sheets/${id}/approve`);
    else await api.post(`/api/manager/goal-sheets/${id}/return`, { comment: "Please revise targets and resubmit." });
    setConfirm(null);
    load();
  }
  async function updateGoal(goalId: number, patch: any) {
    await api.patch(`/api/manager/goals/${goalId}`, patch);
    load();
  }
  return (
    <AppShell>
      <h1 className="page-title">Manager Approvals</h1>
      <div className="mt-4">
        <DataTable data={rows} columns={[
          { header: "Employee", cell: ({ row }: any) => row.original.employee?.name || row.original.employee_id },
          { header: "Status", accessorKey: "status" },
          { header: "Submitted", accessorKey: "submitted_at" },
          { header: "Goals", cell: ({ row }: any) => row.original.goals?.length || 0 },
          { header: "Actions", cell: ({ row }: any) => <div className="flex gap-2"><Button variant="secondary" onClick={() => setConfirm({ type: "approve", id: row.original.id })}><Check size={15} /> Approve</Button><Button variant="secondary" onClick={() => setConfirm({ type: "return", id: row.original.id })}><RotateCcw size={15} /> Return</Button></div> }
        ]} />
      </div>
      <div className="mt-4 space-y-3">
        {rows.filter((sheet) => sheet.status === "SUBMITTED" || sheet.status === "RETURNED").map((sheet) => (
          <div key={sheet.id} className="rounded-md border border-border bg-white p-4">
            <div className="mb-3 text-sm font-semibold">Editable goals for sheet #{sheet.id}</div>
            <div className="space-y-2">
              {(sheet.goals || []).map((goal: any) => (
                <div key={goal.id} className="grid gap-2 border-t border-border pt-2 md:grid-cols-[1fr_120px_120px_90px]">
                  <div>
                    <div className="text-sm font-medium">{goal.title}</div>
                    <div className="text-xs text-slate-500">{goal.thrust_area}</div>
                  </div>
                  <Input type="number" defaultValue={goal.target_value || 0} onBlur={(e) => updateGoal(goal.id, { target_value: Number(e.target.value) })} />
                  <Input type="number" defaultValue={goal.weightage} onBlur={(e) => updateGoal(goal.id, { weightage: Number(e.target.value) })} />
                  <div className="text-xs text-slate-500">Blur to save</div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
      <ConfirmModal open={Boolean(confirm)} title="Confirm action" message="This will update the employee goal sheet and write an audit log." onCancel={() => setConfirm(null)} onConfirm={() => act(confirm.type, confirm.id)} />
    </AppShell>
  );
}
