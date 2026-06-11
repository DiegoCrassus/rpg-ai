# User Roles and Permissions

## Two permission planes

| Plane | Roles | Scope |
|-------|-------|-------|
| **Global (platform)** | Admin, Authenticated User | Entire application |
| **Local (Mesa)** | Master, Player | One Mesa |

A user has **no single global narrative role**. Role is always evaluated in Mesa context.

## Admin (global)

Administrative platform operator. Not a story role.

| Permission | Description |
|------------|-------------|
| Access all Mesas | Read/write for support and audit |
| Manage users | Activate, suspend, delete accounts |
| Global settings | Platform configuration |
| Audit | Activity logs across Mesas |
| Override | Resolve disputes; emergency access |

**Proposal:** one or more Admin accounts; not assignable per Mesa.

## Master (per Mesa)

Full control **inside** the Mesa where they hold the Master role.

| Permission | Description |
|------------|-------------|
| Mesa CRUD | Edit name, description, system, status, settings |
| Participants | Invite, remove, change roles |
| Documents | Create, edit, delete; set visibility |
| Sheet templates | Define and version templates |
| Character sheets | View and edit all sheets in the Mesa |
| Character stories | View all; optional approval workflow |
| Secrets | Master-only materials |

**Decision (Q-002):** Exactly **one Master per Mesa** — the creator. No co-Master, no role transfer in MVP.

## Player (per Mesa)

Entry **only by invite**. Minimum necessary access.

| Permission | Description |
|------------|-------------|
| Mesa access | Only joined Mesas |
| Documents | View documents granted to them |
| Own sheet | Create/edit own character sheet (if allowed by Mesa settings) |
| Own story | Write character narrative |
| Public Mesa info | Name, description, shared materials |
| Private notes | Personal notes not visible to others |

| Denied by default | |
|-------------------|---|
| Other players' sheets | Unless Master grants |
| Master-only documents | |
| Other players' private stories | |

## Permission matrix (summary)

| Action | Admin | Master | Player |
|--------|-------|--------|--------|
| Create Mesa (max 2 as Master) | ✓ | ✓ (within cap) | ✓ (within cap) |
| Invite to Mesa | ✓ | ✓ | ✗ |
| Edit any document | ✓ | ✓ (own Mesa) | ✗ |
| View secret document | ✓ | ✓ (own Mesa) | ✗ |
| Edit own sheet | ✓ | ✓ | ✓ |
| Edit other's sheet | ✓ | ✓ (own Mesa) | ✗ |
| Platform user admin | ✓ | ✗ | ✗ |

## Document visibility levels

| Level | Audience |
|-------|----------|
| `master_only` | Masters of the Mesa only |
| `all_players` | All active Players |
| `specific_players` | Named user list |
| `specific_character` | Owner of one character |
| `owner_private` | Creator only (personal note) |

**Rule:** Master always sees everything in their Mesa. Most restrictive applicable grant wins for Players.

## Player document creation (Q-008)

**Decision:** Players **cannot** create Mesa documents (lore, NPCs, rules) in MVP. They may write **character stories** (`type: character_story`) and keep **private notes** scoped to themselves.
