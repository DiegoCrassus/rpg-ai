import type { WorkflowStepView, WorkflowTrackDef, WorkflowTrackRuntime } from "./workflowTracks";

type WorkflowStageGuideProps = {
  track: WorkflowTrackDef;
  trackRuntime: WorkflowTrackRuntime;
  step: WorkflowStepView | null;
  relationText: string;
};

function StepBadge({ status }: { status: WorkflowStepView["runtimeStatus"] }) {
  if (status === "current") {
    return (
      <span className="rounded border border-sky-400/50 bg-sky-900/50 px-2 py-0.5 text-[10px] font-bold uppercase text-sky-200">
        Active in session
      </span>
    );
  }
  if (status === "completed") {
    return (
      <span className="rounded border border-emerald-500/40 bg-emerald-950/50 px-2 py-0.5 text-[10px] font-bold uppercase text-emerald-200">
        Completed in this run
      </span>
    );
  }
  return null;
}

export function WorkflowStageGuide({
  track,
  trackRuntime,
  step,
  relationText,
}: WorkflowStageGuideProps) {
  const stepIndex = step ? track.stageSlugs.indexOf(step.slug) : -1;
  const prevSlug = stepIndex > 0 ? track.stageSlugs[stepIndex - 1] : null;
  const nextSlug =
    stepIndex >= 0 && stepIndex < track.stageSlugs.length - 1
      ? track.stageSlugs[stepIndex + 1]
      : null;
  const prevStep = prevSlug ? trackRuntime.steps.find((s) => s.slug === prevSlug) : null;
  const nextStep = nextSlug ? trackRuntime.steps.find((s) => s.slug === nextSlug) : null;

  return (
    <aside
      data-testid="workflow-stage-guide"
      className="flex h-full min-h-[320px] flex-col rounded-xl border border-slate-800 bg-surface-card"
    >
      <div className="border-b border-slate-800 px-4 py-3">
        <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
          {step ? "Stage guide" : "Track overview"}
        </p>
        <h2 className="mt-1 text-base font-semibold text-white">
          {step ? step.name : track.label}
        </h2>
      </div>

      <div className="flex-1 space-y-4 overflow-y-auto p-4 text-sm">
        {step ? (
          <>
            <div className="flex flex-wrap gap-2">
              <StepBadge status={step.runtimeStatus} />
              <span className="rounded border border-slate-700 bg-slate-900/60 px-2 py-0.5 font-mono text-[10px] uppercase text-slate-400">
                {step.slug}
              </span>
            </div>

            <section>
              <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                What happens here
              </h3>
              <p className="mt-2 leading-relaxed text-slate-300">
                {step.description || "No description in lifecycle.yaml for this stage."}
              </p>
            </section>

            {step.agentName ? (
              <section>
                <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                  Who runs this stage
                </h3>
                <p className="mt-2 text-white">
                  <span className="font-semibold text-violet-200">{step.agentName}</span>
                  {step.agentId ? (
                    <span className="ml-2 font-mono text-xs text-slate-500">({step.agentId})</span>
                  ) : null}
                </p>
                <p className="mt-1 text-xs text-slate-400">
                  Subagent invoked by the orchestrator while the gate allows writes for this stage.
                </p>
              </section>
            ) : null}

            {step.runtimeStatus === "current" && trackRuntime.nextAgent ? (
              <section className="rounded-lg border border-sky-500/40 bg-sky-950/30 px-3 py-2 text-xs text-sky-100">
                <p className="font-medium">Live routing</p>
                <p className="mt-1">
                  Next agent from handoff:{" "}
                  <span className="font-mono text-sky-50">{trackRuntime.nextAgent}</span>
                  {trackRuntime.stageComplete ? " · stage marked complete" : ""}
                </p>
              </section>
            ) : null}

            {step.transitionLabel ? (
              <section>
                <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                  Next transition
                </h3>
                <p className="mt-2 font-medium text-slate-200">{step.transitionLabel}</p>
                {step.transitionSummary ? (
                  <p className="mt-1 text-xs leading-relaxed text-slate-400">
                    {step.transitionSummary}
                  </p>
                ) : null}
              </section>
            ) : null}

            <section className="grid gap-3 sm:grid-cols-2">
              {prevStep ? (
                <div className="rounded-lg border border-slate-700 bg-slate-900/50 px-3 py-2">
                  <p className="text-[10px] uppercase tracking-wide text-slate-500">Previous</p>
                  <p className="mt-1 text-xs font-medium text-slate-200">{prevStep.name}</p>
                </div>
              ) : (
                <div className="rounded-lg border border-dashed border-slate-700 px-3 py-2 text-xs text-slate-500">
                  Entry point of this track
                </div>
              )}
              {nextStep ? (
                <div className="rounded-lg border border-slate-700 bg-slate-900/50 px-3 py-2">
                  <p className="text-[10px] uppercase tracking-wide text-slate-500">Next</p>
                  <p className="mt-1 text-xs font-medium text-slate-200">{nextStep.name}</p>
                </div>
              ) : (
                <div className="rounded-lg border border-dashed border-slate-700 px-3 py-2 text-xs text-slate-500">
                  End of this track
                </div>
              )}
            </section>
          </>
        ) : (
          <p className="text-slate-400">
            Select a step on the left to see what it means, which agent owns it, and how it connects
            to the rest of the pipeline.
          </p>
        )}

        <section className="rounded-lg border border-amber-500/30 bg-amber-950/20 px-3 py-3">
          <h3 className="text-xs font-semibold uppercase tracking-wide text-amber-200/90">
            How tracks relate
          </h3>
          <p className="mt-2 text-xs leading-relaxed text-amber-100/80">{relationText}</p>
        </section>
      </div>
    </aside>
  );
}
