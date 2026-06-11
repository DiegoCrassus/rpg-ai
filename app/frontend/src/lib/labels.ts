export const MESA_STATUS_LABELS: Record<string, string> = {
  importing: "Importando ficha",
  active: "Ativa",
  paused: "Pausada",
  finished: "Encerrada",
  archived: "Arquivada",
};

export const IMPORT_STATUS_LABELS: Record<string, string> = {
  pending: "Na fila",
  processing: "Processando",
  proposed: "Proposta pronta",
  approved: "Aprovado",
  rejected: "Rejeitado",
  failed: "Falhou",
};

export const DOCUMENT_TYPE_LABELS: Record<string, string> = {
  rule: "Regra",
  campaign_story: "História da campanha",
  lore: "Lore",
  npc: "NPC",
  location: "Local",
  item: "Item",
  monster: "Monstro",
  organization: "Organização",
  session: "Sessão",
  summary: "Resumo",
  freeform: "Livre",
  character_story: "História do personagem",
  attachment: "Anexo",
  external_link: "Link externo",
};

export const VISIBILITY_LABELS: Record<string, string> = {
  master_only: "Somente Mestre",
  all_players: "Todos os jogadores",
  specific_players: "Jogadores específicos",
  specific_character: "Personagem específico",
  owner_private: "Privado",
  owner_only: "Somente dono",
  mesa_masters: "Mestres",
};

export const SHEET_VISIBILITY_OPTIONS = [
  { value: "owner_only", label: "Somente eu" },
  { value: "mesa_masters", label: "Mestres" },
  { value: "all_players", label: "Todos os jogadores" },
];

export const DOCUMENT_VISIBILITY_OPTIONS = [
  { value: "master_only", label: "Somente Mestre" },
  { value: "all_players", label: "Todos os jogadores" },
  { value: "specific_players", label: "Jogadores específicos" },
];

export const DOCUMENT_TYPE_OPTIONS = [
  { value: "session", label: "Sessão" },
  { value: "summary", label: "Resumo" },
  { value: "npc", label: "NPC" },
  { value: "lore", label: "Lore" },
  { value: "character_story", label: "História do personagem" },
  { value: "freeform", label: "Livre" },
];

export function isMaster(mesa: { master_id: string }, userId: string | undefined): boolean {
  return Boolean(userId && mesa.master_id === userId);
}
