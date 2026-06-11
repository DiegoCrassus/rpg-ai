import type { PipelineAgentMeta, PipelineGateMeta } from "../../types/pipeline";
import type { BuilderSelection } from "./BuilderInspector";

type AnnotationInspectorProps = {
  selection: Extract<BuilderSelection, { kind: "agent" | "gate" }>;
  agents: PipelineAgentMeta[];
  gates: PipelineGateMeta[];
  onClose: () => void;
};

export function AnnotationInspector({
  selection,
  agents,
  gates,
  onClose,
}: AnnotationInspectorProps) {
  if (selection.kind === "agent") {
    const agent = agents.find((item) => item.id === selection.agentId);
    if (!agent) {
      return null;
    }

    return (
      <div
        data-testid="builder-inspector-agent-annotation"
        className="flex flex-col gap-3 rounded-xl border border-violet-900/60 bg-surface-card p-4"
      >
        <div className="flex items-start justify-between gap-2">
          <div>
            <p className="text-xs uppercase tracking-wide text-violet-400/80">Subagent (read-only)</p>
            <p className="mt-1 text-sm font-semibold text-white">{agent.name}</p>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="rounded px-2 py-1 text-xs text-slate-400 hover:bg-slate-800 hover:text-white"
          >
            Close
          </button>
        </div>

        <dl className="space-y-2 text-sm">
          <div>
            <dt className="text-slate-500">Agent id</dt>
            <dd className="font-mono text-xs text-violet-300">{agent.id}</dd>
          </div>
          <div>
            <dt className="text-slate-500">Default skill</dt>
            <dd className="text-slate-200">
              {agent.skill.name}{" "}
              <span className="font-mono text-xs text-slate-500">({agent.skill.id})</span>
            </dd>
          </div>
          <div>
            <dt className="text-slate-500">Linked stages</dt>
            <dd className="font-mono text-xs text-slate-300">{agent.stages.join(", ") || "—"}</dd>
          </div>
          <div>
            <dt className="text-slate-500">Cursor agent</dt>
            <dd className="font-mono text-xs text-slate-400">{agent.cursor_agent || "—"}</dd>
          </div>
        </dl>

        <p className="text-xs text-slate-500">
          Visual anchor only — not connectable and excluded from export. Assign this subagent on a
          transition edge in the inspector.
        </p>
      </div>
    );
  }

  const gate = gates.find((item) => item.id === selection.gateId);
  if (!gate) {
    return null;
  }

  return (
    <div
      data-testid="builder-inspector-gate-annotation"
      className="flex flex-col gap-3 rounded-xl border border-amber-900/60 bg-surface-card p-4"
    >
      <div className="flex items-start justify-between gap-2">
        <div>
          <p className="text-xs uppercase tracking-wide text-amber-400/80">Gate paths (read-only)</p>
          <p className="mt-1 text-sm font-semibold text-white">{gate.name}</p>
        </div>
        <button
          type="button"
          onClick={onClose}
          className="rounded px-2 py-1 text-xs text-slate-400 hover:bg-slate-800 hover:text-white"
        >
          Close
        </button>
      </div>

      <dl className="space-y-2 text-sm">
        <div>
          <dt className="text-slate-500">Stage</dt>
          <dd className="font-mono text-xs text-amber-300">{gate.stage}</dd>
        </div>
        <div>
          <dt className="text-slate-500">Source</dt>
          <dd className="font-mono text-xs text-slate-400">{gate.source_ref}</dd>
        </div>
        <div>
          <dt className="text-slate-500">Allowed prefixes</dt>
          <dd className="mt-1 space-y-0.5 font-mono text-[11px] text-slate-300">
            {gate.allowed_prefixes.length === 0 ? (
              <span className="text-slate-500">None</span>
            ) : (
              gate.allowed_prefixes.map((prefix) => <div key={prefix}>{prefix}</div>)
            )}
          </dd>
        </div>
      </dl>

      <p className="text-xs text-slate-500">
        Read-only badge from paths.yaml — not exported with workflow proposals.
      </p>
    </div>
  );
}
