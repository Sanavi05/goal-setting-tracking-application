"use client";

import { flexRender, getCoreRowModel, useReactTable } from "@tanstack/react-table";

export function DataTable<T>({ data, columns }: { data: T[]; columns: any[] }) {
  const table = useReactTable({ data, columns, getCoreRowModel: getCoreRowModel() });
  if (!data.length) return <div className="rounded-md border border-border bg-white p-6 text-sm text-slate-500">No records found.</div>;
  return (
    <div className="overflow-x-auto rounded-md border border-border bg-white">
      <table className="w-full border-collapse text-left text-sm">
        <thead className="bg-muted text-xs uppercase text-slate-500">
          {table.getHeaderGroups().map((group) => (
            <tr key={group.id}>{group.headers.map((header) => <th key={header.id} className="border-b border-border px-3 py-2">{flexRender(header.column.columnDef.header, header.getContext())}</th>)}</tr>
          ))}
        </thead>
        <tbody>
          {table.getRowModel().rows.map((row) => (
            <tr key={row.id} className="border-b border-border last:border-b-0">
              {row.getVisibleCells().map((cell) => <td key={cell.id} className="px-3 py-2 align-top">{flexRender(cell.column.columnDef.cell, cell.getContext())}</td>)}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
