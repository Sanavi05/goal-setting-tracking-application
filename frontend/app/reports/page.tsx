"use client";

import { Download } from "lucide-react";
import { AppShell } from "@/components/AppShell";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function ReportsPage() {
  async function openExport(path: string, filename: string) {
    const token = localStorage.getItem("goalgrid_token");
    const response = await fetch(`${apiUrl}${path}`, { headers: { Authorization: `Bearer ${token}` } });
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    link.click();
    URL.revokeObjectURL(url);
  }
  return (
    <AppShell>
      <h1 className="page-title">Reports</h1>
      <Card className="mt-4">
        <h2 className="text-base font-semibold">Achievement Report</h2>
        <p className="mt-1 text-sm text-slate-600">Planned target vs actual achievement across employees, goals, quarters, and scores.</p>
        <div className="mt-4 flex gap-2">
          <Button onClick={() => openExport("/api/admin/reports/achievement/export/csv", "achievement-report.csv")}><Download size={16} /> CSV</Button>
          <Button variant="secondary" onClick={() => openExport("/api/admin/reports/achievement/export/xlsx", "achievement-report.xlsx")}><Download size={16} /> Excel</Button>
        </div>
      </Card>
    </AppShell>
  );
}
