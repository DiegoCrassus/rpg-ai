import { BaseEdge, EdgeLabelRenderer, getSmoothStepPath, type EdgeProps } from "@xyflow/react";

type TransitionEdgeData = {
  agent?: string;
  agentName?: string;
  skill?: string;
};

export function TransitionEdge({
  id,
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourcePosition,
  targetPosition,
  style,
  markerEnd,
  selected,
  data,
}: EdgeProps) {
  const edgeData = (data ?? {}) as TransitionEdgeData;
  const agentLabel = edgeData.agentName ?? edgeData.agent ?? "";

  const [edgePath, labelX, labelY] = getSmoothStepPath({
    sourceX,
    sourceY,
    targetX,
    targetY,
    sourcePosition,
    targetPosition,
  });

  return (
    <>
      <g
        data-testid="transition-edge"
        data-edge-id={id}
        className={selected ? "selected" : undefined}
      >
        <BaseEdge path={edgePath} markerEnd={markerEnd} style={style} interactionWidth={20} />
      </g>
      {agentLabel ? (
        <EdgeLabelRenderer>
          <div
            data-testid="agent-badge"
            data-agent={edgeData.agent ?? agentLabel}
            className={[
              "pointer-events-none nodrag nopan absolute rounded-full border px-2 py-0.5 text-[10px] font-medium shadow-sm",
              selected
                ? "border-sky-400/80 bg-sky-950/90 text-sky-100"
                : "border-violet-500/60 bg-violet-950/85 text-violet-100",
            ].join(" ")}
            style={{
              transform: `translate(-50%, -50%) translate(${labelX}px, ${labelY}px)`,
            }}
          >
            {agentLabel}
          </div>
        </EdgeLabelRenderer>
      ) : null}
    </>
  );
}
