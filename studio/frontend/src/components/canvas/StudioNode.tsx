import { Handle, Position, type Node, type NodeProps } from "@xyflow/react";

import { validationStatusColor, type StudioNodeData } from "./mapViewModel";

const NEUTRAL_BORDER = "#475569";

const RUNTIME_RING: Record<NonNullable<StudioNodeData["runtimeStatus"]>, string> = {
  current: "ring-2 ring-sky-400/80 shadow-[0_0_24px_rgba(56,189,248,0.35)] animate-pulse",
  completed: "ring-1 ring-emerald-500/40",
  upcoming: "ring-1 ring-slate-600/40 opacity-80",
  inactive: "",
};

const RUNTIME_BADGE: Record<NonNullable<StudioNodeData["runtimeStatus"]>, string | null> = {
  current: "Now",
  completed: "Done",
  upcoming: null,
  inactive: null,
};

export function StudioNode({ data, selected }: NodeProps<Node<StudioNodeData>>) {
  const runtime = data.runtimeStatus ?? "inactive";
  const showValidationBorder = data.validationBorderVisible !== false && runtime === "inactive";
  const borderColor =
    runtime === "current"
      ? "#38bdf8"
      : runtime === "completed"
        ? "#34d399"
        : showValidationBorder
          ? validationStatusColor(data.validationStatus)
          : NEUTRAL_BORDER;
  const runtimeBadge = RUNTIME_BADGE[runtime];

  return (
    <div
      data-testid="stage-node"
      data-runtime={runtime}
      className={[
        "relative rounded-lg border-2 bg-surface-card px-3 py-2 shadow-lg transition-all",
        selected ? "ring-2 ring-studio-accent/60" : RUNTIME_RING[runtime],
        showValidationBorder ? "" : runtime === "inactive" ? "opacity-60" : "",
      ].join(" ")}
      style={{ borderColor, minWidth: 180, maxWidth: 220 }}
    >
      {runtimeBadge ? (
        <span
          className={[
            "absolute -right-2 -top-2 rounded-full border px-1.5 py-0.5 text-[9px] font-bold uppercase tracking-wide",
            runtime === "current"
              ? "border-sky-300/80 bg-sky-900 text-sky-100"
              : "border-emerald-400/60 bg-emerald-950 text-emerald-200",
          ].join(" ")}
        >
          {runtimeBadge}
        </span>
      ) : null}
      <Handle
        type="target"
        position={Position.Top}
        id="target"
        data-testid="stage-handle-target"
        className="!h-4 !w-4 !min-h-4 !min-w-4 !border-2 !border-slate-950 !bg-studio-accent"
      />
      <p className="truncate text-xs uppercase tracking-wide text-slate-500">{data.category}</p>
      <p className="mt-0.5 truncate text-sm font-semibold text-white">{data.label}</p>
      <p className="mt-1 truncate font-mono text-[10px] text-slate-400">{data.entityType}</p>
      <Handle
        type="source"
        position={Position.Bottom}
        id="source"
        data-testid="stage-handle-source"
        className="!h-4 !w-4 !min-h-4 !min-w-4 !border-2 !border-slate-950 !bg-studio-accent"
      />
    </div>
  );
}
