export type FieldType =
  | "text"
  | "textarea"
  | "number"
  | "checkbox"
  | "select"
  | "multiselect"
  | "group"
  | "repeater"
  | "image"
  | "file";

export interface FieldConstraints {
  max_length?: number;
  min?: number;
  max?: number;
  integer?: boolean;
  options?: string[];
  max_items?: number;
  allowed_extensions?: string[];
}

export interface SheetField {
  key: string;
  type: FieldType;
  label: string;
  required?: boolean;
  order?: number;
  item_label?: string;
  constraints?: FieldConstraints;
  children?: SheetField[];
}

export interface User {
  id: string;
  email: string;
  display_name: string;
  is_admin: boolean;
  status: string;
  avatar_storage_path?: string | null;
  avatar_url?: string | null;
  master_mesa_count?: number;
}

export interface Mesa {
  id: string;
  name: string;
  description: string | null;
  rpg_system: string;
  status: string;
  master_id: string;
  settings: Record<string, unknown>;
}

export interface ImportJob {
  id: string;
  status: string;
  source_storage_path: string;
  source_mime: string;
  detected_system: string | null;
  proposal: Record<string, unknown> | null;
  error_message: string | null;
}

export interface Template {
  id: string;
  name: string;
  slug: string;
  description: string | null;
  status: string;
  version: number;
  is_seed: boolean;
}

export interface Character {
  id: string;
  character_name: string;
  owner_id: string;
  template_id: string;
  visibility: string;
  version: number;
  status: string;
}

export interface Document {
  id: string;
  title: string;
  type: string;
  visibility: string;
  tags: string[];
  version: number;
  content_format: string;
}

export interface Participant {
  id: string;
  user_id: string;
  role: string;
  status: string;
}

export interface Invite {
  id: string;
  email: string;
  status: string;
  expires_at: string;
  token?: string;
}

export interface ApiErrorBody {
  error?: {
    code?: string;
    message?: string;
    details?: unknown;
  };
}

export interface ContractEnvelope<T = unknown> {
  contract: string;
  contract_version: string;
  meta: Record<string, unknown>;
  payload: T;
}

export interface SheetTemplatePayload {
  name: string;
  description?: string;
  slug: string;
  is_seed?: boolean;
  seed_key?: string;
  fields: SheetField[];
}

export interface CharacterSheetPayload {
  template_id: string;
  template_entity_version: number;
  values: Record<string, unknown>;
}

export interface AdminUser {
  id: string;
  email: string;
  display_name: string;
  status: string;
  is_admin: boolean;
  master_mesa_count: number;
}

export interface AdminMesa {
  id: string;
  name: string;
  status: string;
  master_id: string;
  rpg_system: string;
}

export interface AuditEvent {
  id: number;
  mesa_id: string | null;
  actor_id: string;
  action: string;
  resource_type: string;
  resource_id: string | null;
  created_at: string;
}
