import type { EventCategory } from "../../types/observability";
import { InfoTip } from "../common/InfoTip";
import { describeCategory } from "./obsHelp";

const CATEGORY_STYLES: Record<EventCategory, string> = {
  gateway: "border-sky-500/40 bg-sky-500/10 text-sky-200",
  obs: "border-emerald-500/40 bg-emerald-500/10 text-emerald-200",
  handoff: "border-violet-500/40 bg-violet-500/10 text-violet-200",
  gate: "border-amber-500/40 bg-amber-500/10 text-amber-200",
};

type CategoryContextBannerProps = {
  category: EventCategory;
};

export function CategoryContextBanner({ category }: CategoryContextBannerProps) {
  const help = describeCategory(category);

  return (
    <div
      className="flex shrink-0 items-start gap-2 rounded-lg border border-slate-800 bg-surface-card/60 px-3 py-2"
      data-testid="obs-category-banner"
    >
      <span
        className={`mt-0.5 shrink-0 rounded px-1.5 py-0.5 text-[10px] uppercase tracking-wide ${CATEGORY_STYLES[category]}`}
      >
        {category}
      </span>
      <div className="min-w-0 flex-1 text-xs leading-relaxed text-slate-400">
        <span className="font-medium text-slate-300">{help.title}</span>
        {" — "}
        {help.description}
        <span className="mt-0.5 block font-mono text-[10px] text-slate-500">
          Examples: {help.examples}
        </span>
      </div>
      <InfoTip label={`More about ${help.title}`} testId="obs-category-banner-info" panelClassName="w-72">
        <p className="font-medium text-slate-200">{help.title}</p>
        <p className="mt-1">{help.description}</p>
        <p className="mt-2 font-mono text-[10px] text-slate-500">Examples: {help.examples}</p>
      </InfoTip>
    </div>
  );
}
