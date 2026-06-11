import type { ValidationStatus } from "../../types/canvas";

export const ALL_VALIDATION_STATUSES: ValidationStatus[] = ["pass", "warn", "fail", "not_run"];

export type ValidationVisibility = Record<ValidationStatus, boolean>;

export const DEFAULT_VALIDATION_VISIBILITY: ValidationVisibility = {
  pass: true,
  warn: true,
  fail: true,
  not_run: true,
};

export function toggleValidationVisibility(
  current: ValidationVisibility,
  status: ValidationStatus,
): ValidationVisibility {
  return { ...current, [status]: !current[status] };
}

export function isValidationBorderVisible(
  status: ValidationStatus,
  visibility: ValidationVisibility,
): boolean {
  return visibility[status] ?? true;
}
