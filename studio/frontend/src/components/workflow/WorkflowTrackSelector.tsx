import type { WorkflowTrackDef, WorkflowTrackId } from "./workflowTracks";

type WorkflowTrackSelectorProps = {
  tracks: WorkflowTrackDef[];
  selectedTrackId: WorkflowTrackId;
  activeTrackId: WorkflowTrackId | null;
  executionActive: boolean;
  onSelect: (trackId: WorkflowTrackId) => void;
};

export function WorkflowTrackSelector({
  tracks,
  selectedTrackId,
  activeTrackId,
  executionActive,
  onSelect,
}: WorkflowTrackSelectorProps) {
  return (
    <div
      data-testid="workflow-track-selector"
      className="flex flex-col gap-3 rounded-xl border border-slate-800 bg-surface-card p-4 sm:flex-row sm:items-center sm:justify-between"
    >
      <div>
        <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
          Workflow tracks
        </p>
        <p className="mt-1 text-sm text-slate-400">
          Two related paths — select one to explore; the live session highlights which is operating.
        </p>
      </div>
      <div className="inline-flex rounded-lg border border-slate-700 p-1">
        {tracks.map((track) => {
          const isSelected = selectedTrackId === track.id;
          const isLive = executionActive && activeTrackId === track.id;
          return (
            <button
              key={track.id}
              type="button"
              data-testid={`workflow-track-${track.id}`}
              onClick={() => onSelect(track.id)}
              className={[
                "relative rounded-md px-4 py-2 text-left text-sm transition-colors",
                isSelected
                  ? "bg-studio-accent/20 text-studio-accent"
                  : "text-slate-400 hover:bg-slate-800 hover:text-white",
              ].join(" ")}
            >
              <span className="font-medium">{track.shortLabel}</span>
              {isLive ? (
                <span className="ml-2 inline-flex items-center gap-1 rounded-full border border-emerald-500/40 bg-emerald-500/10 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-emerald-300">
                  <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-emerald-400" />
                  Active
                </span>
              ) : null}
            </button>
          );
        })}
      </div>
    </div>
  );
}
