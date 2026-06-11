import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";

import { studioApi } from "../api/client";
import { DerivedBanner } from "../components/common/DerivedBanner";
import { PageHeader } from "../components/common/PageHeader";
import { WorkflowCanvas } from "../components/canvas/WorkflowCanvas";
import {
  DEFAULT_VALIDATION_VISIBILITY,
  toggleValidationVisibility,
} from "../components/canvas/validationVisibility";
import { mapRegistryGraphToCanvas } from "../components/registry/registryViewModel";
import type { ValidationStatus } from "../types/canvas";

export function RegistryPage() {
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [visibleValidationStatuses, setVisibleValidationStatuses] = useState(
    DEFAULT_VALIDATION_VISIBILITY,
  );

  const graphQuery = useQuery({
    queryKey: ["studio", "registry", "graph"],
    queryFn: studioApi.registryGraph,
    refetchInterval: 120_000,
  });

  const mapped = useMemo(() => {
    if (!graphQuery.data) {
      return null;
    }
    return mapRegistryGraphToCanvas(graphQuery.data);
  }, [graphQuery.data]);

  const authority = graphQuery.data?.graph.authority ?? "derived_non_authoritative";
  const brokenCount = graphQuery.data?.summary.broken_ref_count ?? 0;

  const onToggleValidationStatus = (status: ValidationStatus) => {
    setVisibleValidationStatuses((current) => toggleValidationVisibility(current, status));
  };

  if (graphQuery.isError) {
    return (
      <div className="mx-auto max-w-3xl space-y-4">
        <DerivedBanner authority={authority} />
        <div className="rounded-lg border border-studio-fail/40 bg-red-950/40 p-4 text-red-200">
          <p className="font-medium">Cannot load registry graph</p>
          <p className="mt-1 text-sm">
            Start the backend with <code className="text-red-100">make studio-dev</code>, then
            refresh.
          </p>
          <p className="mt-2 text-xs text-red-300/80">{graphQuery.error.message}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto flex max-w-[1600px] flex-col gap-4">
      <DerivedBanner authority={authority} />
      <PageHeader
        pageId="registry"
        title="Registry Explorer"
        subtitle={`Referential graph from GET /studio/registry/graph${
          graphQuery.data?.graph.name ? ` · ${graphQuery.data.graph.name}` : ""
        }`}
      />

      {brokenCount > 0 ? (
        <div className="rounded-lg border border-studio-fail/40 bg-red-950/30 px-4 py-3 text-sm text-red-100">
          <p className="font-medium">
            {brokenCount} broken ref{brokenCount === 1 ? "" : "s"} detected
          </p>
          <ul className="mt-2 space-y-1 font-mono text-xs text-red-200/90">
            {mapped?.broken.panelItems.map((item) => (
              <li key={`${item.kind}-${item.id}`}>
                <span className="text-red-300/70">{item.kind}:</span> {item.id}{" "}
                <span className="text-red-300/60">({item.detail})</span>
              </li>
            ))}
          </ul>
        </div>
      ) : (
        <div className="rounded-lg border border-emerald-500/30 bg-emerald-500/5 px-4 py-2 text-sm text-emerald-200">
          No broken registry references in the current compile report.
        </div>
      )}

      {graphQuery.isLoading ? (
        <p className="text-slate-400">Loading registry graph…</p>
      ) : (
        <div className="grid min-h-[520px] gap-4 lg:grid-cols-[1fr_280px]">
          <div className="h-[calc(100vh-16rem)] min-h-[420px]">
            <WorkflowCanvas
              nodes={mapped?.nodes ?? []}
              edges={mapped?.edges ?? []}
              selectedNodeId={selectedNodeId}
              visibleValidationStatuses={visibleValidationStatuses}
              onSelectNode={setSelectedNodeId}
            />
          </div>
          <aside className="space-y-4 rounded-xl border border-slate-800 bg-surface-card p-4">
            <div>
              <p className="text-xs uppercase tracking-wide text-slate-500">Summary</p>
              <dl className="mt-2 space-y-2 text-sm">
                <div className="flex justify-between gap-2">
                  <dt className="text-slate-400">Nodes</dt>
                  <dd className="font-mono text-slate-200">
                    {graphQuery.data?.nodes.length ?? 0}
                  </dd>
                </div>
                <div className="flex justify-between gap-2">
                  <dt className="text-slate-400">Edges</dt>
                  <dd className="font-mono text-slate-200">
                    {graphQuery.data?.edges.length ?? 0}
                  </dd>
                </div>
                <div className="flex justify-between gap-2">
                  <dt className="text-slate-400">Broken refs</dt>
                  <dd className="font-mono text-slate-200">{brokenCount}</dd>
                </div>
              </dl>
            </div>
            {selectedNodeId ? (
              <div>
                <p className="text-xs uppercase tracking-wide text-slate-500">Selected</p>
                <p className="mt-1 font-mono text-xs text-studio-accent">{selectedNodeId}</p>
                {mapped?.broken.brokenNodeIds.has(selectedNodeId) ? (
                  <p className="mt-2 text-xs text-red-300">Highlighted — broken registry ref</p>
                ) : null}
              </div>
            ) : (
              <p className="text-xs text-slate-500">
                Select a node to inspect. Red borders indicate broken refs from the validator.
              </p>
            )}
            <div>
              <p className="text-xs uppercase tracking-wide text-slate-500">Overlay filter</p>
              <div className="mt-2 flex flex-wrap gap-2">
                {(["pass", "warn", "fail", "not_run"] as ValidationStatus[]).map((status) => (
                  <button
                    key={status}
                    type="button"
                    onClick={() => onToggleValidationStatus(status)}
                    className={[
                      "rounded border px-2 py-0.5 text-xs capitalize",
                      visibleValidationStatuses[status]
                        ? "border-studio-accent/50 text-studio-accent"
                        : "border-slate-700 text-slate-500",
                    ].join(" ")}
                  >
                    {status.replace("_", " ")}
                  </button>
                ))}
              </div>
            </div>
          </aside>
        </div>
      )}
    </div>
  );
}
