import type { ReactNode } from "react";
import { Panel, PanelGroup, PanelResizeHandle } from "react-resizable-panels";

type BuilderShellProps = {
  toolbox: ReactNode;
  canvas: ReactNode;
  inspector: ReactNode;
};

/** Three-panel builder layout: toolbox (280–480px), canvas (flex), inspector (~320px). */
export function BuilderShell({ toolbox, canvas, inspector }: BuilderShellProps) {
  return (
    <PanelGroup
      direction="horizontal"
      className="min-h-[calc(100vh-14rem)] rounded-xl border border-slate-800 bg-surface-card/30"
      data-testid="builder-shell"
    >
      <Panel
        id="builder-toolbox-panel"
        defaultSize={22}
        minSize={22}
        maxSize={32}
        className="min-w-[280px] max-w-[480px]"
      >
        <div className="flex h-full flex-col overflow-hidden p-3" data-testid="builder-toolbox">
          {toolbox}
        </div>
      </Panel>

      <PanelResizeHandle className="w-1.5 bg-slate-800 transition-colors hover:bg-studio-accent/40" />

      <Panel id="builder-canvas-panel" minSize={35} className="min-w-0">
        <div className="flex h-full flex-col gap-2 overflow-hidden p-3" data-testid="builder-canvas">
          {canvas}
        </div>
      </Panel>

      <PanelResizeHandle className="w-1.5 bg-slate-800 transition-colors hover:bg-studio-accent/40" />

      <Panel
        id="builder-inspector-panel"
        defaultSize={20}
        minSize={18}
        maxSize={28}
        className="min-w-[280px]"
      >
        <div
          className="flex h-full flex-col gap-4 overflow-y-auto p-3"
          data-testid="builder-inspector-panel"
        >
          {inspector}
        </div>
      </Panel>
    </PanelGroup>
  );
}
