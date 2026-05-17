"use client";

import { useEffect, useState } from "react";
import { Plus, Save, Send } from "lucide-react";
import { AppShell } from "@/components/AppShell";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input, Textarea } from "@/components/ui/input";
import api, { Goal } from "@/lib/api";

const emptyGoal: Goal = { thrust_area: "", title: "", description: "", uom_type: "NUMERIC_MIN", target_value: 0, weightage: 10 };
const uoms = ["NUMERIC_MIN", "NUMERIC_MAX", "PERCENT_MIN", "PERCENT_MAX", "TIMELINE", "ZERO_BASED"];

export default function GoalsPage() {
  const [sheet, setSheet] = useState<any>(null);
  const [goals, setGoals] = useState<Goal[]>([]);
  const [message, setMessage] = useState("");
  const total = goals.reduce((sum, goal) => sum + Number(goal.weightage || 0), 0);
  const locked = Boolean(sheet?.locked_at || sheet?.status === "APPROVED");

  useEffect(() => {
    api.get("/api/goal-sheets/current").then((res) => { setSheet(res.data); setGoals(res.data.goals.length ? res.data.goals : [{ ...emptyGoal, weightage: 40 }, { ...emptyGoal, weightage: 30 }, { ...emptyGoal, weightage: 30 }]); });
  }, []);

  function update(index: number, patch: Partial<Goal>) {
    setGoals((items) => items.map((item, idx) => idx === index ? { ...item, ...patch } : item));
  }

  async function save() {
    setMessage("");
    try {
      const { data } = await api.post("/api/goal-sheets", { goals });
      setSheet(data);
      setMessage("Draft saved.");
      return data;
    } catch (err: any) {
      setMessage(err.response?.data?.detail || "Unable to save goals");
      return null;
    }
  }

  async function submit() {
    const saved = await save();
    if (!saved) return;
    try {
      await api.post(`/api/goal-sheets/${saved.id}/submit`);
      setMessage("Submitted to manager.");
    } catch (err: any) {
      setMessage(err.response?.data?.detail || "Unable to submit");
    }
  }

  return (
    <AppShell>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="page-title">Goal Sheet</h1>
          <p className="mt-1 text-sm text-slate-600">Status: {sheet?.status || "Loading"} · Total weightage: {total}%</p>
        </div>
        <div className="flex gap-2">
          <Button variant="secondary" disabled={locked || goals.length >= 8} onClick={() => setGoals([...goals, emptyGoal])}><Plus size={16} /> Add</Button>
          <Button variant="secondary" disabled={locked} onClick={save}><Save size={16} /> Save Draft</Button>
          <Button disabled={locked || total !== 100} onClick={submit}><Send size={16} /> Submit</Button>
        </div>
      </div>
      {message && <div className="mt-3 rounded-md border border-border bg-white px-3 py-2 text-sm">{message}</div>}
      {total !== 100 && <div className="mt-3 rounded-md border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-800">Total weightage must be exactly 100% before submission.</div>}
      <div className="mt-4 space-y-3">
        {goals.map((goal, index) => (
          <Card key={index}>
            <div className="grid gap-3 md:grid-cols-4">
              <Input disabled={locked} placeholder="Thrust area" value={goal.thrust_area} onChange={(e) => update(index, { thrust_area: e.target.value })} />
              <Input disabled={locked || goal.is_readonly_title_target} placeholder="Goal title" value={goal.title} onChange={(e) => update(index, { title: e.target.value })} />
              <select disabled={locked} className="h-9 rounded-md border border-border px-3 text-sm" value={goal.uom_type} onChange={(e) => update(index, { uom_type: e.target.value })}>{uoms.map((uom) => <option key={uom}>{uom}</option>)}</select>
              <Input disabled={locked || goal.is_readonly_title_target} type="number" placeholder="Target" value={goal.target_value || 0} onChange={(e) => update(index, { target_value: Number(e.target.value) })} />
              <Input disabled={locked} type="number" min={10} placeholder="Weightage" value={goal.weightage} onChange={(e) => update(index, { weightage: Number(e.target.value) })} />
              <Textarea disabled={locked} className="md:col-span-3" placeholder="Description" value={goal.description} onChange={(e) => update(index, { description: e.target.value })} />
            </div>
          </Card>
        ))}
      </div>
    </AppShell>
  );
}
