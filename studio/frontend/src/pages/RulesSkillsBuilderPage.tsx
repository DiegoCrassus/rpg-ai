import { useState } from "react";

import { ConfigBuilderPage } from "./ConfigBuilderPage";
import type { ConfigKind } from "../types/config";

const TABS: { kind: ConfigKind; label: string }[] = [
  { kind: "rule", label: "Rules" },
  { kind: "skill", label: "Skills" },
];

export function RulesSkillsBuilderPage() {
  const [tab, setTab] = useState<ConfigKind>("rule");
  const active = TABS.find((item) => item.kind === tab) ?? TABS[0];

  return (
    <div className="space-y-4">
      <div className="flex gap-2">
        {TABS.map((item) => (
          <button
            key={item.kind}
            type="button"
            onClick={() => setTab(item.kind)}
            className={[
              "rounded-md px-4 py-2 text-sm font-medium",
              tab === item.kind
                ? "bg-studio-accent/15 text-studio-accent ring-1 ring-studio-accent/30"
                : "border border-slate-700 text-slate-300 hover:bg-slate-800",
            ].join(" ")}
          >
            {item.label}
          </button>
        ))}
      </div>
      <ConfigBuilderPage
        key={active.kind}
        kind={active.kind}
        title="Rules & Skills"
        subtitle={`Browse and draft ${active.label.toLowerCase()} under allowlisted .cursor paths, then export a propose-only patch.`}
      />
    </div>
  );
}
