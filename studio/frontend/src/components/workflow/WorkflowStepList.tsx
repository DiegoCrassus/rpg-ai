import type { WorkflowStepView, WorkflowTrackDef } from "./workflowTracks";

const STATUS_STYLES: Record<WorkflowStepView["runtimeStatus"], string> = {
  current: "border-sky-500/70 bg-sky-950/40 ring-1 ring-sky-400/30",
  completed: "border-emerald-500/40 bg-emerald-950/20",
  upcoming: "border-slate-700 bg-slate-900/40",
  inactive: "border-slate-800 bg-slate-900/20 opacity-90",
};

const DOT_STYLES: Record<WorkflowStepView["runtimeStatus"], string> = {
  current: "border-sky-400 bg-sky-400 shadow-[0_0_12px_rgba(56,189,248,0.6)]",
  completed: "border-emerald-400 bg-emerald-500",
  upcoming: "border-slate-500 bg-slate-700",
  inactive: "border-slate-600 bg-slate-800",
};

type WorkflowStepListProps = {
  track: WorkflowTrackDef;
  steps: WorkflowStepView[];
  selectedSlug: string | null;
  onSelect: (slug: string) => void;
};

export function WorkflowStepList({
  track,
  steps,
  selectedSlug,
  onSelect,
}: WorkflowStepListProps) {
  return (
    <div data-testid="workflow-step-list" className="rounded-xl border border-slate-800 bg-surface-card p-4">
      <div className="mb-4">
        <h2 className="text-base font-semibold text-white">{track.label}</h2>
        <p className="mt-1 text-sm text-slate-400">{track.summary}</p>
      </div>

      <ol className="space-y-0">
        {steps.map((step, index) => {
          const isSelected = selectedSlug === step.slug;
          const isLast = index === steps.length - 1;
          return (
            <li key={step.slug} className="relative flex gap-3">
              <div className="flex flex-col items-center">
                <span
                  className={[
                    "mt-4 h-3 w-3 shrink-0 rounded-full border-2",
                    DOT_STYLES[step.runtimeStatus],
                    step.runtimeStatus === "current" ? "animate-pulse" : "",
                  ].join(" ")}
                />
                {!isLast ? (
                  <span className="my-1 w-px flex-1 min-h-[2rem] bg-slate-700" />
                ) : null}
              </div>

              <button
                type="button"
                data-testid={`workflow-step-${step.slug}`}
                data-runtime={step.runtimeStatus}
                onClick={() => onSelect(step.slug)}
                className={[
                  "mb-3 flex-1 rounded-lg border px-4 py-3 text-left transition-colors",
                  STATUS_STYLES[step.runtimeStatus],
                  isSelected ? "ring-2 ring-studio-accent/50" : "hover:border-slate-600",
                ].join(" ")}
              >
                <div className="flex flex-wrap items-center gap-2">
                  <span className="font-mono text-[10px] uppercase tracking-wide text-slate-500">
                    Step {step.order}
                  </span>
                  {step.runtimeStatus === "current" ? (
                    <span className="rounded border border-sky-400/50 bg-sky-900/60 px-1.5 py-0.5 text-[10px] font-bold uppercase text-sky-200">
                      Now
                    </span>
                  ) : null}
                  {step.runtimeStatus === "completed" ? (
                    <span className="rounded border border-emerald-500/40 bg-emerald-950/50 px-1.5 py-0.5 text-[10px] font-bold uppercase text-emerald-200">
                      Done
                    </span>
                  ) : null}
                </div>
                <p className="mt-1 text-sm font-semibold text-white">{step.name}</p>
                <p className="mt-0.5 line-clamp-2 text-xs text-slate-400">{step.description}</p>
                {step.agentName ? (
                  <p className="mt-2 text-xs text-violet-300">
                    Agent: <span className="font-mono">{step.agentName}</span>
                  </p>
                ) : null}
              </button>
            </li>
          );
        })}
      </ol>
    </div>
  );
}
