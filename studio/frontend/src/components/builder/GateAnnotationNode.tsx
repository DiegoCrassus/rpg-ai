import type { Node, NodeProps } from "@xyflow/react";

import type { GateAnnotationNodeData } from "./annotationNodes";

export function GateAnnotationNode({ data, selected }: NodeProps<Node<GateAnnotationNodeData>>) {
  return (
    <div
      data-testid="gate-annotation-node"
      data-gate-id={data.gateId}
      className={[
        "rounded-md border border-amber-500/50 bg-amber-950/50 px-2 py-1.5 shadow-md",
        selected ? "ring-2 ring-amber-400/70" : "",
      ].join(" ")}
      style={{ minWidth: 140, maxWidth: 180 }}
    >
      <p className="text-[10px] uppercase tracking-wide text-amber-300/80">Gate paths</p>
      <p className="truncate text-xs font-semibold text-amber-100">{data.gateName}</p>
      <p className="truncate font-mono text-[10px] text-amber-300/70">
        {data.allowedPrefixCount} prefix{data.allowedPrefixCount === 1 ? "" : "es"}
      </p>
    </div>
  );
}
