"""Generate SDLC Doctor health Canvas (.canvas.tsx) from findings."""

from __future__ import annotations

import json
from datetime import datetime, timezone
try:
    from datetime import UTC
except ImportError:
    UTC = timezone.utc
from pathlib import Path

Finding = tuple[str, str]


def _categorize(message: str) -> str:
    if "YAML" in message:
        return "yaml"
    if "Makefile" in message:
        return "makefile"
    if "Integration" in message:
        return "integrations"
    if message.startswith("Required directory"):
        return "directories"
    if message.startswith("Required file"):
        return "files"
    if message.startswith("Doc file"):
        return "docs"
    if ".cursor/" in message:
        return "ide"
    if ".sdlc/" in message:
        return "sdlc"
    return "other"


def health_score(findings: list[Finding]) -> int:
    pass_n = sum(1 for level, _ in findings if level == "PASS")
    total = len(findings) or 1
    return round(pass_n / total * 100)


def find_canvas_dir(repo_root: Path) -> Path:
    projects = Path.home() / ".cursor" / "projects"
    if projects.is_dir():
        for entry in sorted(projects.iterdir()):
            canvases = entry / "canvases"
            if canvases.is_dir() and repo_root.name in entry.name:
                return canvases
    slug = "home-" + str(repo_root.resolve()).strip("/").replace("/", "-").replace("_", "-")
    out = projects / slug / "canvases"
    out.mkdir(parents=True, exist_ok=True)
    return out


def generate_health_canvas(findings: list[Finding]) -> str:
    ts = datetime.now(UTC).isoformat(timespec="seconds")
    counts = {"PASS": 0, "WARN": 0, "FAIL": 0}
    rows = []
    for level, message in findings:
        counts[level] = counts.get(level, 0) + 1
        rows.append({"level": level, "category": _categorize(message), "message": message})

    score = health_score(findings)
    fails = [r for r in rows if r["level"] == "FAIL"]
    warns = [r for r in rows if r["level"] == "WARN"]
    cats: dict[str, dict[str, int]] = {}
    for r in rows:
        c = cats.setdefault(r["category"], {"PASS": 0, "WARN": 0, "FAIL": 0})
        c[r["level"]] = c.get(r["level"], 0) + 1

    cats_list = [
        {
            "name": k,
            "pass": v.get("PASS", 0),
            "warn": v.get("WARN", 0),
            "fail": v.get("FAIL", 0),
            "total": sum(v.values()),
        }
        for k, v in sorted(cats.items())
    ]

    payload = json.dumps(
        {
            "timestamp": ts,
            "healthScore": score,
            "counts": counts,
            "categories": cats_list,
            "failures": fails[:25],
            "warnings": warns[:25],
            "total": len(rows),
        },
        ensure_ascii=False,
    )

    header = "import React, { useState } from \"react\";\n\nconst D = "
    return (
        header + payload + ";\n\n"
        "const COLORS = {\n"
        "  PASS: { bg: \"#dcfce7\", text: \"#15803d\" },\n"
        "  WARN: { bg: \"#fef3c7\", text: \"#92400e\" },\n"
        "  FAIL: { bg: \"#fee2e2\", text: \"#991b1b\" },\n"
        "};\n\n"
        "function Badge({ status }) {\n"
        "  const c = COLORS[status] || COLORS.WARN;\n"
        "  return (\n"
        "    <span style={{\n"
        "      background: c.bg, color: c.text, padding: \"2px 10px\",\n"
        "      borderRadius: 9999, fontSize: 11, fontWeight: 700,\n"
        "    }}>{status}</span>\n"
        "  );\n"
        "}\n\n"
        "export default function SDLCDoctorHealth() {\n"
        "  const [tab, setTab] = useState(\"overview\");\n"
        "  const ok = D.counts.FAIL === 0;\n"
        "  return (\n"
        "    <div style={{ fontFamily: \"system-ui\", background: \"#f8fafc\", minHeight: \"100vh\", padding: 24 }}>\n"
        "      <div style={{ maxWidth: 960, margin: \"0 auto\" }}>\n"
        "        <div style={{\n"
        "          background: ok ? \"#1e293b\" : \"#7f1d1d\", color: \"#fff\",\n"
        "          borderRadius: 16, padding: 24, marginBottom: 20,\n"
        "        }}>\n"
        "          <div style={{ fontSize: 12, opacity: 0.8 }}>SDLC DOCTOR</div>\n"
        "          <h1 style={{ margin: \"8px 0 4px\", fontSize: 24 }}>\n"
        "            {ok ? \"Estrutura saudavel\" : \"Falhas detectadas\"}\n"
        "          </h1>\n"
        "          <div style={{ fontSize: 13, opacity: 0.9 }}>\n"
        "            {D.timestamp} · {D.total} checks · saude {D.healthScore}%\n"
        "          </div>\n"
        "          <div style={{ marginTop: 16, display: \"flex\", gap: 16 }}>\n"
        "            <Badge status=\"PASS\" /> <span>{D.counts.PASS}</span>\n"
        "            <Badge status=\"WARN\" /> <span>{D.counts.WARN}</span>\n"
        "            <Badge status=\"FAIL\" /> <span>{D.counts.FAIL}</span>\n"
        "          </div>\n"
        "        </div>\n"
        "        <div style={{ display: \"flex\", gap: 8, marginBottom: 16 }}>\n"
        "          {[\"overview\", \"fail\", \"warn\"].map((t) => (\n"
        "            <button key={t} onClick={() => setTab(t)} style={{\n"
        "              padding: \"8px 14px\", borderRadius: 8, border: \"1px solid #cbd5e1\",\n"
        "              background: tab === t ? \"#1e293b\" : \"#fff\",\n"
        "              color: tab === t ? \"#fff\" : \"#334155\", cursor: \"pointer\",\n"
        "            }}>{t}</button>\n"
        "          ))}\n"
        "        </div>\n"
        "        {tab === \"overview\" && D.categories.map((c) => (\n"
        "          <div key={c.name} style={{\n"
        "            background: \"#fff\", padding: 14, marginBottom: 8,\n"
        "            borderRadius: 10, border: \"1px solid #e2e8f0\",\n"
        "            display: \"flex\", justifyContent: \"space-between\",\n"
        "          }}>\n"
        "            <strong>{c.name}</strong>\n"
        "            <span style={{ fontSize: 13 }}>\n"
        "              P{c.pass} W{c.warn} F{c.fail}\n"
        "            </span>\n"
        "          </div>\n"
        "        ))}\n"
        "        {tab === \"fail\" && (\n"
        "          <ul style={{ background: \"#fff\", padding: 16, borderRadius: 10 }}>\n"
        "            {D.failures.length ? D.failures.map((f, i) => (\n"
        "              <li key={i} style={{ marginBottom: 6, fontSize: 13 }}>{f.message}</li>\n"
        "            )) : <li>Sem falhas</li>}\n"
        "          </ul>\n"
        "        )}\n"
        "        {tab === \"warn\" && (\n"
        "          <ul style={{ background: \"#fff\", padding: 16, borderRadius: 10 }}>\n"
        "            {D.warnings.length ? D.warnings.map((w, i) => (\n"
        "              <li key={i} style={{ marginBottom: 6, fontSize: 13 }}>{w.message}</li>\n"
        "            )) : <li>Sem avisos</li>}\n"
        "          </ul>\n"
        "        )}\n"
        "      </div>\n"
        "    </div>\n"
        "  );\n"
        "}\n"
    )


def write_health_canvas(
    findings: list[Finding],
    repo_root: Path,
    *,
    memory_copy: bool = True,
) -> Path:
    canvas_dir = find_canvas_dir(repo_root)
    out = canvas_dir / "sdlc-doctor-health.canvas.tsx"
    out.write_text(generate_health_canvas(findings), encoding="utf-8")

    if memory_copy:
        mem = repo_root / ".sdlc" / "memory"
        mem.mkdir(parents=True, exist_ok=True)
        summary = {
            "timestamp": datetime.now(UTC).isoformat(),
            "health_score": health_score(findings),
            "pass": sum(1 for level, _ in findings if level == "PASS"),
            "warn": sum(1 for level, _ in findings if level == "WARN"),
            "fail": sum(1 for level, _ in findings if level == "FAIL"),
            "canvas_path": str(out),
            "exit_ok": sum(1 for level, _ in findings if level == "FAIL") == 0,
        }
        (mem / "doctor-health.json").write_text(
            json.dumps(summary, indent=2) + "\n", encoding="utf-8"
        )
    return out
