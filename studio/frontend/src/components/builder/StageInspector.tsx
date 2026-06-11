import type { CanvasNode } from "../../types/canvas";

type StageInspectorProps = {
  node: CanvasNode | null;
  onClose: () => void;
};

export function StageInspector({ node, onClose }: StageInspectorProps) {
  if (!node) {
    return null;
  }

  return (
    <div
      data-testid="builder-inspector-stage"
      className="flex flex-col gap-3 rounded-xl border border-slate-800 bg-surface-card p-4"
    >
      <div className="flex items-start justify-between gap-2">
        <div>
          <p className="text-xs uppercase tracking-wide text-slate-500">Lifecycle stage</p>
          <p className="mt-1 text-sm font-semibold text-white">{node.label}</p>
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
          <dt className="text-slate-500">Stage id</dt>
          <dd className="font-mono text-xs text-studio-accent">{node.graph_node_id}</dd>
        </div>
        <div>
          <dt className="text-slate-500">Category</dt>
          <dd className="text-slate-200">{node.category}</dd>
        </div>
      </dl>

      <p className="text-xs text-slate-500">
        Connect this stage to another using bottom → top handles. Agent and skill are set on the
        transition edge, not on the stage node.
      </p>
    </div>
  );
}
