import { BaseEdge, EdgeLabelRenderer, getSmoothStepPath, type EdgeProps } from "@xyflow/react";

type WorkflowTransitionEdgeData = {
  agent?: string;
  skill?: string;
  label?: string;
  runtimeActive?: boolean;
};

export function WorkflowTransitionEdge({
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
  const edgeData = (data ?? {}) as WorkflowTransitionEdgeData;
  const agentLabel = edgeData.agent ?? "";
  const isActive = edgeData.runtimeActive === true;

  const [edgePath, labelX, labelY] = getSmoothStepPath({
    sourceX,
    sourceY,
    targetX,
    targetY,
    sourcePosition,
    targetPosition,
  });

  const mergedStyle = {
    ...style,
    stroke: isActive ? "#38bdf8" : (style?.stroke as string | undefined) ?? "#64748b",
    strokeWidth: isActive ? 3 : (style?.strokeWidth as number | undefined) ?? 2,
    opacity: isActive ? 1 : 0.65,
  };

  return (
    <>
      <g data-testid="workflow-transition-edge" data-edge-id={id} className={selected ? "selected" : undefined}>
        <BaseEdge path={edgePath} markerEnd={markerEnd} style={mergedStyle} interactionWidth={24} />
        {isActive ? (
          <BaseEdge
            path={edgePath}
            style={{
              stroke: "#38bdf8",
              strokeWidth: 8,
              opacity: 0.2,
              pointerEvents: "none",
            }}
            interactionWidth={0}
          />
        ) : null}
      </g>
      {agentLabel ? (
        <EdgeLabelRenderer>
          <div
            data-testid="workflow-agent-badge"
            data-agent={agentLabel}
            className={[
              "pointer-events-none nodrag nopan absolute rounded-full border px-2 py-0.5 text-[10px] font-medium shadow-sm",
              isActive
                ? "border-sky-300/90 bg-sky-900/95 text-sky-50 ring-2 ring-sky-400/40"
                : selected
                  ? "border-violet-400/80 bg-violet-950/90 text-violet-100"
                  : "border-slate-600/80 bg-slate-900/90 text-slate-300",
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
