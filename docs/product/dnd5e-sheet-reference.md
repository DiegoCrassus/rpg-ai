# D&D 5e Character Sheet — Reference for Import Agent

> **Status:** Reference (refinement)  
> **Date:** 2026-06-11  
> **Primary source:** Wizards of the Coast **2024** character sheet ([D&D Beyond PDF](https://media.dndbeyond.com/compendium-images/phb/downloads/DnD_2024_Character-Sheet.pdf))  
> **Legacy:** 2014 sheet supported as `dnd5e_2014` with layout differences

Used by the [Sheet Import Agent](./sheet-import-agent.md) as the canonical field glossary when classifying `dnd5e_2024`.

## Editions the agent must distinguish

| ID | Pages | Distinguishing features |
|----|-------|-------------------------|
| `dnd5e_2024` | 2 | Skills under abilities; **Species** not Race; **Heroic Inspiration**; 3 attunement slots; spells on page 2 |
| `dnd5e_2014` | 3 | Skills in separate column; **Race**; Inspiration top-right; Personality Traits / Ideals / Bonds / Flaws block |

Classifier picks edition before field mapping. Wrong edition → systematic misalignment → low confidence → review.

---

## 2024 sheet — section map

### Page 1

| Section | Template keys (proposal) | Types |
|---------|--------------------------|-------|
| **Identity** | | `group` |
| | `character_name` | text |
| | `species` | text |
| | `class` | text |
| | `level` | number |
| | `subclass` | text |
| | `background` | text |
| | `alignment` | select |
| | `experience_points` | number |
| **Combat summary** | | `group` |
| | `armor_class` | number |
| | `initiative` | number |
| | `speed` | number |
| | `size` | select |
| | `passive_perception` | number |
| **Proficiency & inspiration** | | |
| | `proficiency_bonus` | number |
| | `heroic_inspiration` | checkbox |
| **Hit points** | | `group` |
| | `hp_max` | number |
| | `hp_current` | number |
| | `hp_temp` | number |
| | `hit_dice` | text |
| | `death_save_successes` | number (0–3) |
| | `death_save_failures` | number (0–3) |
| **Ability scores** (×6) | | `group` ×6 |
| | `str_score`, `str_modifier`, `str_save_proficient` | number, number, checkbox |
| | `dex_score`, … | (same pattern) |
| | `con_score`, … | |
| | `int_score`, … | |
| | `wis_score`, … | |
| | `cha_score`, … | |
| **Skills** (under parent ability) | | `repeater` or fixed keys |
| | `skill_acrobatics` | group: proficiency + modifier |
| | `skill_animal_handling` | |
| | `skill_arcana` | |
| | `skill_athletics` | |
| | `skill_deception` | |
| | `skill_history` | |
| | `skill_insight` | |
| | `skill_intimidation` | |
| | `skill_investigation` | |
| | `skill_medicine` | |
| | `skill_nature` | |
| | `skill_perception` | |
| | `skill_performance` | |
| | `skill_persuasion` | |
| | `skill_religion` | |
| | `skill_sleight_of_hand` | |
| | `skill_stealth` | |
| | `skill_survival` | |
| **Attacks** | `attacks` | `repeater` |
| | `attack_name`, `attack_bonus`, `attack_damage`, `attack_notes` | |
| **Spellcasting summary** | | `group` |
| | `spellcasting_ability` | select (int/wis/cha) |
| | `spell_modifier` | number |
| | `spell_save_dc` | number |
| | `spell_attack_bonus` | number |
| **Features & traits** | | |
| | `class_features` | `repeater` (name, description) |
| | `species_traits` | `repeater` |
| | `feats` | `repeater` |

### Page 2

| Section | Template keys | Types |
|---------|---------------|-------|
| **Coins** | `coins_cp`, `coins_sp`, `coins_ep`, `coins_gp`, `coins_pp` | number |
| **Equipment** | `equipment` | textarea |
| **Training & proficiencies** | `armor_training`, `weapon_proficiencies`, `tool_proficiencies` | textarea / multiselect |
| **Languages** | `languages` | textarea |
| **Magic item attunement** | `attunement_1`, `attunement_2`, `attunement_3` | text |
| **Cantrips & prepared spells** | `cantrips`, `prepared_spells` | `repeater` |
| **Spell slots** | `slots_level_1` … `slots_level_9` | number each |
| **Backstory & personality** | `backstory`, `appearance` | textarea |
| **Equipment list (extended)** | `equipment_detailed` | textarea |

---

## Skill → ability mapping (2024 layout)

Skills are grouped under abilities on the 2024 sheet:

| Ability | Skills |
|---------|--------|
| STR | Athletics |
| DEX | Acrobatics, Sleight of Hand, Stealth |
| INT | Arcana, History, Investigation, Nature, Religion |
| WIS | Animal Handling, Insight, Medicine, Perception, Survival |
| CHA | Deception, Intimidation, Performance, Persuasion |

Agent uses this to validate extracted proficiency positions.

---

## Proficiency encoding in template

```json
{
  "key": "skill_stealth",
  "type": "group",
  "label": "Stealth (DEX)",
  "children": [
    { "key": "proficiency", "type": "select", "constraints": { "options": ["none", "proficient", "expertise"] } },
    { "key": "modifier", "type": "number" }
  ]
}
```

Filled sheet: filled circle = `proficient`; double = `expertise`; empty = `none`.

---

## Import mapping examples

### Blank official PDF → template only

Agent outputs `template_proposal` with all fields above; `character_proposal` omitted.

### Filled scan → template + character

```json
{
  "values": {
    "character_name": "Borin",
    "species": "Dwarf",
    "class": "Fighter",
    "level": 3,
    "str_score": 16,
    "str_modifier": 3,
    "skill_athletics": { "proficiency": "proficient", "modifier": 5 },
    "hp_max": 28,
    "hp_current": 22
  }
}
```

Handwriting or poor scan → `field_confidence` &lt; 0.8 on affected keys.

---

## Alignment options (closed list for template)

`lg` | `ng` | `cg` | `ln` | `tn` | `cn` | `le` | `ne` | `ce` — store labels in UI, keys in JSON.

## Size options

`tiny` | `small` | `medium` | `large` | `huge` | `gargantuan`

---

## References

- [D&D Beyond — 2024 Character Sheet PDF](https://media.dndbeyond.com/compendium-images/phb/downloads/DnD_2024_Character-Sheet.pdf)
- [Roll20 — 2024 Character Sheet field guide](https://help.roll20.net/hc/en-us/articles/30748164251287-Dungeons-Dragons-2024-Character-Sheet)
- [RPG.SE — 2024 vs 2014 sheet differences](https://rpg.stackexchange.com/questions/212958/what-is-different-about-the-2024-character-sheets)

## Platform seed alignment

The repo seed `seeds/dnd5e/schema.json` (implementation) must match this reference. The import agent for a clean 2024 PDF should produce a template within **field key parity** of the seed — differences only in optional ordering or labels.
