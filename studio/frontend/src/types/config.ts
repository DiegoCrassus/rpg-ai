import type { ProposalKind } from "./proposals";

export type ConfigKind = Extract<ProposalKind, "agent" | "rule" | "skill" | "command">;

export type ConfigFileEntry = {
  path: string;
  name: string;
  size_bytes?: number | null;
};

export type ConfigFileListResponse = {
  kind: ConfigKind;
  files: ConfigFileEntry[];
  q?: string | null;
};

export type ConfigFileContentResponse = {
  path: string;
  content: string;
  exists: boolean;
};
