"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { BarChart3, Bell, ClipboardCheck, FileDown, Home, LogOut, Settings, Share2, Target } from "lucide-react";
import { Button } from "@/components/ui/button";
import { getStoredUser, logout } from "@/lib/api";
import { cn } from "@/lib/utils";

const items = [
  { href: "/dashboard", label: "Dashboard", icon: Home },
  { href: "/goals", label: "Goal sheet", icon: Target, roles: ["EMPLOYEE"] },
  { href: "/manager/approvals", label: "Approvals", icon: ClipboardCheck, roles: ["MANAGER"] },
  { href: "/check-ins", label: "Check-ins", icon: ClipboardCheck },
  { href: "/admin/cycles", label: "Cycles", icon: Settings, roles: ["ADMIN"] },
  { href: "/shared-goals", label: "Shared goals", icon: Share2, roles: ["ADMIN", "MANAGER"] },
  { href: "/reports", label: "Reports", icon: FileDown, roles: ["ADMIN"] },
  { href: "/analytics", label: "Analytics", icon: BarChart3 }
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const user = getStoredUser();
  const visible = items.filter((item) => !item.roles || (user && item.roles.includes(user.role)));
  return (
    <div className="min-h-screen lg:grid lg:grid-cols-[240px_1fr]">
      <aside className="border-r border-border bg-white">
        <div className="flex h-14 items-center justify-between border-b border-border px-4">
          <div>
            <div className="text-sm font-bold">GoalGrid</div>
            <div className="text-xs text-slate-500">{user?.role || "Portal"}</div>
          </div>
          <Bell size={18} />
        </div>
        <nav className="flex gap-1 overflow-x-auto p-2 lg:block">
          {visible.map((item) => {
            const Icon = item.icon;
            return (
              <Link key={item.href} href={item.href} className={cn("flex min-w-max items-center gap-2 rounded-md px-3 py-2 text-sm text-slate-700 hover:bg-muted", pathname === item.href && "bg-muted font-semibold text-ink")}>
                <Icon size={17} /> {item.label}
              </Link>
            );
          })}
        </nav>
      </aside>
      <main>
        <header className="flex h-14 items-center justify-between border-b border-border bg-white px-4">
          <div className="text-sm text-slate-600">{user ? `${user.name} · ${user.department}` : "Not signed in"}</div>
          <Button variant="ghost" onClick={() => { logout(); router.push("/login"); }}><LogOut size={16} /> Sign out</Button>
        </header>
        <div className="mx-auto max-w-7xl p-4">{children}</div>
      </main>
    </div>
  );
}
