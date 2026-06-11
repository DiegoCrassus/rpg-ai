import { useCallback, useEffect, useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { useMutation, useQuery } from "@tanstack/react-query";
import type { XYPosition } from "@xyflow/react";

import { studioApi } from "../api/client";
import { PageHeader } from "../components/common/PageHeader";
import { AssetPalette } from "../components/builder/AssetPalette";
import { BuilderInspector, type BuilderSelection } from "../components/builder/BuilderInspector";
import { BuilderShell } from "../components/builder/BuilderShell";
import { BuilderToast } from "../components/builder/BuilderToast";
import { ProposalPanel } from "../components/builder/ProposalPanel";
import { ProposedBanner } from "../components/builder/ProposedBanner";
import {
  WorkflowBuilderCanvas,
  type BuilderCanvasSelection,
} from "../components/builder/WorkflowBuilderCanvas";
import {
  createStageCanvasNode,
  findStageOnCanvas,
  normalizeStageSlug,
} from "../components/builder/builderDnD";
import {
  buildWorkflowProposalRequest,
  createTransitionDraft,
  draftsFromCanvas,
  stageNodesFromCanvas,
} from "../components/builder/workflowDraft";
import type { CanvasNode } from "../types/canvas";
import type { WorkflowTransitionDraft } from "../types/builder";
import type { ProposalResponse } from "../types/proposals";

export function WorkflowBuilderPage() {
  const [searchParams] = useSearchParams();
  const urlNodeId = searchParams.get("node");

  const [drafts, setDrafts] = useState<WorkflowTransitionDraft[]>([]);
  const [selection, setSelection] = useState<BuilderSelection>({ kind: "none" });
  const [showAnnotations, setShowAnnotations] = useState(true);
  const [proposalTitle, setProposalTitle] = useState("Workflow transition update");
  const [simulatedCard, setSimulatedCard] = useState("INVES-N");
  const [proposal, setProposal] = useState<ProposalResponse | null>(null);
  const [initialized, setInitialized] = useState(false);
  const [focusNodeId, setFocusNodeId] = useState<string | null>(urlNodeId);
  const [connectOnClick, setConnectOnClick] = useState(false);
  const [toastMessage, setToastMessage] = useState<string | null>(null);
  const [placedStageNodes, setPlacedStageNodes] = useState<CanvasNode[]>([]);
  const [manualPositions, setManualPositions] = useState<Record<string, XYPosition>>({});

  const selectedEdgeId = selection.kind === "edge" ? selection.edgeId : null;
  const highlightedNodeId = useMemo(() => {
    if (selection.kind === "stage") {
      return selection.nodeId;
    }
    if (selection.kind === "agent") {
      return `display.annotation.agent.${selection.agentId}`;
    }
    if (selection.kind === "gate") {
      return `display.annotation.gate.${selection.gateId}`;
    }
    return focusNodeId;
  }, [selection, focusNodeId]);

  const canvasQuery = useQuery({
    queryKey: ["studio", "canvas", "workflow-builder"],
    queryFn: () => studioApi.canvasWorkflowBuilder(),
    refetchInterval: 60_000,
  });

  const pipelineQuery = useQuery({
    queryKey: ["studio", "metadata", "pipeline"],
    queryFn: () => studioApi.pipelineMetadata(),
  });

  const sessionQuery = useQuery({
    queryKey: ["studio", "session", "gate"],
    queryFn: studioApi.sessionGate,
  });

  useEffect(() => {
    const card = sessionQuery.data?.gate?.card;
    if (card) {
      setSimulatedCard(card);
    }
  }, [sessionQuery.data?.gate?.card]);

  useEffect(() => {
    if (canvasQuery.data && !initialized) {
      setDrafts(draftsFromCanvas(canvasQuery.data.nodes, canvasQuery.data.edges));
      setInitialized(true);
    }
  }, [canvasQuery.data, initialized]);

  useEffect(() => {
    if (!toastMessage) {
      return undefined;
    }
    const timer = window.setTimeout(() => setToastMessage(null), 5000);
    return () => window.clearTimeout(timer);
  }, [toastMessage]);

  const apiNodes = canvasQuery.data?.nodes ?? [];
  const canvasStageNodes = useMemo(() => {
    const fromApi = stageNodesFromCanvas(apiNodes);
    const byId = new Map(fromApi.map((node) => [node.id, node]));
    for (const node of placedStageNodes) {
      if (!byId.has(node.id)) {
        byId.set(node.id, node);
      }
    }
    return [...byId.values()];
  }, [apiNodes, placedStageNodes]);

  const nodesById = useMemo(
    () => new Map(canvasStageNodes.map((node) => [node.id, node])),
    [canvasStageNodes],
  );

  const selectedStage = useMemo(() => {
    if (selection.kind !== "stage") {
      return null;
    }
    return canvasStageNodes.find((node) => node.id === selection.nodeId) ?? null;
  }, [canvasStageNodes, selection]);

  const handleCanvasSelection = useCallback((next: BuilderCanvasSelection) => {
    setSelection(next);
  }, []);

  const clearSelection = useCallback(() => {
    setSelection({ kind: "none" });
  }, []);

  const selectedDraft = useMemo(
    () => drafts.find((draft) => draft.edgeDisplayId === selectedEdgeId) ?? null,
    [drafts, selectedEdgeId],
  );

  const updateDraft = useCallback((updated: WorkflowTransitionDraft) => {
    setDrafts((current) =>
      current.map((draft) => (draft.edgeDisplayId === updated.edgeDisplayId ? updated : draft)),
    );
    setProposal(null);
  }, []);

  const onConnectStages = useCallback(
    (sourceDisplayId: string, targetDisplayId: string) => {
      const existing = drafts.find(
        (draft) =>
          draft.sourceDisplayId === sourceDisplayId && draft.targetDisplayId === targetDisplayId,
      );
      if (existing) {
        setSelection({ kind: "edge", edgeId: existing.edgeDisplayId });
        return;
      }

      const created = createTransitionDraft(sourceDisplayId, targetDisplayId, nodesById);
      if (!created) {
        setToastMessage("Could not create transition between these stages.");
        return;
      }

      setDrafts((current) => [...current, created]);
      setSelection({ kind: "edge", edgeId: created.edgeDisplayId });
      setProposal(null);
    },
    [drafts, nodesById],
  );

  const onRemoveEdge = useCallback((edgeDisplayId: string) => {
    setDrafts((current) => current.filter((draft) => draft.edgeDisplayId !== edgeDisplayId));
    setSelection((current) =>
      current.kind === "edge" && current.edgeId === edgeDisplayId ? { kind: "none" } : current,
    );
    setProposal(null);
  }, []);

  const onConnectionFailed = useCallback((message: string) => {
    setToastMessage(message);
  }, []);

  const onDropStage = useCallback(
    (stageId: string, position: XYPosition) => {
      const existing = findStageOnCanvas(canvasStageNodes, stageId);
      if (existing) {
        setFocusNodeId(existing.id);
        setSelection({ kind: "stage", nodeId: existing.id });
        return;
      }

      const slug = normalizeStageSlug(stageId);
      const meta = pipelineQuery.data?.stages.find(
        (stage) => normalizeStageSlug(stage.id) === slug,
      );
      if (!meta) {
        setToastMessage(`Unknown stage: ${stageId}`);
        return;
      }

      const node = createStageCanvasNode(meta);
      setPlacedStageNodes((current) => [...current, node]);
      setManualPositions((current) => ({ ...current, [node.id]: position }));
      setFocusNodeId(node.id);
      setSelection({ kind: "stage", nodeId: node.id });
    },
    [canvasStageNodes, pipelineQuery.data?.stages],
  );

  const createProposalMutation = useMutation({
    mutationFn: () => {
      const body = buildWorkflowProposalRequest(drafts, proposalTitle.trim(), simulatedCard.trim());
      return studioApi.createProposal(body);
    },
    onSuccess: setProposal,
  });

  if (canvasQuery.isError) {
    return (
      <div className="mx-auto max-w-3xl space-y-4" data-testid="builder-page">
        <ProposedBanner />
        <div className="rounded-lg border border-studio-fail/40 bg-red-950/40 p-4 text-red-200">
          <p className="font-medium">Cannot load workflow builder</p>
          <p className="mt-1 text-sm">
            Start the backend with <code className="text-red-100">make studio-dev</code>, then
            refresh.
          </p>
          <p className="mt-2 text-xs text-red-300/80">{canvasQuery.error.message}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto flex max-w-[1600px] flex-col gap-4" data-testid="builder-page">
      <ProposedBanner />
      <BuilderToast message={toastMessage} onDismiss={() => setToastMessage(null)} />

      <PageHeader
        pageId="builder"
        subtitle="Author SDLC lifecycle transitions (10 stages). Assign a Cursor subagent per edge, then export a propose-only patch — apply via git/Plane; agents run in Cursor, not here."
        aside={
          <Link
            to="/workflows"
            className="rounded-md border border-slate-700 px-4 py-2 text-sm text-slate-300 hover:bg-slate-800"
          >
            Back to canvas
          </Link>
        }
      />

      <BuilderShell
        toolbox={
          pipelineQuery.data ? (
            <AssetPalette
              stages={pipelineQuery.data.stages}
              agents={pipelineQuery.data.agents}
              gates={pipelineQuery.data.gates ?? []}
              onFocusStage={(id) => {
                setFocusNodeId(id);
                setSelection({ kind: "stage", nodeId: id });
              }}
            />
          ) : (
            <p className="text-xs text-slate-500">Loading SDLC assets…</p>
          )
        }
        canvas={
          canvasQuery.isLoading ? (
            <p className="text-slate-400">Loading stages…</p>
          ) : (
            <WorkflowBuilderCanvas
              nodes={canvasStageNodes}
              drafts={drafts}
              agents={pipelineQuery.data?.agents ?? []}
              gates={pipelineQuery.data?.gates ?? []}
              showAnnotations={showAnnotations}
              selectedEdgeId={selectedEdgeId}
              highlightedNodeId={highlightedNodeId}
              manualPositions={manualPositions}
              connectOnClick={connectOnClick}
              onConnectOnClickChange={setConnectOnClick}
              onSelectionChange={handleCanvasSelection}
              onConnectStages={onConnectStages}
              onRemoveEdge={onRemoveEdge}
              onDropStage={onDropStage}
              onConnectionFailed={onConnectionFailed}
              onShowAnnotationsChange={setShowAnnotations}
            />
          )
        }
        inspector={
          <>
            <BuilderInspector
              selection={selection}
              selectedDraft={selectedDraft}
              selectedStage={selectedStage}
              agents={pipelineQuery.data?.agents ?? []}
              gates={pipelineQuery.data?.gates ?? []}
              skills={pipelineQuery.data?.skills ?? []}
              onDraftChange={updateDraft}
              onRemoveEdge={onRemoveEdge}
              onClearSelection={clearSelection}
            />

            <div className="rounded-xl border border-slate-800 bg-surface-card p-4">
              <p className="text-xs uppercase tracking-wide text-slate-500">Export proposal</p>
              <label className="mt-3 block text-sm">
                <span className="text-slate-400">Title</span>
                <input
                  className="mt-1 w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-white"
                  value={proposalTitle}
                  onChange={(event) => setProposalTitle(event.target.value)}
                />
              </label>
              <label className="mt-3 block text-sm">
                <span className="text-slate-400">Simulated gate card</span>
                <input
                  className="mt-1 w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 font-mono text-xs text-white"
                  value={simulatedCard}
                  onChange={(event) => setSimulatedCard(event.target.value)}
                />
              </label>
              <button
                type="button"
                data-testid="builder-create-proposal"
                disabled={createProposalMutation.isPending || drafts.length === 0}
                onClick={() => createProposalMutation.mutate()}
                className="mt-4 w-full rounded-md bg-studio-accent px-4 py-2 text-sm font-medium text-slate-950 hover:bg-sky-300 disabled:opacity-50"
              >
                {createProposalMutation.isPending ? "Creating proposal…" : "Create proposal"}
              </button>
              {createProposalMutation.error ? (
                <p className="mt-2 text-sm text-red-300">
                  {(createProposalMutation.error as Error).message}
                </p>
              ) : null}
            </div>
          </>
        }
      />

      {proposal ? (
        <ProposalPanel
          proposal={proposal}
          onUpdated={setProposal}
          onDiscard={() => setProposal(null)}
        />
      ) : null}
    </div>
  );
}
