---
title: "Wiki Navigation and Content Guide"
created: 2026-06-02
updated: 2026-06-02
type: guide
tags: [documentation, guide, meta]
canon_status: canon
---

# Wiki Navigation and Content Guide

### Overview
This guide serves as the authoritative map for navigating and updating the Creative Wiki. It outlines the folder architecture, the compiled web interface, active narrative universes, and the backend pipelines that maintain the integrity of this compounding story bible.

---

### Navigation Interfaces

### Interactive Web Portal (SPA)
The compiled web portal (index.html) is a highly customized single-page application designed for offline and online navigation.

- Search Bar: Evaluates search terms against title and body text in real-time, instantly filtering the sidebar catalog.
- Wikipedia Mode: Toggles a clean, serif-based readability layout optimized for long-form study.
- Category Filter: The sidebar groups pages into Characters, Locations, Organizations, Items, Concepts, Plots, and Drafts.
- Tag Cloud: Located in the sidebar footer; clicking any tag isolates pages bearing that metadata.
- Bi-directional Backlinks: Every page footer contains a panel listing other wiki entries that link directly to it.
- Obsidian Integration: The interface features deep links that open the active page directly in your local editing environment.

### Obsidian local vault
The wiki folder is configured as a local Obsidian vault.

- Graph View: Opens a visual node-network representing every markdown file and wikilink in the story bible.
- Live Editing: Allows direct text changes and markdown formatting.
- File Explorer: Mirroring the physical directory structure of the repository.

---

### Folder and Content Architecture

The workspace is organized into discrete directories, ensuring raw source materials and derived lore pages are kept distinct.

- raw/ directory: Houses immutable original sources. The drafts/ subfolder contains full chapter writeups, while fragments/ stores raw scenes or brainstorm snippets.
- entities/ directory: Contains core story assets. Divided into characters/ (motivations and narrative arcs), locations/ (settings and environments), organizations/ (factions and hierarchies), and items/ (relics and tools).
- concepts/ directory: Explains magic systems, techno-occult protocols, and fictional technologies.
- plots/ directory: Stores act-by-act outlines, scene beats, and master timelines.
- non-fiction/ directory: Archives real-world historical records and research references.
- scripts/ directory: Contains custom utility scripts utilized for text processing or pipeline automation.

---

### Active Narrative Worlds

### The Allegiance (One-Hundred-Year Man)
A technical audit of a simulated refinery reality where human life is processed as a debt-sink.

- Methodology: "Meta-Audit" or "Wiki-Churn" (the systematic breakdown of simulated elements to reveal structural errors).
- Strategic Goal: "Financial Osmosis" (converting narrative debt to ultimate creditor status, eventually forcing a foreclosure on the simulation itself).
- Atmosphere: Clinical, technical, and post-humanist.

### Cosmic Order (Planetary Servers)
A techno-occult setting where cosmic forces are governed by ancient magic squares (Kameas) operating as digital grimoires.

- Entities: The Four Kings (Amaymon, Egine, Urience, Paymon) ruling planetary servers.
- Mechanics: Gematria hack protocols, Mercury firewall re-coordination, and d88 coordinate systems.

### Project FILTER
A high-stress surveillance thriller tracking a technological tracking program in Washington D.C.

- Technology: "The Filter" (an advanced ocular implant secure-link that causes cognitive degradation and nerve tracking).
- Setting: SCIFs, subterranean networks, and digital communication grids.

### Peanut Butter Underground
A dystopian rebellion taking place beneath a totalitarian Washington D.C. ruled by the Fatherhood.

- Setting: A network of sewer tunnels beneath the Capital City.
- Key Items: "Peanut Butter" (a rare, medicinal white ointment used as currency and pain relief).

---

### Ingestion and Compile Pipelines

### The Audit-Ingest Cycle
When new creative work is submitted, it is processed via an automated workflow.

1. Archive: The raw text is written to raw/drafts/ with proper YAML frontmatter and an immutable sha256 hash.
2. Analyze: The document is audited for characters, locations, concepts, and narrative continuity.
3. Update: Relevant profiles in entities/ or concepts/ are created or amended, appending footnotes that point back to the source draft.
4. Log: The action is recorded chronologically in log.md, and the index.md file is updated.

### Web Compiler (build_web_wiki.py)
This script compiles the entire directory of markdown files into the monolithic index.html file. It scans all directories, resolves wikilink relationships, computes backlinks, calculates word counts, evaluates readability metrics, and generates the application JSON block.

### Deployment (deploy_wiki.py)
Pushes compiled HTML assets and static resources to GitHub Pages or local mirrors, ensuring deep links are maintained.

---

### System Recommendations and Critical Failure Modes

### 1. Jekyll Build Failures
GitHub Pages by default uses Jekyll to build static sites. Because this wiki compiles into a single monolithic file with custom formatting, Jekyll compilation will crash or time out.
- Failure Mode: Broken pages and 404 errors on GitHub Pages deployment.
- Prevention: An empty `.nojekyll` file must remain in the repository root to bypass Jekyll entirely and serve the raw compiled HTML file.

### 2. Wikilink Ghost Links
Deleting or renaming a lore page without updating internal references causes broken links.
- Failure Mode: Red-dashed underlines in the browser web view and broken link tooltips.
- Prevention: Perform a global search and replace across the workspace before deleting files.

### 3. Footnote Provenance Disconnection
Merging character profiles or moving text without copying footnote references breaks narrative audit trails.
- Failure Mode: Footnotes pointing to non-existent drafts or missing source origins.
- Prevention: Always append original `^[raw/drafts/file.md]` footprints when consolidating texts.

### 4. Direct Index.html Editing
Modifying the output index.html file directly.
- Failure Mode: All manual edits to index.html are instantly wiped out the next time the compiler is run.
- Prevention: Always edit the underlying markdown files in raw/, entities/, or concepts/, then run `python build_web_wiki.py` to regenerate the HTML.
