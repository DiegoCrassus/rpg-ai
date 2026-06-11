import { Navigate, Route, Routes } from "react-router-dom";

import { StudioLayout } from "./components/shell/StudioLayout";
import { AssistancePage } from "./pages/AssistancePage";
import { DashboardPage } from "./pages/DashboardPage";
import { ObservabilityPage } from "./pages/ObservabilityPage";
import { ConfigBuilderPage } from "./pages/ConfigBuilderPage";
import { RegistryPage } from "./pages/RegistryPage";
import { RulesSkillsBuilderPage } from "./pages/RulesSkillsBuilderPage";
import { SimulationPage } from "./pages/SimulationPage";
import { EvidencePage } from "./pages/EvidencePage";
import { StubPage } from "./pages/StubPage";
import { ValidationPage } from "./pages/ValidationPage";
import { WorkflowsPage } from "./pages/WorkflowsPage";

const stubs: { path: string; title: string; phase: string }[] = [
  { path: "settings", title: "Settings", phase: "meta" },
];

export default function App() {
  return (
    <Routes>
      <Route element={<StudioLayout />}>
        <Route path="/" element={<DashboardPage />} />
        <Route path="workflows" element={<WorkflowsPage />} />
        <Route path="builder" element={<Navigate to="/workflows" replace />} />
        <Route
          path="agents"
          element={
            <ConfigBuilderPage
              kind="agent"
              title="Agents & Subagents"
              subtitle="Browse .cursor/agents, edit or draft from template, export propose-only patches."
            />
          }
        />
        <Route path="rules" element={<RulesSkillsBuilderPage />} />
        <Route
          path="commands"
          element={
            <ConfigBuilderPage
              kind="command"
              title="Commands"
              subtitle="Browse .cursor/commands, edit or draft slash commands as propose-only patches."
            />
          }
        />
        <Route path="observability" element={<ObservabilityPage />} />
        <Route path="registry" element={<RegistryPage />} />
        <Route path="validation" element={<ValidationPage />} />
        <Route path="simulation" element={<SimulationPage />} />
        <Route path="assistance" element={<AssistancePage />} />
        <Route path="evidence" element={<EvidencePage />} />
        {stubs.map((s) => (
          <Route
            key={s.path}
            path={s.path}
            element={<StubPage title={s.title} phase={s.phase} />}
          />
        ))}
      </Route>
    </Routes>
  );
}
