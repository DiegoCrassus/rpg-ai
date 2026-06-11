type WorkflowLegendPanelProps = {
  gateOpen: boolean;
};

export function WorkflowLegendPanel({ gateOpen }: WorkflowLegendPanelProps) {
  return (
    <aside className="flex w-full max-w-md flex-col rounded-xl border border-slate-800 bg-surface-card p-4 lg:w-80">
      <h2 className="text-sm font-semibold text-white">How to read this diagram</h2>
      <ul className="mt-3 space-y-2 text-xs text-slate-400">
        <li className="flex items-start gap-2">
          <span className="mt-0.5 h-3 w-3 shrink-0 rounded border-2 border-sky-400 bg-sky-950/50" />
          <span>
            <strong className="text-sky-200">Now</strong> — current stage while the gate is open
          </span>
        </li>
        <li className="flex items-start gap-2">
          <span className="mt-0.5 h-3 w-3 shrink-0 rounded border-2 border-emerald-400 bg-emerald-950/40" />
          <span>
            <strong className="text-emerald-200">Done</strong> — stages already passed in this run
          </span>
        </li>
        <li className="flex items-start gap-2">
          <span className="mt-0.5 h-3 w-3 shrink-0 rounded border-2 border-slate-500" />
          <span>Upcoming stages in the lifecycle</span>
        </li>
        <li className="flex items-start gap-2">
          <span className="mt-0.5 h-6 w-0.5 shrink-0 rounded bg-sky-400" />
          <span>
            Highlighted edge — next transition; badge shows the responsible agent
          </span>
        </li>
      </ul>
      <p className="mt-4 text-xs text-slate-500">
        {gateOpen
          ? "Session updates every few seconds from session-gate.json and orchestrator-handoff."
          : "Start a card with workflow start to see live progress on the canvas."}
      </p>
    </aside>
  );
}
