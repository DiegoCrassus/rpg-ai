import type { CanvasEdge, CanvasNode } from "../../types/canvas";
import type { PipelineStageMeta } from "../../types/pipeline";
import type { WorkflowRuntimeState } from "./workflowRuntime";
import { nodeIdToStageSlug } from "./workflowRuntime";

type StageDetailPanelProps = {
  node: CanvasNode | null;
  edges: CanvasEdge[];
  stages: PipelineStageMeta[];
  runtime: WorkflowRuntimeState;
  onClose: () => void;
};

function stageMeta(stages: PipelineStageMeta[], slug: string | null): PipelineStageMeta | null {
  if (!slug) return null;
  return (
    stages.find((item) => item.id === slug || item.id === `stage.${slug}`) ?? null
  );
}

export function StageDetailPanel({
  node,
  edges,
  stages,
  runtime,
  onClose,
}: StageDetailPanelProps) {
  if (!node) {
    return null;
  }

  const slug = nodeIdToStageSlug(node.id);
  const meta = stageMeta(stages, slug);
  const outgoing = edges.filter((edge) => edge.source === node.id);
  const incoming = edges.filter((edge) => edge.target === node.id);
  const isCurrent = runtime.currentNodeId === node.id;

  return (
    <aside
      data-testid="stage-detail-panel"
      className="flex w-full max-w-md flex-col rounded-xl border border-slate-800 bg-surface-card lg:w-96"
    >
      <div className="flex items-center justify-between border-b border-slate-800 px-4 py-3">
        <h2 className="text-sm font-semibold text-white">Stage detail</h2>
        <button
          type="button"
          className="text-xs text-slate-400 hover:text-white"
          onClick={onClose}
        >
          Close
        </button>
      </div>

      <div className="flex-1 space-y-4 overflow-y-auto p-4 text-sm">
        <div>
          <p className="text-xs uppercase tracking-wide text-slate-500">Stage</p>
          <p className="mt-1 text-lg font-semibold text-white">{node.label}</p>
          {meta?.description ? (
            <p className="mt-2 text-xs leading-relaxed text-slate-400">{meta.description}</p>
          ) : null}
        </div>

        {isCurrent ? (
          <div className="rounded-lg border border-sky-500/40 bg-sky-950/40 px-3 py-2 text-xs text-sky-100">
            Active now — gate is open on this stage
            {runtime.nextAgent ? (
              <span>
                {" "}
                · next agent <span className="font-mono text-sky-50">{runtime.nextAgent}</span>
              </span>
            ) : null}
          </div>
        ) : null}

        {incoming.length > 0 ? (
          <div>
            <p className="text-xs uppercase tracking-wide text-slate-500">Arrives from</p>
            <ul className="mt-2 space-y-2">
              {incoming.map((edge) => (
                <li
                  key={edge.id}
                  className="rounded-lg border border-slate-700 bg-slate-900/60 px-3 py-2 text-xs"
                >
                  <p className="font-medium text-slate-200">{edge.label ?? edge.graph_edge_id}</p>
                  {edge.agent ? (
                    <p className="mt-1 text-slate-400">
                      Agent: <span className="font-mono text-violet-300">{edge.agent}</span>
                    </p>
                  ) : null}
                  {edge.summary ? <p className="mt-1 text-slate-500">{edge.summary}</p> : null}
                </li>
              ))}
            </ul>
          </div>
        ) : null}

        {outgoing.length > 0 ? (
          <div>
            <p className="text-xs uppercase tracking-wide text-slate-500">Continues to</p>
            <ul className="mt-2 space-y-2">
              {outgoing.map((edge) => {
                const active = runtime.activeEdgeId === edge.id;
                return (
                  <li
                    key={edge.id}
                    className={[
                      "rounded-lg border px-3 py-2 text-xs",
                      active
                        ? "border-sky-500/50 bg-sky-950/50"
                        : "border-slate-700 bg-slate-900/60",
                    ].join(" ")}
                  >
                    <p className="font-medium text-slate-200">{edge.label ?? edge.graph_edge_id}</p>
                    {edge.agent ? (
                      <p className="mt-1 text-slate-400">
                        Agent: <span className="font-mono text-violet-300">{edge.agent}</span>
                      </p>
                    ) : null}
                    {edge.skill ? (
                      <p className="mt-0.5 text-slate-500">
                        Skill: <span className="font-mono">{edge.skill}</span>
                      </p>
                    ) : null}
                    {active ? (
                      <p className="mt-1 text-sky-300">Next transition in the live pipeline</p>
                    ) : null}
                  </li>
                );
              })}
            </ul>
          </div>
        ) : null}
      </div>
    </aside>
  );
}
