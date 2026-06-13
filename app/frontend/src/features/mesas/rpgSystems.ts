export interface RpgSystemPreset {
  id: string;
  label: string;
  value: string;
  platformTemplate: boolean;
}

export const RPG_SYSTEM_PRESETS: RpgSystemPreset[] = [
  { id: "dnd5e", label: "D&D 5e", value: "D&D 5e", platformTemplate: true },
  { id: "pf2e", label: "Pathfinder 2e", value: "Pathfinder 2e", platformTemplate: false },
  { id: "coc", label: "Call of Cthulhu", value: "Call of Cthulhu", platformTemplate: false },
  { id: "custom", label: "Outro sistema…", value: "", platformTemplate: false },
];

export const DEFAULT_RPG_SYSTEM_ID = "dnd5e";
