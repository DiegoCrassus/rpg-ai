"""Database enum types."""

import enum


class UserStatus(str, enum.Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DELETED = "deleted"


class MesaStatus(str, enum.Enum):
    IMPORTING = "importing"
    ACTIVE = "active"
    PAUSED = "paused"
    FINISHED = "finished"
    ARCHIVED = "archived"


class ImportJobStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    PROPOSED = "proposed"
    APPROVED = "approved"
    REJECTED = "rejected"
    FAILED = "failed"


class ParticipantRole(str, enum.Enum):
    MASTER = "master"
    PLAYER = "player"


class ParticipantStatus(str, enum.Enum):
    PENDING = "pending"
    ACTIVE = "active"
    REMOVED = "removed"
    LEFT = "left"


class InviteStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class TemplateStatus(str, enum.Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"


class SheetStatus(str, enum.Enum):
    ACTIVE = "active"
    DEAD = "dead"
    RETIRED = "retired"
    ARCHIVED = "archived"


class SheetVisibility(str, enum.Enum):
    OWNER_ONLY = "owner_only"
    MESA_MASTERS = "mesa_masters"
    ALL_PLAYERS = "all_players"


class DocumentType(str, enum.Enum):
    RULE = "rule"
    CAMPAIGN_STORY = "campaign_story"
    LORE = "lore"
    NPC = "npc"
    LOCATION = "location"
    ITEM = "item"
    MONSTER = "monster"
    ORGANIZATION = "organization"
    SESSION = "session"
    SUMMARY = "summary"
    FREEFORM = "freeform"
    CHARACTER_STORY = "character_story"
    ATTACHMENT = "attachment"
    EXTERNAL_LINK = "external_link"


class DocumentVisibility(str, enum.Enum):
    MASTER_ONLY = "master_only"
    ALL_PLAYERS = "all_players"
    SPECIFIC_PLAYERS = "specific_players"
    SPECIFIC_CHARACTER = "specific_character"
    OWNER_PRIVATE = "owner_private"


class ContentFormat(str, enum.Enum):
    MARKDOWN = "markdown"
    STRUCTURED_JSON = "structured_json"


class StorageResourceType(str, enum.Enum):
    SHEET_TEMPLATE = "sheet_template"
    CHARACTER_SHEET = "character_sheet"
    DOCUMENT = "document"
    CAMPAIGN_ASSET = "campaign_asset"
    MANIFEST = "manifest"


class PermissionGranteeType(str, enum.Enum):
    USER = "user"
    CHARACTER = "character"
