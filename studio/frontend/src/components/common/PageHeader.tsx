import type { ReactNode } from "react";

import { InfoTip } from "./InfoTip";
import { pageHelpFor, type PageHelpId } from "./pageHelp";

type PageHeaderProps = {
  pageId: PageHelpId;
  title?: string;
  subtitle?: string;
  /** Extra controls aligned to the right (badges, buttons) */
  aside?: ReactNode;
  testId?: string;
};

export function PageHeader({ pageId, title, subtitle, aside, testId }: PageHeaderProps) {
  const help = pageHelpFor(pageId);
  const heading = title ?? help.title;
  const desc = subtitle ?? help.subtitle;

  return (
    <div
      className="flex flex-wrap items-start justify-between gap-4"
      data-testid={testId ?? `page-header-${pageId}`}
    >
      <div className="min-w-0">
        <h1 className="flex items-center gap-2 text-2xl font-bold text-white">
          <span>{heading}</span>
          <InfoTip
            label={`About ${heading}`}
            testId={`page-info-${pageId}`}
            panelClassName="w-80"
          >
            <p className="font-medium text-slate-200">{help.title}</p>
            <p className="mt-2 text-slate-300">{help.summary}</p>
            {help.bullets && help.bullets.length > 0 ? (
              <ul className="mt-2 list-disc space-y-1 pl-4 text-slate-400">
                {help.bullets.map((bullet) => (
                  <li key={bullet}>{bullet}</li>
                ))}
              </ul>
            ) : null}
          </InfoTip>
        </h1>
        {desc ? <p className="mt-1 text-sm text-slate-400">{desc}</p> : null}
      </div>
      {aside ? <div className="shrink-0">{aside}</div> : null}
    </div>
  );
}
