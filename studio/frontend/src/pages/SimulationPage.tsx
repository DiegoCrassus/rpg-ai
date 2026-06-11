import { useEffect, useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";

import { studioApi } from "../api/client";
import { DerivedBanner } from "../components/common/DerivedBanner";
import { PageHeader } from "../components/common/PageHeader";
import {
  pathLabelChipClass,
  scenarioSlugFromId,
} from "../components/registry/registryViewModel";

const DEFAULT_SCENARIO = "docs_only";

export function SimulationPage() {
  const [scenario, setScenario] = useState(DEFAULT_SCENARIO);

  const catalogQuery = useQuery({
    queryKey: ["studio", "simulation", "catalog"],
    queryFn: () => studioApi.simulationPreview(),
    staleTime: 300_000,
  });

  const previewQuery = useQuery({
    queryKey: ["studio", "simulation", "preview", scenario],
    queryFn: () => studioApi.simulationPreview({ scenario }),
    refetchInterval: 120_000,
  });

  const scenarioOptions = useMemo(() => {
    return (catalogQuery.data?.scenarios ?? []).map((item) => ({
      slug: scenarioSlugFromId(item.id),
      name: item.name,
    }));
  }, [catalogQuery.data?.scenarios]);

  useEffect(() => {
    if (scenarioOptions.length === 0) {
      return;
    }
    if (!scenarioOptions.some((option) => option.slug === scenario)) {
      setScenario(scenarioOptions[0]?.slug ?? DEFAULT_SCENARIO);
    }
  }, [scenario, scenarioOptions]);

  const authority = previewQuery.data?.simulation.authority ?? "derived_non_authoritative";
  const activeScenario = previewQuery.data?.scenarios[0];
  const steps = activeScenario?.steps ?? [];

  if (previewQuery.isError) {
    return (
      <div className="mx-auto max-w-3xl space-y-4">
        <DerivedBanner authority={authority} />
        <div className="rounded-lg border border-studio-fail/40 bg-red-950/40 p-4 text-red-200">
          <p className="font-medium">Cannot load simulation preview</p>
          <p className="mt-2 text-xs text-red-300/80">{previewQuery.error.message}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <DerivedBanner authority={authority} />
      <PageHeader
        pageId="simulation"
        subtitle={`Non-executing preview from POST /studio/simulation/preview${
          previewQuery.data?.simulation.execution_mode
            ? ` · ${previewQuery.data.simulation.execution_mode}`
            : ""
        }`}
      />

      <div className="flex flex-wrap items-end gap-4">
        <label className="text-sm text-slate-400">
          Scenario
          <select
            value={scenario}
            onChange={(e) => setScenario(e.target.value)}
            disabled={catalogQuery.isLoading}
            className="mt-1 block min-w-[240px] rounded border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-slate-200"
          >
            {scenarioOptions.map((option) => (
              <option key={option.slug} value={option.slug}>
                {option.name}
              </option>
            ))}
          </select>
        </label>
        {previewQuery.data?.summary ? (
          <p className="text-xs text-slate-500">
            {previewQuery.data.summary.step_count} step(s) · path labels:{" "}
            {Object.entries(previewQuery.data.summary.path_labels ?? {})
              .map(([key, count]) => `${key}=${count}`)
              .join(", ")}
          </p>
        ) : null}
      </div>

      {activeScenario ? (
        <div className="rounded-lg border border-slate-800 bg-surface-card px-4 py-3 text-sm text-slate-300">
          <p className="font-medium text-white">{activeScenario.name}</p>
          <p className="mt-1 text-slate-400">{activeScenario.description}</p>
        </div>
      ) : null}

      {previewQuery.isLoading ? (
        <p className="text-slate-400">Loading simulation steps…</p>
      ) : (
        <ol className="space-y-4">
          {steps.map((step) => (
            <li
              key={step.id}
              className="rounded-xl border border-slate-800 bg-surface-card/80 p-4"
            >
              <div className="flex flex-wrap items-center gap-2">
                <span className="font-mono text-xs text-slate-500">#{step.order}</span>
                <span
                  className={[
                    "rounded border px-2 py-0.5 text-xs font-medium uppercase tracking-wide",
                    pathLabelChipClass(step.path_label),
                  ].join(" ")}
                >
                  {step.path_label}
                </span>
                <span className="rounded bg-slate-800 px-2 py-0.5 font-mono text-[10px] text-slate-400">
                  {step.kind}
                </span>
              </div>
              <p className="mt-2 text-sm text-white">{step.summary}</p>
              {step.lifecycle_source ? (
                <p className="mt-2 font-mono text-xs text-studio-accent">
                  lifecycle: {step.lifecycle_source}
                </p>
              ) : null}
              {step.next_agent_recommendation ? (
                <p className="mt-1 text-xs text-slate-500">
                  Next agent:{" "}
                  <span className="font-mono text-slate-300">
                    {step.next_agent_recommendation}
                  </span>
                </p>
              ) : null}
              {step.exit_criteria ? (
                <p className="mt-1 text-xs text-slate-500">Exit: {step.exit_criteria}</p>
              ) : null}
            </li>
          ))}
        </ol>
      )}
    </div>
  );
}
