import { useEffect, useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";

import { studioApi } from "../api/client";
import { DerivedBanner } from "../components/common/DerivedBanner";
import { PageHeader } from "../components/common/PageHeader";
import { WorkflowSessionPanel } from "../components/canvas/WorkflowSessionPanel";
import { WorkflowStageGuide } from "../components/workflow/WorkflowStageGuide";
import { WorkflowStepList } from "../components/workflow/WorkflowStepList";
import { WorkflowTrackSelector } from "../components/workflow/WorkflowTrackSelector";
import {
  buildTrackRuntime,
  crossTrackRelation,
  resolveActiveTrackId,
  WORKFLOW_TRACKS,
  type WorkflowTrackId,
} from "../components/workflow/workflowTracks";

const TRACK_LIST = [WORKFLOW_TRACKS.main, WORKFLOW_TRACKS.incident];

export function WorkflowsPage() {
  const [selectedTrackId, setSelectedTrackId] = useState<WorkflowTrackId>("main");
  const [selectedSlug, setSelectedSlug] = useState<string | null>(null);

  const canvasQuery = useQuery({
    queryKey: ["studio", "canvas", "workflow-lifecycle"],
    queryFn: studioApi.canvasWorkflowBuilder,
    staleTime: 120_000,
  });

  const pipelineQuery = useQuery({
    queryKey: ["studio", "metadata", "pipeline"],
    queryFn: studioApi.pipelineMetadata,
    staleTime: 300_000,
  });

  const sessionQuery = useQuery({
    queryKey: ["studio", "dashboard", "summary", "workflow-live"],
    queryFn: studioApi.dashboardSummary,
    refetchInterval: 5_000,
    staleTime: 2_000,
  });

  const authority = canvasQuery.data?.canvas.authority ?? "derived_non_authoritative";
  const session = sessionQuery.data?.session;
  const edges = canvasQuery.data?.edges ?? [];
  const stages = pipelineQuery.data?.stages ?? [];
  const agents = pipelineQuery.data?.agents ?? [];

  const executionActive = Boolean(session?.execution_active ?? session?.gate_open);

  const activeTrackId = useMemo(
    () => (executionActive ? resolveActiveTrackId(session?.stage ?? null) : null),
    [executionActive, session?.stage],
  );

  const selectedTrack = WORKFLOW_TRACKS[selectedTrackId];

  const trackRuntime = useMemo(
    () => buildTrackRuntime(selectedTrack, session, stages, agents, edges),
    [selectedTrack, session, stages, agents, edges],
  );

  const selectedStep = useMemo(
    () => trackRuntime.steps.find((step) => step.slug === selectedSlug) ?? null,
    [trackRuntime.steps, selectedSlug],
  );

  const currentStageName = useMemo(() => {
    const slug = trackRuntime.stageSlug;
    if (!slug) return null;
    return trackRuntime.steps.find((step) => step.slug === slug)?.name ?? slug;
  }, [trackRuntime]);

  const relationText = crossTrackRelation(selectedTrackId, activeTrackId);

  useEffect(() => {
    if (activeTrackId) {
      setSelectedTrackId(activeTrackId);
    }
  }, [activeTrackId]);

  useEffect(() => {
    if (!trackRuntime.executionActive || !trackRuntime.stageSlug) {
      return;
    }
    setSelectedSlug((current) => current ?? trackRuntime.stageSlug);
  }, [trackRuntime.executionActive, trackRuntime.stageSlug, selectedTrackId]);

  if (canvasQuery.isError || pipelineQuery.isError) {
    return (
      <div className="mx-auto max-w-3xl space-y-4">
        <DerivedBanner authority={authority} />
        <div className="rounded-lg border border-studio-fail/40 bg-red-950/40 p-4 text-red-200">
          <p className="font-medium">Cannot load workflow</p>
          <p className="mt-1 text-sm">
            Start the backend with <code className="text-red-100">make studio-dev</code>, then
            refresh.
          </p>
          <p className="mt-2 text-xs text-red-300/80">
            {canvasQuery.error?.message ?? pipelineQuery.error?.message}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto flex max-w-[1400px] flex-col gap-4">
      <DerivedBanner authority={authority} />
      <PageHeader
        pageId="workflows"
        subtitle="Two SDLC tracks — delivery and incident response — with live session highlighting"
      />

      {canvasQuery.isLoading || pipelineQuery.isLoading || sessionQuery.isLoading ? (
        <p className="text-slate-400">Loading workflow…</p>
      ) : (
        <>
          <WorkflowSessionPanel
            session={session}
            stageName={currentStageName}
            activeTrackLabel={
              activeTrackId ? WORKFLOW_TRACKS[activeTrackId].label : undefined
            }
          />

          <WorkflowTrackSelector
            tracks={TRACK_LIST}
            selectedTrackId={selectedTrackId}
            activeTrackId={activeTrackId}
            executionActive={executionActive}
            onSelect={(trackId) => {
              setSelectedTrackId(trackId);
              setSelectedSlug(null);
            }}
          />

          <div className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_22rem] xl:grid-cols-[minmax(0,1fr)_24rem]">
            <WorkflowStepList
              track={selectedTrack}
              steps={trackRuntime.steps}
              selectedSlug={selectedSlug}
              onSelect={setSelectedSlug}
            />
            <WorkflowStageGuide
              track={selectedTrack}
              trackRuntime={trackRuntime}
              step={selectedStep}
              relationText={relationText}
            />
          </div>
        </>
      )}
    </div>
  );
}
