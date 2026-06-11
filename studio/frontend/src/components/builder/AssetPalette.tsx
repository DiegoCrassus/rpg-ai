import { useMemo, useState, type ReactNode } from "react";

import type { PipelineAgentMeta, PipelineGateMeta, PipelineStageMeta } from "../../types/pipeline";

import { stageDisplayId } from "./builderDnD";
import { DraggableAssetChip } from "./DraggableAssetChip";

type AssetPaletteProps = {
  stages: PipelineStageMeta[];
  agents: PipelineAgentMeta[];
  gates: PipelineGateMeta[];
  onFocusStage: (displayNodeId: string) => void;
};

function CollapsibleSection({
  title,
  count,
  defaultOpen = true,
  children,
}: {
  title: string;
  count: number;
  defaultOpen?: boolean;
  children: ReactNode;
}) {
  const [open, setOpen] = useState(defaultOpen);

  return (
    <section className="border-t border-slate-800/80 pt-2 first:border-t-0 first:pt-0">
      <button
        type="button"
        className="flex w-full items-center justify-between rounded px-1 py-1 text-left text-xs font-medium text-slate-400 hover:bg-slate-800/60"
        onClick={() => setOpen((value) => !value)}
        aria-expanded={open}
      >
        <span>
          {title} ({count})
        </span>
        <span className="text-slate-500">{open ? "▾" : "▸"}</span>
      </button>
      {open ? <div className="mt-1">{children}</div> : null}
    </section>
  );
}

export function AssetPalette({ stages, agents, gates, onFocusStage }: AssetPaletteProps) {
  const [search, setSearch] = useState("");

  const query = search.trim().toLowerCase();

  const filteredStages = useMemo(() => {
    if (!query) {
      return stages;
    }
    return stages.filter(
      (stage) =>
        stage.name.toLowerCase().includes(query) || stage.id.toLowerCase().includes(query),
    );
  }, [stages, query]);

  const filteredAgents = useMemo(() => {
    if (!query) {
      return agents;
    }
    return agents.filter(
      (agent) =>
        agent.name.toLowerCase().includes(query) ||
        agent.id.toLowerCase().includes(query) ||
        agent.skill.name.toLowerCase().includes(query),
    );
  }, [agents, query]);

  const filteredGates = useMemo(() => {
    if (!query) {
      return gates;
    }
    return gates.filter(
      (gate) =>
        gate.name.toLowerCase().includes(query) ||
        gate.stage.toLowerCase().includes(query) ||
        gate.id.toLowerCase().includes(query),
    );
  }, [gates, query]);

  return (
    <div className="flex h-full min-h-0 flex-col rounded-xl border border-slate-800 bg-surface-card text-sm">
      <div className="sticky top-0 z-10 shrink-0 border-b border-slate-800 bg-surface-card p-3 pb-2">
        <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">SDLC assets</p>
        <p className="mt-1 text-xs text-slate-400">
          Drag stages onto the canvas or click to focus. Connect bottom→top handles. Agents apply per
          transition in the inspector.
        </p>
        <input
          type="search"
          data-testid="builder-toolbox-search"
          placeholder="Search stages, agents…"
          value={search}
          onChange={(event) => setSearch(event.target.value)}
          className="mt-2 w-full rounded-md border border-slate-700 bg-slate-900 px-2 py-1.5 text-xs text-white placeholder:text-slate-500"
        />
      </div>

      <div className="min-h-0 flex-1 overflow-y-auto p-3 pt-2">
        <CollapsibleSection title="Stages" count={filteredStages.length}>
          <ul className="space-y-1" data-testid="builder-toolbox-stages">
            {filteredStages.map((stage) => (
              <li key={stage.id}>
                <DraggableAssetChip
                  stageId={stage.id}
                  testId={`builder-toolbox-stage-${stage.id}`}
                  className="w-full cursor-grab rounded px-2 py-1 text-left text-slate-200 hover:bg-slate-800 active:cursor-grabbing"
                  onClick={() => onFocusStage(stageDisplayId(stage.id))}
                >
                  <span className="font-medium">{stage.name}</span>
                  <span className="ml-2 font-mono text-[10px] text-slate-500">{stage.id}</span>
                </DraggableAssetChip>
              </li>
            ))}
            {filteredStages.length === 0 ? (
              <li className="px-2 text-xs text-slate-500">No stages match search.</li>
            ) : null}
          </ul>
        </CollapsibleSection>

        <CollapsibleSection title="Subagents" count={filteredAgents.length} defaultOpen={false}>
          <ul className="space-y-1 text-xs text-slate-400" data-testid="builder-toolbox-agents">
            {filteredAgents.map((agent) => (
              <li
                key={agent.id}
                className="rounded px-2 py-1 hover:bg-slate-800/60"
                data-testid={`builder-toolbox-agent-${agent.id}`}
              >
                <span className="text-slate-200">{agent.name}</span>
                <span className="text-slate-500"> · {agent.skill.name}</span>
              </li>
            ))}
            {filteredAgents.length === 0 ? (
              <li className="px-2 text-slate-500">No agents match search.</li>
            ) : null}
          </ul>
        </CollapsibleSection>

        <CollapsibleSection title="Gate paths" count={filteredGates.length} defaultOpen={false}>
          <ul className="space-y-1 text-xs text-slate-400" data-testid="builder-toolbox-gates">
            {filteredGates.map((gate) => (
              <li
                key={gate.id}
                className="rounded px-2 py-1 hover:bg-slate-800/60"
                data-testid={`builder-toolbox-gate-${gate.id}`}
              >
                <span className="text-slate-200">{gate.name}</span>
                <span className="text-slate-500">
                  {" "}
                  · {gate.allowed_prefixes.length} prefix
                  {gate.allowed_prefixes.length === 1 ? "" : "es"}
                </span>
              </li>
            ))}
            {filteredGates.length === 0 ? (
              <li className="px-2 text-slate-500">No gates match search.</li>
            ) : null}
          </ul>
        </CollapsibleSection>

        <p className="mt-3 text-[10px] text-slate-500">
          Agents and gates appear as read-only canvas annotations when enabled. Assign subagents on
          transition edges in the inspector.
        </p>
      </div>
    </div>
  );
}
