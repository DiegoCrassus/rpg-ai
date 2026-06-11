import { formatEventTimestamp, payloadSummary } from "../../api/obsQuery";
import { InfoTip } from "../common/InfoTip";
import type { StudioEvent } from "../../types/observability";
import { describeCategory, describeEventType } from "./obsHelp";

const CATEGORY_STYLES: Record<StudioEvent["category"], string> = {
  gateway: "border-sky-500/40 bg-sky-500/10 text-sky-200",
  obs: "border-emerald-500/40 bg-emerald-500/10 text-emerald-200",
  handoff: "border-violet-500/40 bg-violet-500/10 text-violet-200",
  gate: "border-amber-500/40 bg-amber-500/10 text-amber-200",
};

type TimelineEventRowProps = {
  event: StudioEvent;
  selected: boolean;
  onSelect: () => void;
};

export function TimelineEventRow({ event, selected, onSelect }: TimelineEventRowProps) {
  const categoryClass = CATEGORY_STYLES[event.category];
  const categoryHelp = describeCategory(event.category);

  return (
    <button
      type="button"
      data-testid="obs-timeline-row"
      onClick={onSelect}
      className={[
        "w-full rounded-md border px-3 py-2 text-left transition-colors",
        selected
          ? "border-studio-accent/60 bg-studio-accent/10"
          : "border-slate-800 bg-surface-card/80 hover:border-slate-600",
      ].join(" ")}
    >
      <div className="flex flex-wrap items-center gap-x-2 gap-y-0.5">
        <span className="font-mono text-[11px] text-slate-500">
          {formatEventTimestamp(event.timestamp)}
        </span>
        <span
          className={`inline-flex items-center gap-0.5 rounded px-1 py-0.5 text-[10px] uppercase tracking-wide ${categoryClass}`}
        >
          {event.category}
          <InfoTip
            label={`About ${categoryHelp.title} events`}
            testId={`obs-row-category-info-${event.category}`}
            stopPropagation
            panelClassName="w-60"
          >
            <p className="font-medium text-slate-200">{categoryHelp.title}</p>
            <p className="mt-1">{categoryHelp.description}</p>
          </InfoTip>
        </span>
        <span className="inline-flex items-center gap-0.5 font-mono text-[11px] text-studio-accent">
          {event.event_type}
          <InfoTip
            label={`About ${event.event_type}`}
            testId="obs-row-event-type-info"
            stopPropagation
            panelClassName="w-64"
          >
            <p className="font-mono text-slate-200">{event.event_type}</p>
            <p className="mt-1 text-slate-400">{describeEventType(event.event_type)}</p>
          </InfoTip>
        </span>
      </div>
      <p className="mt-0.5 line-clamp-2 text-xs leading-snug text-slate-300">
        {payloadSummary(event)}
      </p>
      {event.correlation_id ? (
        <p className="mt-0.5 truncate font-mono text-[10px] text-slate-500">
          {event.correlation_id}
        </p>
      ) : null}
    </button>
  );
}
