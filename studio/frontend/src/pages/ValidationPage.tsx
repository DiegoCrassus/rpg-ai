import { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";

import { studioApi } from "../api/client";
import { DerivedBanner } from "../components/common/DerivedBanner";
import { PageHeader } from "../components/common/PageHeader";
import { doctorChipClass } from "../components/registry/registryViewModel";
import { validationStatusColor } from "../components/canvas/mapViewModel";
import type { ValidationStatus } from "../types/canvas";

function StatusBadge({ status }: { status: ValidationStatus }) {
  return (
    <span
      className="inline-flex rounded border px-2 py-0.5 text-xs font-medium capitalize"
      style={{
        borderColor: validationStatusColor(status),
        color: validationStatusColor(status),
      }}
    >
      {status.replace("_", " ")}
    </span>
  );
}

export function ValidationPage() {
  const [statusFilter, setStatusFilter] = useState<string>("");

  const inspectQuery = useQuery({
    queryKey: ["studio", "validation", "inspect", statusFilter],
    queryFn: () =>
      studioApi.validationInspect(statusFilter ? { status: statusFilter } : undefined),
    refetchInterval: 120_000,
  });

  const doctorMutation = useMutation({
    mutationFn: () => studioApi.doctorRun(),
  });

  const authority = inspectQuery.data?.inspection.authority ?? "derived_non_authoritative";
  const records = inspectQuery.data?.records ?? [];

  if (inspectQuery.isError) {
    return (
      <div className="mx-auto max-w-3xl space-y-4">
        <DerivedBanner authority={authority} />
        <div className="rounded-lg border border-studio-fail/40 bg-red-950/40 p-4 text-red-200">
          <p className="font-medium">Cannot load validation inspection</p>
          <p className="mt-2 text-xs text-red-300/80">{inspectQuery.error.message}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-6xl space-y-6">
      <DerivedBanner authority={authority} />
      <PageHeader
        pageId="validation"
        title="Validation Center"
        subtitle={`Inspection from GET /studio/validation/inspect${
          inspectQuery.data?.summary.visible_records != null
            ? ` · ${inspectQuery.data.summary.visible_records} record(s)`
            : ""
        }`}
        aside={
          <div className="flex flex-wrap items-center gap-3">
          <button
            type="button"
            onClick={() => doctorMutation.mutate()}
            disabled={doctorMutation.isPending}
            className="rounded-md border border-studio-accent/50 bg-studio-accent/10 px-4 py-2 text-sm font-medium text-studio-accent hover:bg-studio-accent/20 disabled:opacity-50"
          >
            {doctorMutation.isPending ? "Running doctor…" : "Run doctor"}
          </button>
          {doctorMutation.data != null ? (
            <span
              className={[
                "rounded border px-3 py-1 text-xs font-semibold uppercase tracking-wide",
                doctorChipClass(doctorMutation.data.exit_code),
              ].join(" ")}
            >
              {doctorMutation.data.exit_code === 0 ? "Pass" : "Fail"} · exit{" "}
              {doctorMutation.data.exit_code}
            </span>
          ) : null}
          </div>
        }
      />

      {doctorMutation.data ? (
        <div className="rounded-lg border border-slate-800 bg-surface-card px-4 py-3 text-sm text-slate-300">
          <p className="font-mono text-xs text-slate-500">POST /studio/doctor/run</p>
          <p className="mt-1">{doctorMutation.data.summary}</p>
        </div>
      ) : null}

      <div className="flex flex-wrap items-center gap-3">
        <label className="text-sm text-slate-400">
          Status filter
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="ml-2 rounded border border-slate-700 bg-slate-900 px-2 py-1 text-sm text-slate-200"
          >
            <option value="">All</option>
            <option value="pass">pass</option>
            <option value="warn">warn</option>
            <option value="fail">fail</option>
            <option value="not_run">not_run</option>
          </select>
        </label>
      </div>

      {inspectQuery.isLoading ? (
        <p className="text-slate-400">Loading validation records…</p>
      ) : (
        <div className="overflow-x-auto rounded-xl border border-slate-800">
          <table className="min-w-full divide-y divide-slate-800 text-sm">
            <thead className="bg-surface-card text-left text-xs uppercase tracking-wide text-slate-500">
              <tr>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Check</th>
                <th className="px-4 py-3">Target</th>
                <th className="px-4 py-3">Summary</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/80 bg-slate-900/40">
              {records.length === 0 ? (
                <tr>
                  <td colSpan={4} className="px-4 py-6 text-center text-slate-500">
                    No validation records for the current filter.
                  </td>
                </tr>
              ) : (
                records.map((record) => (
                  <tr key={record.id} className="hover:bg-slate-800/30">
                    <td className="px-4 py-3">
                      <StatusBadge status={record.status} />
                    </td>
                    <td className="px-4 py-3 font-mono text-xs text-slate-300">
                      {record.check_type}
                    </td>
                    <td className="px-4 py-3 font-mono text-xs text-slate-400">
                      {record.target.ref}
                    </td>
                    <td className="px-4 py-3 text-slate-300">{record.summary}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
