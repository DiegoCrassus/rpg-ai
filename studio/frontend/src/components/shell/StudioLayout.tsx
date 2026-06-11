import { useCallback, useEffect, useState } from "react";
import { Outlet } from "react-router-dom";

import { Sidebar } from "./Sidebar";
import { TopBar } from "./TopBar";

const STORAGE_KEY = "studio-sidebar-collapsed";

function readCollapsedPreference(): boolean {
  try {
    return localStorage.getItem(STORAGE_KEY) === "true";
  } catch {
    return false;
  }
}

export function StudioLayout() {
  const [navOpen, setNavOpen] = useState(false);
  const [collapsed, setCollapsed] = useState(readCollapsedPreference);

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, collapsed ? "true" : "false");
    } catch {
      /* ignore */
    }
  }, [collapsed]);

  const handleMenuToggle = useCallback(() => {
    const isMobile = window.matchMedia("(max-width: 1023px)").matches;
    if (isMobile) {
      setNavOpen((value) => !value);
      return;
    }
    setCollapsed((value) => !value);
  }, []);

  const handleToggleCollapse = useCallback(() => {
    setCollapsed((value) => !value);
  }, []);

  return (
    <div className="flex min-h-screen flex-col bg-surface">
      <TopBar onMenuToggle={handleMenuToggle} sidebarCollapsed={collapsed} />
      <div className="flex min-h-0 flex-1">
        <Sidebar
          open={navOpen}
          collapsed={collapsed}
          onClose={() => setNavOpen(false)}
          onToggleCollapse={handleToggleCollapse}
        />
        <main className="min-w-0 flex-1 overflow-y-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
