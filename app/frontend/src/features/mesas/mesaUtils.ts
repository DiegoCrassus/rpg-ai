import { RPG_SYSTEM_PRESETS } from "./rpgSystems";

export const DEFAULT_SEED_MESA_NAME = "Minha Mesa D&D 5e";

export function resolveSeedMesaName(name: string): string {
  const trimmed = name.trim();
  return trimmed || DEFAULT_SEED_MESA_NAME;
}

export function resolveRpgSystem(selectId: string, customText: string): string {
  if (selectId === "custom") {
    return customText.trim();
  }
  const preset = RPG_SYSTEM_PRESETS.find((p) => p.id === selectId);
  return preset?.value ?? customText.trim();
}

export interface CreateFormInput {
  name: string;
  systemId: string;
  customSystemText: string;
  usePlatformTemplate: boolean;
  file: File | null;
}

export interface CreateFormValidation {
  valid: boolean;
  errors: {
    name?: string;
    system?: string;
    file?: string;
  };
}

export function needsImportFile(systemId: string, usePlatformTemplate: boolean): boolean {
  if (systemId === "dnd5e" && usePlatformTemplate) {
    return false;
  }
  return true;
}

export function validateCreateForm(input: CreateFormInput): CreateFormValidation {
  const errors: CreateFormValidation["errors"] = {};
  const trimmedName = input.name.trim();

  if (!trimmedName) {
    errors.name = "Informe o nome da campanha.";
  }

  if (input.systemId === "custom") {
    if (!input.customSystemText.trim()) {
      errors.system = "Informe o nome do sistema de RPG.";
    }
  } else if (!RPG_SYSTEM_PRESETS.some((p) => p.id === input.systemId)) {
    errors.system = "Selecione um sistema de RPG.";
  }

  if (needsImportFile(input.systemId, input.usePlatformTemplate) && !input.file) {
    errors.file = "Envie a ficha oficial para continuar.";
  }

  return {
    valid: Object.keys(errors).length === 0,
    errors,
  };
}
