import { useCallback, useEffect, useMemo } from "react";
import {
  Background,
  Controls,
  MiniMap,
  ReactFlow,
  useReactFlow,
  type Node,
  type OnSelectionChangeParams,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";

import type { CanvasEdge, CanvasNode } from "../../types/canvas";
import { mapCanvasToFlow, type StudioNodeData } from "./mapViewModel";
import { StudioNode } from "./StudioNode";
import {
  isValidationBorderVisible,
  type ValidationVisibility,
} from "./validationVisibility";
import { WorkflowTransitionEdge } from "./WorkflowTransitionEdge";
import type { WorkflowRuntimeState } from "./workflowRuntime";

const nodeTypes = { studioNode: StudioNode };
const edgeTypes = { workflowTransition: WorkflowTransitionEdge };

type WorkflowCanvasProps = {
  nodes: CanvasNode[];
  edges: CanvasEdge[];
  selectedNodeId: string | null;
  visibleValidationStatuses: ValidationVisibility;
  onSelectNode: (nodeId: string | null) => void;
  workflowMode?: boolean;
  runtime?: WorkflowRuntimeState;
};

function FocusCurrentNode({ nodeId }: { nodeId: string | null }) {
  const { fitView } = useReactFlow();

  useEffect(() => {
    if (!nodeId) {
      return;
    }
    const timer = window.setTimeout(() => {
      fitView({ nodes: [{ id: nodeId }], padding: 0.35, duration: 450, maxZoom: 1.1 });
    }, 120);
    return () => window.clearTimeout(timer);
  }, [fitView, nodeId]);

  return null;
}

export function WorkflowCanvas({
  nodes,
  edges,
  selectedNodeId,
  visibleValidationStatuses,
  onSelectNode,
  workflowMode = false,
  runtime,
}: WorkflowCanvasProps) {
  const { nodes: flowNodes, edges: flowEdges } = useMemo(
    () => mapCanvasToFlow(nodes, edges, { useWorkflowEdge: workflowMode }),
    [nodes, edges, workflowMode],
  );

  const styledNodes = useMemo(
    () =>
      flowNodes.map((node) => ({
        ...node,
        selected: node.id === selectedNodeId,
        data: {
          ...node.data,
          runtimeStatus: workflowMode
            ? (runtime?.nodeStatusById[node.id] ?? "inactive")
            : undefined,
          validationBorderVisible: workflowMode
            ? false
            : isValidationBorderVisible(
                node.data.validationStatus,
                visibleValidationStatuses,
              ),
        },
      })),
    [flowNodes, selectedNodeId, visibleValidationStatuses, workflowMode, runtime],
  );

  const styledEdges = useMemo(
    () =>
      flowEdges.map((edge) => ({
        ...edge,
        animated: workflowMode
          ? runtime?.activeEdgeId === edge.id
          : edge.animated,
        data: {
          ...edge.data,
          runtimeActive: workflowMode && runtime?.activeEdgeId === edge.id,
        },
      })),
    [flowEdges, workflowMode, runtime],
  );

  const onSelectionChange = useCallback(
    ({ nodes: selected }: OnSelectionChangeParams<Node<StudioNodeData>>) => {
      onSelectNode(selected[0]?.id ?? null);
    },
    [onSelectNode],
  );

  const onPaneClick = useCallback(() => {
    onSelectNode(null);
  }, [onSelectNode]);

  if (nodes.length === 0) {
    return (
      <div className="flex h-full min-h-[420px] items-center justify-center rounded-xl border border-dashed border-slate-700 bg-surface-card/40 text-sm text-slate-500">
        No stages in the lifecycle workflow.
      </div>
    );
  }

  return (
    <div
      data-testid="workflow-canvas"
      className="h-full min-h-[420px] overflow-hidden rounded-xl border border-slate-800 bg-slate-950"
    >
      <ReactFlow
        nodes={styledNodes}
        edges={styledEdges}
        nodeTypes={nodeTypes}
        edgeTypes={workflowMode ? edgeTypes : undefined}
        fitView
        fitViewOptions={{ padding: 0.2 }}
        minZoom={0.15}
        maxZoom={1.5}
        onSelectionChange={onSelectionChange}
        onPaneClick={onPaneClick}
        proOptions={{ hideAttribution: true }}
      >
        {workflowMode && runtime?.gateOpen ? (
          <FocusCurrentNode nodeId={runtime.currentNodeId} />
        ) : null}
        <Background gap={16} color="#334155" />
        <Controls className="!border-slate-700 !bg-surface-card !shadow-lg [&>button]:!border-slate-600 [&>button]:!bg-slate-800 [&>button]:!text-slate-200" />
        <MiniMap
          className="!border-slate-700 !bg-surface-card"
          nodeColor={(node) => {
            const data = node.data as StudioNodeData | undefined;
            if (workflowMode && data?.runtimeStatus) {
              if (data.runtimeStatus === "current") return "#38bdf8";
              if (data.runtimeStatus === "completed") return "#34d399";
              if (data.runtimeStatus === "upcoming") return "#94a3b8";
            }
            if (!data || data.validationBorderVisible === false) {
              return "#64748b";
            }
            const status = data.validationStatus;
            if (status === "pass") return "#34d399";
            if (status === "warn") return "#fbbf24";
            if (status === "fail") return "#f87171";
            return "#64748b";
          }}
          maskColor="rgb(15 23 42 / 0.75)"
        />
      </ReactFlow>
    </div>
  );
}
