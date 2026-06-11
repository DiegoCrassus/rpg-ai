/** Get/set nested values using dot paths for groups; repeaters use array indices. */

export function getNestedValue(obj: Record<string, unknown>, path: string): unknown {
  const parts = path.split(".");
  let current: unknown = obj;
  for (const part of parts) {
    if (current == null || typeof current !== "object") return undefined;
    current = (current as Record<string, unknown>)[part];
  }
  return current;
}

export function setNestedValue(
  obj: Record<string, unknown>,
  path: string,
  value: unknown,
): Record<string, unknown> {
  const parts = path.split(".");
  const clone = structuredClone(obj);
  let current: Record<string, unknown> = clone;

  for (let i = 0; i < parts.length - 1; i++) {
    const key = parts[i];
    if (!(key in current) || typeof current[key] !== "object" || current[key] === null) {
      current[key] = {};
    }
    current = current[key] as Record<string, unknown>;
  }

  current[parts[parts.length - 1]] = value;
  return clone;
}

export function sortFields<T extends { order?: number }>(fields: T[]): T[] {
  return [...fields].sort((a, b) => (a.order ?? 0) - (b.order ?? 0));
}

export function defaultRepeaterItem(
  children: { key: string; type: string }[] | undefined,
): Record<string, unknown> {
  const item: Record<string, unknown> = {};
  for (const child of children ?? []) {
    if (child.type === "checkbox") item[child.key] = false;
    else if (child.type === "number") item[child.key] = null;
    else if (child.type === "multiselect") item[child.key] = [];
    else item[child.key] = "";
  }
  return item;
}

export function extractProposalFields(
  proposal: Record<string, unknown> | null | undefined,
): { name?: string; fields?: unknown[] } | null {
  if (!proposal) return null;
  const payload = (proposal as { payload?: Record<string, unknown> }).payload ?? proposal;
  const template = (payload as { template?: Record<string, unknown> }).template ?? payload;
  return template as { name?: string; fields?: unknown[] };
}
