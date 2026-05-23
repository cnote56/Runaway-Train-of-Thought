# Creative Wiki Log

> Chronological record of all updates, drafts ingested, and lore audits in the Story Bible.
> Format: `## [YYYY-MM-DD] action | Subject`

## [2026-05-23] ingest | 
- Ingested and normalized new draft to `raw/drafts/.md`.
- Extracted and updated/created lore pages:
  - Locations: [[ancient-architecture]]
  - Items: [[magic-squares]]
  - Concepts: [[ancient-magic]]

## [2026-05-23] ingest | Architects of the Source Code: RPG Skill Trees
- Ingested and normalized new draft to `raw/drafts/architects-of-the-source-code-rpg-skill-trees.md`.
- Extracted and updated/created lore pages:
  - Characters: [[the-mathematician]], [[the-occultist]], [[the-cosmologist]], [[the-artist]]
  - Concepts: [[source-code-of-reality]], [[magic-constant]], [[administrative-portfolios]], [[skill-trees]]

## [2026-05-23] ingest | The Mysterious Stranger
- Ingested and normalized new draft to `raw/drafts/the-mysterious-stranger.md`.
- Extracted and updated/created lore pages:
  - Characters: [[vance]]
  - Locations: [[capital-city]], [[subterranean-bar]]
  - Items: [[white-peanut-butter]]
  - Concepts: [[nerve-fever]], [[silver-tokens]]

## [2026-05-23] ingest | The Mysterious Stranger
- Ingested and normalized new draft to `raw/drafts/the-mysterious-stranger.md`.
- Extracted and updated/created lore pages:
  - Characters: [[vance]]
  - Locations: [[capital-city]], [[subterranean-bar]]
  - Items: [[silver-tokens]]
  - Concepts: [[nerve-fever]], [[pedwalls]]

## [2026-05-23] create | Story Bible Initialized
- Set up directory structure for the Creative Wiki.
- Wrote `SCHEMA.md` with conventions, tag taxonomy, and templates.
- Initialized `index.md` for index-based navigation.
- Initialized `log.md` for chronological logging.

## [2026-05-23] Ingest & Story Bible Construction | Kill The Sun
- Converted and archived raw `.docx` draft to `raw/drafts/kill-the-sun.md`
- Created character profile for [[edgar]] (android caretaker/infiltrator)
- Created character profile for [[janet]] (skeptical geologist)
- Created character profile for [[brady]] (historian survivor)
- Created location profile for [[the-ark]] (geothermal knowledge base)
- Created lore concept page for [[solar-fission-project]] (the cause of the great climate shift)
- Created lore concept page for [[volcanic-gases]] (Mount Mazama geological history)
- Created narrative plot outline for [[kill-the-sun-plot]]
- Integrated and cross-referenced all pages inside `index.md`

## [2026-05-23] Ingest & Story Bible Construction | The Peanut Butter Underground
- Sorted and moved original `.docx` draft from `writings of a madman` to the curated sorted path: `\\wsl.localhost\Ubuntu\home\cole\data_to_backup\misc\Creative Writing and Fiction\Science Fiction\The Peanut Butter Underground.docx`
- Extracted complete text (152,492 words) and compiled as a Markdown draft at `raw/drafts/the-peanut-butter-underground.md`
- Generated SHA-256 hash of manuscript body and stored in YAML frontmatter.
- Created character profiles for [[tony]] (protagonist), [[lucinda]] (feline provisioner), [[personati]] (redheaded rebel), and [[willie]] (underground contact).
- Created concept and lore pages for [[the-fatherhood]] (regime) and [[bloxes]] (secret police drones) and [[peanut-butter]] (restorative substance).
- Created location profiles for [[the-capital-city]] and [[the-underground]].
- Created detailed plot structure and chapter outline at [[the-peanut-butter-underground-plot]].
- Re-indexed and cross-referenced the main directory in [[index.md]].

## [2026-05-23] Ingest & Story Bible Construction | Project FILTER
- Extracted and compiled raw `.docx` draft (77,952 words) to Markdown draft at `raw/drafts/project-filter.md`.
- Created character profiles for [[reggie-watts]] (Chief of Staff), [[trevor]] (operator guide), [[jessica-powell]] (tech specialist), [[general-robinson]] (military liaison), [[clemens]] (civilian director), and [[chuck-ammerstand]] (oversight Senator).
- Created location profiles for [[washington-dc]] (surveillance-mesh capital) and [[the-digital-underground]] (shielded network sanctuaries).
- Created lore concept pages for [[the-filter]] (secure-link eye implant) and [[surveillance-protocols]] (data-collection codenames yellowbounce, chillywater, echelon, etc.).
- Created act-by-act narrative plot outline at [[project-filter-plot]].
- Updated and cross-referenced the main Story Bible directory in [[index.md]] (totaling 29 wiki pages).

## [2026-05-23] Ingest & Story Bible Construction | Blog Writing & DFS Strategy
- Discovered and parsed 10 distinct professional blog drafts, editorial instructions, and sports commentary files from the raw MSYS target directory.
- Developed and ran `scripts/ingest_blog_writings.py` inside the WSL Python virtual environment to cleanly convert all documents (`.docx`, `.txt`, `.html`) to normalized Markdown.
- Attached beautiful YAML metadata blocks to all 10 drafts, conforming directly to `SCHEMA.md` with structured title, creation date, updated date, tags, sources, and canon_status.
- Ingested files:
  - `raw/drafts/confessions-of-a-dfs-player.md` (Social critique of daily fantasy culture)
  - `raw/drafts/no-ordinary-saturday-night.md` (DFS strategy and Major League Soccer launch)
  - `raw/drafts/rage-against-the-hype-machine.md` (Media analysis on Conor McGregor's self-hype)
  - `raw/drafts/fifa-congress-and-the-bomb-threat.md` (Sepp Blatter re-election and soccer corruption)
  - `raw/drafts/unpublished-nfl-piece.md` (NFL branding rules vs players' casino events)
  - `raw/drafts/cards-hacking-scandal.md` (FBI investigation on the St. Louis Cardinals Astros hack)
  - `raw/drafts/wizards-dfs-playbook-post-draft-1.md` (NBA playoff tactical breakdown of the Wizards sweep)
  - `raw/drafts/redskins-draft-possibilities-draft.md` (Redskins draft and offensive line issues with RG3)
  - `raw/drafts/hawks-nets-series-i-expect-a-game-8.md` (NBA playoff analysis of Hawks-Nets series)
- Updated the main index at [[index.md]] with a dedicated non-fiction index and updated the overall page count of the Story Bible to 39.
