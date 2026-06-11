import type { CanvasNode } from "../../types/canvas";
import type { PipelineAgentMeta, PipelineGateMeta, PipelineSkillMeta } from "../../types/pipeline";
import type { WorkflowTransitionDraft } from "../../types/builder";

import { AnnotationInspector } from "./AnnotationInspector";
import { StageInspector } from "./StageInspector";
import { TransitionInspector } from "./TransitionInspector";

export type BuilderSelection =
  | { kind: "none" }
  | { kind: "edge"; edgeId: string }
  | { kind: "stage"; nodeId: string }
  | { kind: "agent"; agentId: string }
  | { kind: "gate"; gateId: string };

type BuilderInspectorProps = {
  selection: BuilderSelection;
  selectedDraft: WorkflowTransitionDraft | null;
  selectedStage: CanvasNode | null;
  agents: PipelineAgentMeta[];
  gates: PipelineGateMeta[];
  skills: PipelineSkillMeta[];
  onDraftChange: (draft: WorkflowTransitionDraft) => void;
  onRemoveEdge: (edgeDisplayId: string) => void;
  onClearSelection: () => void;
};

export function BuilderInspector({
  selection,
  selectedDraft,
  selectedStage,
  agents,
  gates,
  skills,
  onDraftChange,
  onRemoveEdge,
  onClearSelection,
}: BuilderInspectorProps) {
  if (selection.kind === "edge" && selectedDraft) {
    return (
      <TransitionInspector
        draft={selectedDraft}
        agents={agents}
        skills={skills}
        onChange={onDraftChange}
        onRemove={onRemoveEdge}
        onClose={onClearSelection}
      />
    );
  }

  if (selection.kind === "stage") {
    return <StageInspector node={selectedStage} onClose={onClearSelection} />;
  }

  if (selection.kind === "agent" || selection.kind === "gate") {
    return (
      <AnnotationInspector
        selection={selection}
        agents={agents}
        gates={gates}
        onClose={onClearSelection}
      />
    );
  }

  return (
    <div
      data-testid="builder-inspector"
      className="rounded-xl border border-dashed border-slate-700 bg-surface-card/40 p-4 text-sm text-slate-500"
    >
      Select a <strong className="text-slate-300">stage</strong>,{" "}
      <strong className="text-slate-300">transition edge</strong>, or optional{" "}
      <strong className="text-slate-300">annotation</strong>. Connect stages with bottom → top
      handles, then set agent and skill on the edge.
    </div>
  );
}
