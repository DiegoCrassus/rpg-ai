#!/usr/bin/env node
/**
 * Optional smoke check when Studio API is running (make studio-dev or uvicorn).
 * Exits 0 on success, 1 on failure.
 */
const base = (process.env.VITE_STUDIO_API_URL ?? "http://127.0.0.1:8100").replace(
  /\/$/,
  "",
);

const token = process.env.STUDIO_AUTH_TOKEN?.trim();
const headers = token ? { Authorization: `Bearer ${token}` } : undefined;

const paths = [
  "/studio/health",
  "/studio/readiness",
  "/studio/dashboard/summary",
  "/studio/canvas/full",
];

let failed = false;
for (const path of paths) {
  const url = `${base}${path}`;
  try {
    const res = await fetch(url, headers ? { headers } : undefined);
    if (!res.ok) {
      console.error(`FAIL ${path}: HTTP ${res.status}`);
      failed = true;
      continue;
    }
    const body = await res.json();
    console.log(`OK ${path}`, Object.keys(body).join(", "));
  } catch (err) {
    console.error(`FAIL ${path}:`, err instanceof Error ? err.message : err);
    failed = true;
  }
}

process.exit(failed ? 1 : 0);
