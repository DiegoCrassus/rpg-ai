import { NavLink } from "react-router-dom";
import type { ComponentType, SVGProps } from "react";

import type { PageHelpId } from "../common/pageHelp";
import {
  IconAgents,
  IconAssistance,
  IconChevronLeft,
  IconChevronRight,
  IconCommands,
  IconDashboard,
  IconEvidence,
  IconObservability,
  IconRegistry,
  IconRules,
  IconSettings,
  IconSimulation,
  IconValidation,
  IconWorkflows,
} from "./navIcons";

export type NavItem = {
  to: string;
  label: string;
  end?: boolean;
  pageId: PageHelpId;
  Icon: ComponentType<SVGProps<SVGSVGElement>>;
};

export const PRIMARY_NAV: NavItem[] = [
  { to: "/", label: "Dashboard", end: true, pageId: "dashboard", Icon: IconDashboard },
  { to: "/workflows", label: "Workflow", pageId: "workflows", Icon: IconWorkflows },
  { to: "/agents", label: "Agents & Subagents", pageId: "agents", Icon: IconAgents },
  { to: "/rules", label: "Rules & Skills", pageId: "rules", Icon: IconRules },
  { to: "/commands", label: "Commands", pageId: "commands", Icon: IconCommands },
  { to: "/registry", label: "Registry", pageId: "registry", Icon: IconRegistry },
  { to: "/validation", label: "Validation", pageId: "validation", Icon: IconValidation },
  { to: "/simulation", label: "Simulation", pageId: "simulation", Icon: IconSimulation },
  { to: "/assistance", label: "Assistance", pageId: "assistance", Icon: IconAssistance },
  { to: "/observability", label: "Observability", pageId: "observability", Icon: IconObservability },
  { to: "/evidence", label: "Evidence & Delivery", pageId: "evidence", Icon: IconEvidence },
  { to: "/settings", label: "Settings", pageId: "settings", Icon: IconSettings },
];

const linkClass = ({ isActive }: { isActive: boolean }, collapsed: boolean) =>
  [
    "flex items-center rounded-lg text-sm font-medium transition-colors",
    collapsed ? "justify-center px-2 py-2.5" : "gap-3 px-3 py-2",
    isActive
      ? "bg-studio-accent/15 text-studio-accent ring-1 ring-studio-accent/30"
      : "text-slate-400 hover:bg-slate-800 hover:text-white",
  ].join(" ");

type SidebarProps = {
  open: boolean;
  collapsed: boolean;
  onClose: () => void;
  onToggleCollapse: () => void;
};

export function Sidebar({ open, collapsed, onClose, onToggleCollapse }: SidebarProps) {
  const showCollapsed = collapsed && !open;

  return (
    <>
      {open ? (
        <button
          type="button"
          className="fixed inset-0 z-40 bg-black/50 lg:hidden"
          aria-label="Close navigation"
          onClick={onClose}
        />
      ) : null}
      <aside
        data-testid="studio-sidebar"
        data-collapsed={showCollapsed ? "true" : "false"}
        className={[
          "fixed inset-y-0 left-0 z-50 flex flex-col border-r border-slate-800 bg-slate-950 transition-all duration-200 lg:static lg:z-0",
          showCollapsed ? "w-[4.5rem]" : "w-64",
          open ? "translate-x-0 top-14" : "-translate-x-full top-14 lg:top-0 lg:translate-x-0",
        ].join(" ")}
      >
        <nav className="flex-1 overflow-y-auto overflow-x-hidden p-2" aria-label="Studio navigation">
          <ul className="space-y-1">
            {PRIMARY_NAV.map((item) => (
              <li key={item.to}>
                <NavLink
                  to={item.to}
                  end={item.end}
                  title={showCollapsed ? item.label : undefined}
                  className={(state) => linkClass(state, showCollapsed)}
                  onClick={onClose}
                >
                  <item.Icon className="h-5 w-5 shrink-0" />
                  {showCollapsed ? (
                    <span className="sr-only">{item.label}</span>
                  ) : (
                    <span className="truncate">{item.label}</span>
                  )}
                </NavLink>
              </li>
            ))}
          </ul>
        </nav>
        <div className="hidden shrink-0 border-t border-slate-800 p-2 lg:block">
          <button
            type="button"
            data-testid="sidebar-collapse-toggle"
            onClick={onToggleCollapse}
            aria-label={showCollapsed ? "Expand sidebar" : "Collapse sidebar"}
            className="flex w-full items-center justify-center gap-2 rounded-lg px-2 py-2 text-slate-400 transition-colors hover:bg-slate-800 hover:text-white"
          >
            {showCollapsed ? (
              <IconChevronRight className="h-5 w-5" />
            ) : (
              <>
                <IconChevronLeft className="h-5 w-5" />
                <span className="text-xs">Collapse</span>
              </>
            )}
          </button>
        </div>
      </aside>
    </>
  );
}
