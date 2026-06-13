export const DEFAULT_SEED_MESA_NAME = "Minha Mesa D&D 5e";

export function resolveSeedMesaName(name: string): string {
  const trimmed = name.trim();
  return trimmed || DEFAULT_SEED_MESA_NAME;
}
