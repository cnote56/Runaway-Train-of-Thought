# Creative Wiki Schema (Story Bible)

This schema governs the structure, taxonomy, and conventions of our compounding creative wiki (Story Bible).

## Domain
Creative projects, novels, screenplays, worldbuilding, characters, magic systems, and timelines.

## Structure & Folders
- `raw/` - Immutable raw drafts, fragments, assets.
  - `drafts/` - Completed chapters, polished scenes, outlines.
  - `fragments/` - Midnight notes, brainstorms, quick prose snippets.
- `entities/` - Profiles of concrete story elements.
  - `characters/` - Character files (physicality, motivation, arc, relationships).
  - `locations/` - Geography, settings, cities, maps.
  - `organizations/` - Guilds, factions, empires, families.
  - `items/` - Relics, weapons, artifacts, spellbooks.
- `concepts/` - Abstract lore (magic systems, history, timeline, technology).
- `plots/` - Scene outlines, act-by-act structures, chapter summaries.
- `queries/` - Brainstorms, QA investigations, hypothetical plot explorations.

## Conventions & Style
- **Filename casing:** lowercase, hyphens instead of spaces (e.g., `sir-gawain.md`, `magic-system.md`).
- **YAML Frontmatter:** Every page in the wiki (outside of index, log, schema) must start with a YAML frontmatter block.
- **Wikilinks:** Use `[[wikilink]]` format to link between pages. Maintain a high degree of cross-referencing.
- **Provenance:** Append footnotes citing the raw draft where a fact originated (e.g., `^[raw/drafts/chapter-1.md]`).
- **Canon Status:** Use the `canon_status` property to differentiate between:
  - `canon`: Firmly established facts from finished text.
  - `draft`: Ideas from unpolished drafts that might shift.
  - `apocrypha`: Ideas, brainstorms, or alternate paths not currently in main story thread.

## Frontmatter Template
```yaml
---
title: "Page Title"
created: YYYY-MM-DD
updated: YYYY-MM-DD
type: character | location | organization | item | concept | plot | query
tags: [from taxonomy below]
sources: [raw/drafts/source-file.md]
canon_status: canon | draft | apocrypha
---
```

## Tag Taxonomy
- `character` (protagonist, antagonist, supporting)
- `location` (city, landmark, region, nation, cosmos)
- `organization` (faction, family, guild, empire, cult)
- `item` (weapon, relic, technology, magic-object)
- `concept` (magic-system, historical-event, cosmology, myth, rule)
- `plot` (arc, chapter-summary, outline, act)
- `meta` (query, backtrack, draft, canon)

## Update & Canon Policies
1. **Never overwrite older lore silently:** If a new draft contradicts existing lore, note the contradiction on the page (e.g., "In [[chapter-1-draft]] Helen is described as having brown eyes, but in [[chapter-3-draft]] she has green eyes"). Flag for user decision.
2. **Threshold for Page Creation:** Create dedicated entity files only for elements mentioned in 2+ sources OR highly central to 1 source. Passing mentions should just be recorded in the scene summary.
3. **Split Pages:** If a character profile or concept page exceeds 200 lines, split it into sub-pages (e.g., `sir-gawain-history.md`, `sir-gawain-relationships.md`) with a main portal page.
