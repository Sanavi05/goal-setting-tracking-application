import { InputHTMLAttributes, TextareaHTMLAttributes } from "react";
import { cn } from "@/lib/utils";

export function Input(props: InputHTMLAttributes<HTMLInputElement>) {
  return <input {...props} className={cn("h-9 w-full rounded-md border border-border bg-white px-3 text-sm outline-none focus:border-accent", props.className)} />;
}

export function Textarea(props: TextareaHTMLAttributes<HTMLTextAreaElement>) {
  return <textarea {...props} className={cn("min-h-20 w-full rounded-md border border-border bg-white px-3 py-2 text-sm outline-none focus:border-accent", props.className)} />;
}
