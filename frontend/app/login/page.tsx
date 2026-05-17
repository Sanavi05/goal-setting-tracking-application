"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { zodResolver } from "@hookform/resolvers/zod";
import { LogIn } from "lucide-react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { login } from "@/lib/api";

const demos = [
  ["Employee", "employee@goalgrid.demo"],
  ["Manager", "manager@goalgrid.demo"],
  ["Admin", "admin@goalgrid.demo"]
];

const loginSchema = z.object({
  email: z.string().email("Enter a valid work email"),
  password: z.string().min(8, "Password must be at least 8 characters")
});

type LoginForm = z.infer<typeof loginSchema>;

export default function LoginPage() {
  const router = useRouter();
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { register, handleSubmit, setValue, getValues, formState: { errors } } = useForm<LoginForm>({
    resolver: zodResolver(loginSchema),
    defaultValues: { email: "employee@goalgrid.demo", password: "password123" }
  });

  async function submit(values: LoginForm) {
    setLoading(true);
    setError("");
    try {
      await login(values.email, values.password);
      router.push("/dashboard");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Unable to sign in");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="grid min-h-screen place-items-center p-4">
      <Card className="w-full max-w-md">
        <div className="mb-5">
          <h1 className="page-title">GoalGrid</h1>
          <p className="mt-1 text-sm text-slate-600">In-house goal setting and tracking portal</p>
        </div>
        <div className="grid grid-cols-3 gap-2">
          {demos.map(([label, demoEmail]) => (
            <Button key={demoEmail} variant="secondary" onClick={() => { setValue("email", demoEmail); submit({ ...getValues(), email: demoEmail }); }}>{label}</Button>
          ))}
        </div>
        <form className="mt-5 space-y-3" onSubmit={handleSubmit(submit)}>
          <label className="block text-sm font-medium">Email</label>
          <Input {...register("email")} />
          {errors.email && <div className="text-sm text-red-700">{errors.email.message}</div>}
          <label className="block text-sm font-medium">Password</label>
          <Input type="password" {...register("password")} />
          {errors.password && <div className="text-sm text-red-700">{errors.password.message}</div>}
          {error && <div className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{error}</div>}
          <Button className="w-full" disabled={loading} type="submit"><LogIn size={16} /> {loading ? "Signing in..." : "Sign in"}</Button>
        </form>
      </Card>
    </main>
  );
}
