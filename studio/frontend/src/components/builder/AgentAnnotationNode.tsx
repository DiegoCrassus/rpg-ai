import type { Node, NodeProps } from "@xyflow/react";

import type { AgentAnnotationNodeData } from "./annotationNodes";

export function AgentAnnotationNode({
  data,
  selected,
}: NodeProps<Node<AgentAnnotationNodeData>>) {
  return (
    <div
      data-testid="agent-annotation-node"
      data-agent-id={data.agentId}
      className={[
        "rounded-md border border-violet-500/50 bg-violet-950/60 px-2 py-1.5 shadow-md",
        selected ? "ring-2 ring-violet-400/70" : "",
      ].join(" ")}
      style={{ minWidth: 140, maxWidth: 180 }}
    >
      <p className="text-[10px] uppercase tracking-wide text-violet-300/80">Subagent</p>
      <p className="truncate text-xs font-semibold text-violet-100">{data.agentName}</p>
      <p className="truncate text-[10px] text-violet-300/70">{data.skillName}</p>
    </div>
  );
}
