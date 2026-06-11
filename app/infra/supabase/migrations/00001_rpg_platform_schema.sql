-- RPG Platform — initial schema (control plane)
-- Source of truth: docs/product/database-schema.md

CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "citext";

-- ---------------------------------------------------------------------------
-- Enums
-- ---------------------------------------------------------------------------

CREATE TYPE user_status AS ENUM ('active', 'suspended', 'deleted');
CREATE TYPE mesa_status AS ENUM ('importing', 'active', 'paused', 'finished', 'archived');
CREATE TYPE import_job_status AS ENUM ('pending', 'processing', 'proposed', 'approved', 'rejected', 'failed');
CREATE TYPE participant_role AS ENUM ('master', 'player');
CREATE TYPE participant_status AS ENUM ('pending', 'active', 'removed', 'left');
CREATE TYPE invite_status AS ENUM ('pending', 'accepted', 'expired', 'cancelled');
CREATE TYPE template_status AS ENUM ('active', 'archived');
CREATE TYPE sheet_status AS ENUM ('active', 'dead', 'retired', 'archived');
CREATE TYPE sheet_visibility AS ENUM ('owner_only', 'mesa_masters', 'all_players');
CREATE TYPE document_type AS ENUM (
  'rule', 'campaign_story', 'lore', 'npc', 'location', 'item', 'monster',
  'organization', 'session', 'summary', 'freeform', 'character_story',
  'attachment', 'external_link'
);
CREATE TYPE document_visibility AS ENUM (
  'master_only', 'all_players', 'specific_players', 'specific_character', 'owner_private'
);
CREATE TYPE content_format AS ENUM ('markdown', 'structured_json');
CREATE TYPE storage_resource_type AS ENUM (
  'sheet_template', 'character_sheet', 'document', 'campaign_asset', 'manifest'
);
CREATE TYPE permission_grantee_type AS ENUM ('user', 'character');

-- ---------------------------------------------------------------------------
-- Utility: updated_at trigger
-- ---------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ---------------------------------------------------------------------------
-- users (mirror of auth.users)
-- ---------------------------------------------------------------------------

CREATE TABLE users (
  id uuid PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email citext NOT NULL UNIQUE,
  display_name varchar(120) NOT NULL,
  avatar_storage_path text NULL,
  status user_status NOT NULL DEFAULT 'active',
  is_admin boolean NOT NULL DEFAULT false,
  master_mesa_count smallint NOT NULL DEFAULT 0,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  last_login_at timestamptz NULL
);

CREATE INDEX users_status_idx ON users (status);

CREATE TRIGGER users_set_updated_at
  BEFORE UPDATE ON users
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ---------------------------------------------------------------------------
-- mesas
-- ---------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION check_master_mesa_limit()
RETURNS TRIGGER AS $$
BEGIN
  IF (SELECT master_mesa_count FROM users WHERE id = NEW.master_id) >= 2 THEN
    RAISE EXCEPTION 'BR-01: user % already masters 2 mesas', NEW.master_id;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION increment_master_mesa_count()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.status <> 'archived' THEN
    UPDATE users
    SET master_mesa_count = master_mesa_count + 1,
        updated_at = now()
    WHERE id = NEW.master_id;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION decrement_master_mesa_count()
RETURNS TRIGGER AS $$
DECLARE
  target_user uuid;
  was_active boolean;
  is_active boolean;
BEGIN
  IF TG_OP = 'DELETE' THEN
    target_user := OLD.master_id;
    was_active := OLD.status <> 'archived';
    IF was_active THEN
      UPDATE users
      SET master_mesa_count = GREATEST(0, master_mesa_count - 1),
          updated_at = now()
      WHERE id = target_user;
    END IF;
    RETURN OLD;
  END IF;

  target_user := NEW.master_id;
  was_active := OLD.status <> 'archived';
  is_active := NEW.status <> 'archived';

  IF was_active AND NOT is_active THEN
    UPDATE users
    SET master_mesa_count = GREATEST(0, master_mesa_count - 1),
        updated_at = now()
    WHERE id = target_user;
  ELSIF NOT was_active AND is_active THEN
    UPDATE users
    SET master_mesa_count = master_mesa_count + 1,
        updated_at = now()
    WHERE id = target_user;
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TABLE mesas (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name varchar(120) NOT NULL,
  description text NULL,
  rpg_system varchar(80) NOT NULL,
  status mesa_status NOT NULL DEFAULT 'importing',
  master_id uuid NOT NULL REFERENCES users(id),
  settings jsonb NOT NULL DEFAULT '{
    "players_can_edit_own_sheet": true,
    "players_can_view_other_sheets": false,
    "character_story_requires_approval": false,
    "seed_dnd5e_template": true
  }'::jsonb,
  storage_root text NOT NULL,
  manifest_storage_path text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX mesas_master_id_idx ON mesas (master_id);
CREATE INDEX mesas_status_idx ON mesas (status);
CREATE INDEX mesas_master_id_status_idx ON mesas (master_id, status);

CREATE TRIGGER mesas_check_master_limit
  BEFORE INSERT ON mesas
  FOR EACH ROW EXECUTE FUNCTION check_master_mesa_limit();

CREATE TRIGGER mesas_increment_master_count
  AFTER INSERT ON mesas
  FOR EACH ROW EXECUTE FUNCTION increment_master_mesa_count();

CREATE TRIGGER mesas_decrement_master_count
  AFTER DELETE OR UPDATE OF status ON mesas
  FOR EACH ROW EXECUTE FUNCTION decrement_master_mesa_count();

CREATE TRIGGER mesas_set_updated_at
  BEFORE UPDATE ON mesas
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ---------------------------------------------------------------------------
-- mesa_participants
-- ---------------------------------------------------------------------------

CREATE TABLE mesa_participants (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  mesa_id uuid NOT NULL REFERENCES mesas(id) ON DELETE CASCADE,
  user_id uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  role participant_role NOT NULL,
  status participant_status NOT NULL DEFAULT 'pending',
  joined_at timestamptz NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (mesa_id, user_id)
);

CREATE INDEX mesa_participants_mesa_status_idx ON mesa_participants (mesa_id, status);
CREATE INDEX mesa_participants_user_status_idx ON mesa_participants (user_id, status);
CREATE INDEX mesa_participants_mesa_role_idx ON mesa_participants (mesa_id, role);

CREATE UNIQUE INDEX one_master_per_mesa ON mesa_participants (mesa_id)
  WHERE role = 'master' AND status = 'active';

CREATE TRIGGER mesa_participants_set_updated_at
  BEFORE UPDATE ON mesa_participants
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ---------------------------------------------------------------------------
-- invites
-- ---------------------------------------------------------------------------

CREATE TABLE invites (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  mesa_id uuid NOT NULL REFERENCES mesas(id) ON DELETE CASCADE,
  email citext NOT NULL,
  token_hash text NOT NULL UNIQUE,
  status invite_status NOT NULL DEFAULT 'pending',
  expires_at timestamptz NOT NULL,
  used_at timestamptz NULL,
  accepted_by uuid NULL REFERENCES users(id),
  created_by uuid NOT NULL REFERENCES users(id),
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX invites_mesa_status_idx ON invites (mesa_id, status);
CREATE INDEX invites_token_hash_idx ON invites (token_hash);
CREATE INDEX invites_email_mesa_idx ON invites (email, mesa_id);

-- ---------------------------------------------------------------------------
-- sheet_templates (before import jobs FK targets)
-- ---------------------------------------------------------------------------

CREATE TABLE sheet_templates (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  mesa_id uuid NOT NULL REFERENCES mesas(id) ON DELETE CASCADE,
  name varchar(120) NOT NULL,
  slug varchar(80) NOT NULL,
  description text NULL,
  status template_status NOT NULL DEFAULT 'active',
  is_seed boolean NOT NULL DEFAULT false,
  seed_key varchar(40) NULL,
  version integer NOT NULL DEFAULT 1 CHECK (version >= 1),
  storage_path text NOT NULL,
  contract varchar(64) NOT NULL DEFAULT 'rpg.sheet-template',
  contract_version varchar(20) NOT NULL DEFAULT '1.0.0',
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (mesa_id, slug)
);

CREATE INDEX sheet_templates_mesa_status_idx ON sheet_templates (mesa_id, status);

CREATE TRIGGER sheet_templates_set_updated_at
  BEFORE UPDATE ON sheet_templates
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ---------------------------------------------------------------------------
-- character_sheets (before import jobs optional FK)
-- ---------------------------------------------------------------------------

CREATE TABLE character_sheets (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  mesa_id uuid NOT NULL REFERENCES mesas(id) ON DELETE CASCADE,
  template_id uuid NOT NULL REFERENCES sheet_templates(id),
  owner_id uuid NOT NULL REFERENCES users(id),
  character_name varchar(120) NOT NULL,
  status sheet_status NOT NULL DEFAULT 'active',
  visibility sheet_visibility NOT NULL DEFAULT 'owner_only',
  template_version integer NOT NULL,
  schema_outdated boolean NOT NULL DEFAULT false,
  version integer NOT NULL DEFAULT 1 CHECK (version >= 1),
  storage_path text NOT NULL,
  meta_storage_path text NOT NULL,
  contract varchar(64) NOT NULL DEFAULT 'rpg.character-sheet',
  contract_version varchar(20) NOT NULL DEFAULT '1.0.0',
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX character_sheets_mesa_owner_idx ON character_sheets (mesa_id, owner_id);
CREATE INDEX character_sheets_mesa_status_idx ON character_sheets (mesa_id, status);
CREATE INDEX character_sheets_template_id_idx ON character_sheets (template_id);
CREATE INDEX character_sheets_mesa_name_idx ON character_sheets (mesa_id, character_name);

CREATE TRIGGER character_sheets_set_updated_at
  BEFORE UPDATE ON character_sheets
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ---------------------------------------------------------------------------
-- sheet_import_jobs
-- ---------------------------------------------------------------------------

CREATE TABLE sheet_import_jobs (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  mesa_id uuid NOT NULL REFERENCES mesas(id) ON DELETE CASCADE,
  created_by uuid NOT NULL REFERENCES users(id),
  status import_job_status NOT NULL DEFAULT 'pending',
  source_storage_path text NOT NULL,
  source_mime varchar(127) NOT NULL,
  detected_system varchar(40) NULL,
  proposal jsonb NULL,
  result_template_id uuid NULL REFERENCES sheet_templates(id),
  result_sheet_id uuid NULL REFERENCES character_sheets(id),
  error_message text NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  completed_at timestamptz NULL
);

CREATE INDEX sheet_import_jobs_mesa_status_idx ON sheet_import_jobs (mesa_id, status);

-- ---------------------------------------------------------------------------
-- sheet_template_versions
-- ---------------------------------------------------------------------------

CREATE TABLE sheet_template_versions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  template_id uuid NOT NULL REFERENCES sheet_templates(id) ON DELETE CASCADE,
  mesa_id uuid NOT NULL REFERENCES mesas(id) ON DELETE CASCADE,
  version integer NOT NULL,
  storage_path text NOT NULL,
  checksum_sha256 char(64) NOT NULL,
  created_by uuid NOT NULL REFERENCES users(id),
  created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (template_id, version)
);

-- ---------------------------------------------------------------------------
-- character_sheet_versions
-- ---------------------------------------------------------------------------

CREATE TABLE character_sheet_versions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  sheet_id uuid NOT NULL REFERENCES character_sheets(id) ON DELETE CASCADE,
  mesa_id uuid NOT NULL REFERENCES mesas(id) ON DELETE CASCADE,
  version integer NOT NULL,
  storage_path text NOT NULL,
  checksum_sha256 char(64) NOT NULL,
  created_by uuid NOT NULL REFERENCES users(id),
  created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (sheet_id, version)
);

-- ---------------------------------------------------------------------------
-- documents
-- ---------------------------------------------------------------------------

CREATE TABLE documents (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  mesa_id uuid NOT NULL REFERENCES mesas(id) ON DELETE CASCADE,
  type document_type NOT NULL,
  title varchar(200) NOT NULL,
  tags text[] NOT NULL DEFAULT '{}',
  visibility document_visibility NOT NULL,
  content_format content_format NOT NULL DEFAULT 'markdown',
  character_sheet_id uuid NULL REFERENCES character_sheets(id),
  created_by uuid NOT NULL REFERENCES users(id),
  version integer NOT NULL DEFAULT 1 CHECK (version >= 1),
  storage_path text NOT NULL,
  meta_storage_path text NOT NULL,
  deleted_at timestamptz NULL,
  contract varchar(64) NOT NULL,
  contract_version varchar(20) NOT NULL DEFAULT '1.0.0',
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT character_story_requires_sheet CHECK (
    type <> 'character_story' OR character_sheet_id IS NOT NULL
  )
);

CREATE INDEX documents_mesa_type_idx ON documents (mesa_id, type);
CREATE INDEX documents_mesa_visibility_idx ON documents (mesa_id, visibility);
CREATE INDEX documents_mesa_active_idx ON documents (mesa_id) WHERE deleted_at IS NULL;
CREATE INDEX documents_tags_gin_idx ON documents USING gin (tags);

CREATE TRIGGER documents_set_updated_at
  BEFORE UPDATE ON documents
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ---------------------------------------------------------------------------
-- document_permissions
-- ---------------------------------------------------------------------------

CREATE TABLE document_permissions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  document_id uuid NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
  mesa_id uuid NOT NULL REFERENCES mesas(id) ON DELETE CASCADE,
  grantee_type permission_grantee_type NOT NULL,
  grantee_id uuid NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (document_id, grantee_type, grantee_id)
);

CREATE INDEX document_permissions_mesa_grantee_idx
  ON document_permissions (mesa_id, grantee_type, grantee_id);

-- ---------------------------------------------------------------------------
-- document_versions
-- ---------------------------------------------------------------------------

CREATE TABLE document_versions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  document_id uuid NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
  mesa_id uuid NOT NULL REFERENCES mesas(id) ON DELETE CASCADE,
  version integer NOT NULL,
  storage_path text NOT NULL,
  checksum_sha256 char(64) NOT NULL,
  created_by uuid NOT NULL REFERENCES users(id),
  created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (document_id, version)
);

-- ---------------------------------------------------------------------------
-- campaign_assets
-- ---------------------------------------------------------------------------

CREATE TABLE campaign_assets (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  mesa_id uuid NOT NULL REFERENCES mesas(id) ON DELETE CASCADE,
  filename varchar(255) NOT NULL,
  mime_type varchar(127) NOT NULL,
  byte_size bigint NOT NULL CHECK (byte_size > 0),
  storage_path text NOT NULL,
  uploaded_by uuid NOT NULL REFERENCES users(id),
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX campaign_assets_mesa_id_idx ON campaign_assets (mesa_id);

-- ---------------------------------------------------------------------------
-- storage_files (integrity registry)
-- ---------------------------------------------------------------------------

CREATE TABLE storage_files (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  mesa_id uuid NOT NULL REFERENCES mesas(id) ON DELETE CASCADE,
  bucket varchar(64) NOT NULL DEFAULT 'campaigns',
  relative_path text NOT NULL,
  resource_type storage_resource_type NOT NULL,
  resource_id uuid NULL,
  content_type varchar(127) NOT NULL,
  contract varchar(64) NOT NULL,
  contract_version varchar(20) NOT NULL,
  entity_version integer NOT NULL DEFAULT 1,
  byte_size bigint NOT NULL,
  checksum_sha256 char(64) NOT NULL,
  last_validated_at timestamptz NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (bucket, relative_path)
);

CREATE INDEX storage_files_mesa_resource_type_idx ON storage_files (mesa_id, resource_type);
CREATE INDEX storage_files_resource_type_id_idx ON storage_files (resource_type, resource_id);

CREATE TRIGGER storage_files_set_updated_at
  BEFORE UPDATE ON storage_files
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ---------------------------------------------------------------------------
-- audit_events
-- ---------------------------------------------------------------------------

CREATE TABLE audit_events (
  id bigint PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  mesa_id uuid NULL,
  actor_id uuid NOT NULL REFERENCES users(id),
  action varchar(64) NOT NULL,
  resource_type varchar(64) NOT NULL,
  resource_id uuid NULL,
  metadata jsonb NOT NULL DEFAULT '{}',
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX audit_events_mesa_created_idx ON audit_events (mesa_id, created_at DESC);
CREATE INDEX audit_events_actor_created_idx ON audit_events (actor_id, created_at DESC);

-- ---------------------------------------------------------------------------
-- Storage buckets (API-mediated; not public)
-- ---------------------------------------------------------------------------

INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES
  (
    'profiles',
    'profiles',
    false,
    5242880,
    ARRAY['image/webp', 'image/png', 'image/jpeg']::text[]
  ),
  (
    'campaigns',
    'campaigns',
    false,
    10485760,
    NULL
  )
ON CONFLICT (id) DO UPDATE SET
  public = EXCLUDED.public,
  file_size_limit = EXCLUDED.file_size_limit,
  allowed_mime_types = EXCLUDED.allowed_mime_types;
