import { InfoTip } from "../common/InfoTip";
import type { StudioEvent } from "../../types/observability";
import {
  CORRELATION_FIELD_HELP,
  describeCategory,
  describeEventType,
} from "./obsHelp";

type CorrelationPanelProps = {
  event: StudioEvent;
};

function fieldHelp(key: string): string | undefined {
  return CORRELATION_FIELD_HELP[key];
}

export function CorrelationPanel({ event }: CorrelationPanelProps) {
  const corr = event.correlation;
  const categoryHelp = describeCategory(event.category);
  const entries: [string, string][] = [
    ["correlation_id", event.correlation_id],
    ["card", corr.card],
    ["run_id", corr.run_id],
    ["branch", corr.branch],
    ["session_id", corr.session_id],
  ].flatMap(([key, value]) => (value ? [[key, String(value)] as [string, string]] : []));

  return (
    <div
      className="grid min-h-0 flex-1 grid-rows-[auto_minmax(12rem,1fr)_auto] gap-3 overflow-hidden rounded-xl border border-slate-800 bg-surface-card p-4"
      data-testid="obs-detail-panel"
    >
      <div className="min-h-0 max-h-[min(38vh,14rem)] space-y-4 overflow-y-auto pr-1">
        <div>
          <p className="flex items-center gap-1 text-xs uppercase tracking-wide text-slate-500">
            Selected event
            <InfoTip label="About selected event panel" testId="obs-detail-event-info" panelClassName="w-72">
              <p className="text-slate-300">
                Shows what happened for the timeline row you selected — event type, correlation
                fields, and full JSON payload.
              </p>
            </InfoTip>
          </p>
          <div className="mt-1 flex flex-wrap items-center gap-2">
            <span className="rounded border border-slate-700 bg-slate-800/80 px-1.5 py-0.5 text-[10px] uppercase text-slate-400">
              {event.category}
            </span>
            <InfoTip
              label={`About ${categoryHelp.title}`}
              testId="obs-detail-category-info"
              panelClassName="w-64"
            >
              <p className="font-medium text-slate-200">{categoryHelp.title}</p>
              <p className="mt-1">{categoryHelp.description}</p>
            </InfoTip>
          </div>
          <p className="mt-2 flex items-start gap-1 font-mono text-sm leading-relaxed text-studio-accent">
            <span className="min-w-0 break-all">{event.event_type}</span>
            <InfoTip
              label={`About ${event.event_type}`}
              testId="obs-detail-event-type-info"
              panelClassName="w-72"
            >
              <p className="font-mono text-slate-200">{event.event_type}</p>
              <p className="mt-1">{describeEventType(event.event_type)}</p>
            </InfoTip>
          </p>
          <p className="mt-1 break-all font-mono text-xs leading-relaxed text-slate-500">
            {event.event_id}
          </p>
        </div>
        {entries.length > 0 ? (
          <dl className="space-y-3 text-sm">
            {entries.map(([key, value]) => (
              <div key={key}>
                <dt className="flex items-center gap-1 text-xs uppercase text-slate-500">
                  {key}
                  {fieldHelp(key) ? (
                    <InfoTip label={`About ${key}`} testId={`obs-detail-field-${key}`}>
                      {fieldHelp(key)}
                    </InfoTip>
                  ) : null}
                </dt>
                <dd className="mt-0.5 break-all font-mono text-sm leading-relaxed text-slate-200">
                  {String(value)}
                </dd>
              </div>
            ))}
          </dl>
        ) : (
          <p className="text-sm leading-relaxed text-slate-500">No correlation fields on this event.</p>
        )}
      </div>

      <div className="flex min-h-0 flex-col overflow-hidden border-t border-slate-800/80 pt-3">
        <p className="shrink-0 text-xs uppercase tracking-wide text-slate-500">Payload</p>
        <pre
          data-testid="obs-payload"
          className="mt-2 min-h-0 flex-1 overflow-auto rounded-md border border-slate-700 bg-slate-900 p-3 font-mono text-sm leading-relaxed text-slate-300"
        >
          {JSON.stringify(event.payload, null, 2)}
        </pre>
      </div>

      <p className="shrink-0 border-t border-slate-800/80 pt-2 text-sm leading-relaxed text-slate-500">
        Continue orchestration in Cursor — Studio does not embed chat. Source:{" "}
        <span className="font-mono text-slate-400">{event.source}</span>
      </p>
    </div>
  );
}
