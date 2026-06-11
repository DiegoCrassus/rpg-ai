import { useState } from "react";
import { useQuery } from "@tanstack/react-query";

import { studioApi } from "../api/client";
import { DerivedBanner } from "../components/common/DerivedBanner";
import { PageHeader } from "../components/common/PageHeader";

const ASSISTANCE_KINDS = [
  { value: "", label: "All kinds" },
  { value: "validation_gap", label: "Validation gap" },
  { value: "missing_source_ref", label: "Missing source ref" },
  { value: "workflow_handoff", label: "Workflow handoff" },
  { value: "plane_follow_up_draft", label: "Plane follow-up draft" },
  { value: "risk_summary", label: "Risk summary" },
];

export function AssistancePage() {
  const [kind, setKind] = useState("");

  const assistanceQuery = useQuery({
    queryKey: ["studio", "assistance", "workflow", kind],
    queryFn: () => studioApi.workflowAssistance(kind ? { kind } : undefined),
    refetchInterval: 120_000,
  });

  const authority = assistanceQuery.data?.assistance.authority ?? "derived_non_authoritative";
  const suggestions = assistanceQuery.data?.suggestions ?? [];

  if (assistanceQuery.isError) {
    return (
      <div className="mx-auto max-w-3xl space-y-4">
        <DerivedBanner authority={authority} />
        <div className="rounded-lg border border-studio-fail/40 bg-red-950/40 p-4 text-red-200">
          <p className="font-medium">Cannot load workflow assistance</p>
          <p className="mt-2 text-xs text-red-300/80">{assistanceQuery.error.message}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <div
        role="status"
        className="rounded-lg border border-rose-500/50 bg-rose-950/40 px-4 py-3 text-sm text-rose-100"
      >
        <span className="font-semibold uppercase tracking-wide text-xs text-rose-300">
          Advisory only — not agent instructions
        </span>
        <p className="mt-1">
          Suggestions below are derived, non-authoritative hints. They are not Cursor agent
          prompts and must not be auto-applied to the repository.
        </p>
      </div>

      <DerivedBanner authority={authority} />

      <PageHeader
        pageId="assistance"
        subtitle="Advisory workflow hints from POST /studio/assistance/workflow"
        aside={
        <label className="text-sm text-slate-400">
          Kind
          <select
            value={kind}
            onChange={(e) => setKind(e.target.value)}
            className="ml-2 rounded border border-slate-700 bg-slate-900 px-2 py-1 text-sm text-slate-200"
          >
            {ASSISTANCE_KINDS.map((option) => (
              <option key={option.value || "all"} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </label>
        }
      />

      {assistanceQuery.isLoading ? (
        <p className="text-slate-400">Loading suggestions…</p>
      ) : (
        <ul className="space-y-4">
          {suggestions.length === 0 ? (
            <li className="rounded-xl border border-dashed border-slate-700 p-8 text-center text-sm text-slate-500">
              No suggestions for the selected filter.
            </li>
          ) : (
            suggestions.map((suggestion) => (
              <li
                key={suggestion.id}
                className="rounded-xl border border-slate-800 bg-surface-card p-4"
              >
                <div className="flex flex-wrap items-center gap-2">
                  <span className="rounded bg-amber-500/10 px-2 py-0.5 text-xs font-medium uppercase tracking-wide text-amber-200">
                    {suggestion.status}
                  </span>
                  <span className="font-mono text-[10px] text-slate-500">{suggestion.kind}</span>
                </div>
                <p className="mt-2 text-sm font-medium text-white">{suggestion.summary}</p>
                {suggestion.observed ? (
                  <p className="mt-2 text-sm text-slate-400">
                    <span className="text-slate-500">Observed:</span> {suggestion.observed}
                  </p>
                ) : null}
                {suggestion.proposed ? (
                  <p className="mt-1 text-sm text-slate-300">
                    <span className="text-slate-500">Proposed:</span> {suggestion.proposed}
                  </p>
                ) : null}
                {suggestion.source_refs.length > 0 ? (
                  <ul className="mt-3 space-y-1 font-mono text-[11px] text-studio-accent">
                    {suggestion.source_refs.map((ref) => (
                      <li key={`${suggestion.id}-${ref.ref}`}>{ref.ref}</li>
                    ))}
                  </ul>
                ) : null}
              </li>
            ))
          )}
        </ul>
      )}
    </div>
  );
}
