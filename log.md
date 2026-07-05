## [2026-06-21] refactor | Portability & Dynamic Pathing
- Modernized path dependencies across all scripts and documentation:
  - Updated `scripts/ingest_blog_writings.py` to dynamically resolve path dependencies in both Windows and WSL environments.
  - Updated `scripts/ingest_fiction_drafts.py` to resolve absolute pathing dynamically using `pathlib.Path`.
  - Audited and updated relative reference directories in `meta/deep_dive_compendium.md` and `meta/final_show_runner_briefing.md` to maintain path-independence.
- Verified compilation and build compatibility:
  - Ran `build_web_wiki.py` compiler; all 548 story, draft, and concept pages compiled with 40 tag taxonomies in under 1 second.
  - Updated `index.html` and verified interactive web rendering.
  - Synchronized and updated local documentation in `index.md` to reflect the 548 total pages.

## [2026-06-02] ingest | The Insect's Dilemma
- Ingested and normalized new draft to `raw/drafts/the-insects-dilemma.md`.
- Extracted and updated/created lore pages:
  - Characters: [[insect-char]]
  - Locations: [[shoebox-loc]]
  - Concepts: [[insect-trap-concept]]

## [2026-06-02] ingest | The Accident and Its Aftermath
- Ingested and normalized new draft to `raw/drafts/the-accident-and-its-aftermath.md`.
- Extracted and updated/created lore pages:
  - Characters: [[char-tony]], [[char-emily]], [[char-patricia]], [[char-doctor-tolar]]
  - Locations: [[loc-apartment]], [[loc-hospital-bed]]
  - Organizations: [[org-st-peters-hospital]], [[org-wilson-room]]
  - Items: [[item-flowers]], [[item-phone-message]]
  - Concepts: [[concept-car-accident]], [[concept-coma]], [[concept-god-questioning]]

## [2026-06-02] ingest | Home for Gilded Age
- Ingested and normalized new draft to `raw/drafts/home-for-gilded-age.md`.
- Extracted and updated/created lore pages:
  - Locations: [[home-gilded-age]]
  - Concepts: [[gilded-age-setting]], [[pella-ia-home]]

## [2026-06-02] ingest | Hell's Kitchen: A Tale of Segregation
- Ingested and normalized new draft to `raw/drafts/hells-kitchen-a-tale-of-segregation.md`.
- Extracted and updated/created lore pages:
  - Characters: [[newspaperman]]
  - Locations: [[hell-kitchen]]
  - Concepts: [[natural-order-segregation]], [[father-son-succession]]

## [2026-06-02] ingest | William Clark: The Copper King and His Untold Story
- Ingested and normalized new draft to `raw/drafts/william-clark-the-copper-king-and-his-untold-story.md`.
- Extracted and updated/created lore pages:
  - Characters: [[william-carter]], [[reginald-von-dorne]]
  - Locations: [[montana-copper-mines]]
  - Organizations: [[carter-syndicate]]
  - Concepts: [[gilded-age-conflict]]

## [2026-06-02] ingest | Heat Island
- Ingested and normalized new draft to `raw/drafts/heat-island.md`.
- Extracted and updated/created lore pages:
  - Locations: [[heat-island-city]]
  - Concepts: [[global-warming]]

## [2026-06-02] ingest | Heartbreaks and Hesitations
- Ingested and normalized new draft to `raw/drafts/heartbreaks-and-hesitations.md`.
- Extracted and updated/created lore pages:
  - Characters: [[man-on-corner]], [[protagonist]]
  - Locations: [[ups-truck]], [[street-corner]]
  - Organizations: [[ups]], [[postal-service]]
  - Items: [[book]], [[bell-ringing]]
  - Concepts: [[religion]], [[ups-vs-postal-service]]

## [2026-06-02] ingest | Alone and Tired
- Ingested and normalized new draft to `raw/drafts/alone-and-tired.md`.
- Extracted and updated/created lore pages:
  - Characters: [[dowden]]
  - Locations: [[alone_room]]
  - Concepts: [[solitude_and_questioning]], [[life_as_cooking]]

## [2026-06-02] ingest | Free Speech: Modern Abuse
- Ingested and normalized new draft to `raw/drafts/free-speech-modern-abuse.md`.
- Extracted and updated/created lore pages:
  - Concepts: [[free-speech-abuse]]

## [2026-06-02] ingest | The Old Man and His Pocket Watch
- Ingested and normalized new draft to `raw/drafts/the-old-man-and-his-pocket-watch.md`.
- Extracted and updated/created lore pages:
  - Characters: [[old-man]]
  - Locations: [[modern-world]]
  - Items: [[pocket-watch]]
  - Concepts: [[time-obsession]]

## [2026-06-02] ingest | Haunted Memories
- Ingested and normalized new draft to `raw/drafts/haunted-memories.md`.
- Extracted and updated/created lore pages:
  - Characters: [[widow-character]]
  - Locations: [[house-location]]
  - Concepts: [[haunting-concept]]

## [2026-06-02] ingest | Hated and Revered
- Ingested and normalized new draft to `raw/drafts/hated-and-revered.md`.
- Extracted and updated/created lore pages:
  - Locations: [[small-town]]
  - Concepts: [[prejudice]], [[new-kid]]

## [2026-06-02] ingest | Demon Possession of a Preacher
- Ingested and normalized new draft to `raw/drafts/demon-possession-of-a-preacher.md`.
- Extracted and updated/created lore pages:
  - Concepts: [[demon-possession]]

## [2026-06-02] ingest | The Grin
- Ingested and normalized new draft to `raw/drafts/the-grin.md`.
- Extracted and updated/created lore pages:
  - Concepts: [[grin-mystery]]

## [2026-06-02] ingest | Prisoner's Reflections
- Ingested and normalized new draft to `raw/drafts/prisoners-reflections.md`.
- Extracted and updated/created lore pages:
  - Characters: [[prisoner]]
  - Locations: [[cage]]
  - Concepts: [[sin]], [[retribution]]

## [2026-06-02] ingest | Last Rounds
- Ingested and normalized new draft to `raw/drafts/last-rounds.md`.
- Extracted and updated/created lore pages:
  - Characters: [[commander]]
  - Locations: [[last_position]]
  - Concepts: [[chain_command_protocol]]

## [2026-06-02] ingest | The Debate on Education for Undocumented Immigrants
- Ingested and normalized new draft to `raw/drafts/the-debate-on-education-for-undocumented-immigrants.md`.
- Extracted and updated/created lore pages:
  - Characters: [[william-coleman-dowden-iii]]
  - Concepts: [[american-dream]], [[constitution-and-bill-of-rights]]

## [2026-06-02] ingest | The Lonely Dwellers
- Ingested and normalized new draft to `raw/drafts/the-lonely-dwellers.md`.
- Extracted and updated/created lore pages:
  - Characters: [[dowden]]
  - Locations: [[solitary_situation]]
  - Concepts: [[life_as_cooking]], [[consumption_of_life]]

## [2026-06-02] ingest | Free Speech: Modern Abuse
- Ingested and normalized new draft to `raw/drafts/free-speech-modern-abuse.md`.
- Extracted and updated/created lore pages:
  - Concepts: [[free-speech-abuse]]

## [2026-06-02] ingest | The Wall of Sleep
- Ingested and normalized new draft to `raw/drafts/the-wall-of-sleep.md`.
- Extracted and updated/created lore pages:
  - Concepts: [[dream-threat]], [[wall-of-sleep]]

## [2026-06-02] ingest | Good Morning, Welcome Home
- Ingested and normalized new draft to `raw/drafts/good-morning-welcome-home.md`.
- Extracted and updated/created lore pages:
  - Characters: [[lonely-man]], [[best-friend-jack]], [[broken-woman]], [[baby-girl-in-bathroom]]
  - Locations: [[street-corner]], [[curb-counting-rewards]]
  - Concepts: [[city-song-orchestration]]

## [2026-06-02] ingest | The Wall of Dreams
- Ingested and normalized new draft to `raw/drafts/the-wall-of-dreams.md`.
- Extracted and updated/created lore pages:
  - Concepts: [[dream-threat]]

## [2026-06-02] ingest | The Lonely Dwellers
- Ingested and normalized new draft to `raw/drafts/the-lonely-dwellers.md`.
- Extracted and updated/created lore pages:
  - Characters: [[dowden]]
  - Locations: [[solitude]]
  - Concepts: [[misery_of_alone]]

## [2026-06-02] ingest | Free Speech: Modern Abuse
- Ingested and normalized new draft to `raw/drafts/free-speech-modern-abuse.md`.
- Extracted and updated/created lore pages:
  - Concepts: [[free-speech-abuse]]

## [2026-06-02] ingest | The Debate on Education for Undocumented Immigrants
- Ingested and normalized new draft to `raw/drafts/the-debate-on-education-for-undocumented-immigrants.md`.
- Extracted and updated/created lore pages:
  - Characters: [[william-coleman-dowden-iii]]
  - Concepts: [[american-dream]], [[education-rights-for-undocumented-immigrants]]

## [2026-06-02] ingest | God's Country: A Sacred Vow
- Ingested and normalized new draft to `raw/drafts/gods-country-a-sacred-vow.md`.
- Extracted and updated/created lore pages:
  - Locations: [[god-s-country]]
  - Concepts: [[sacred-vow]]

## [2026-06-02] ingest | Survival Without Care: Human Newborns in Extreme Circumstances
- Ingested and normalized new draft to `raw/drafts/survival-without-care-human-newborns-in-extreme-circumstances.md`.
- Extracted and updated/created lore pages:
  - Characters: [[newborn-child]]
  - Concepts: [[survival-probability-newborns]], [[genetic-mutations-and-birth-outcomes]], [[potential-for-another-species-to-care]], [[accidental-astronaut-theory]]

## [2026-06-02] ingest | God Dies From Cancer: A Love Letter to Endings
- Ingested and normalized new draft to `raw/drafts/god-dies-from-cancer-a-love-letter-to-endings.md`.
- Extracted and updated/created lore pages:
  - Characters: [[mother-character]]
  - Concepts: [[cancer-concept]], [[meaning-of-life-concept]]

## [2026-06-02] ingest | Superman's Daily Routine
- Ingested and normalized new draft to `raw/drafts/supermans-daily-routine.md`.
- Extracted and updated/created lore pages:
  - Characters: [[edwin-starr]], [[superman]]
  - Concepts: [[graviational-limits]], [[matrix-illusion]], [[glen-miller-and-nine-inch-nails-soundtrack]], [[raw-meat-show]]

## [2026-06-02] ingest | Bloodletting Lessons
- Ingested and normalized new draft to `raw/drafts/bloodletting-lessons.md`.
- Extracted and updated/created lore pages:
  - Characters: [[man-reflector]]
  - Concepts: [[bloodletting-lessons]], [[pain-and-pleasure]]

## [2026-06-02] ingest | A Burger and a Coke
- Ingested and normalized new draft to `raw/drafts/a-burger-and-a-coke.md`.
- Extracted and updated/created lore pages:
  - Characters: [[girl]]
  - Locations: [[roadside_car]]
  - Items: [[burger_and_coke]]
  - Concepts: [[ransom_game]]

## [2026-06-02] ingest | Alone and Searching
- Ingested and normalized new draft to `raw/drafts/alone-and-searching.md`.
- Extracted and updated/created lore pages:
  - Characters: [[dowden]]
  - Locations: [[alone_room]]
  - Concepts: [[life_as_cooking]], [[solitude_and_search]]

## [2026-06-02] ingest | Burn Baby Burn
- Ingested and normalized new draft to `raw/drafts/burn-baby-burn.md`.
- Extracted and updated/created lore pages:
  - Concepts: [[burning-world]], [[apocalyptic-slogan]]

## [2026-06-02] ingest | Free Speech: Modern Abuse
- Ingested and normalized new draft to `raw/drafts/free-speech-modern-abuse.md`.
- Extracted and updated/created lore pages:
  - Concepts: [[free-speech-abuse]]

## [2026-06-02] ingest | The Wall of Sleep
- Ingested and normalized new draft to `raw/drafts/the-wall-of-sleep.md`.
- Extracted and updated/created lore pages:
  - Concepts: [[wall-of-sleep-concept]]

## [2026-06-02] ingest | Free Speech: Modern Abuse
- Ingested and normalized new draft to `raw/drafts/free-speech-modern-abuse.md`.
- Extracted and updated/created lore pages:
  - Concepts: [[free-speech-abuse]]

## [2026-06-02] ingest | Mercenaries vs. The Sleepers
- Ingested and normalized new draft to `raw/drafts/mercenaries-vs-the-sleepers.md`.
- Extracted and updated/created lore pages:
  - Characters: [[free_agent]]
  - Locations: [[american_seaboard]]
  - Organizations: [[mercenaries]]
  - Concepts: [[electronic_warfare]]

## [2026-06-02] ingest | Truth Revealed
- Ingested and normalized new draft to `raw/drafts/truth-revealed.md`.
- Extracted and updated/created lore pages:
  - Characters: [[trouble-character]]
  - Concepts: [[truth-concept]], [[god-bombs-concept]]

## [2026-06-02] ingest | Life's Unavoidable Moments
- Ingested and normalized new draft to `raw/drafts/lifes-unavoidable-moments.md`.
- Extracted and updated/created lore pages:
  - Concepts: [[life-unavoidable-moments]]

## [2026-06-01] ingest | Deep Dive: 13.8.txt
- Saved original draft to `raw/drafts/13.8.txt`
- Mapped system lore: [[13-8-billion-years]], [[the-harp]], [[dobly]]
- Defined "Architect" vs "Humanist" voice signatures in the lore schema.
- Initiated Structural Audit of system.

## [2026-06-01] ingest | Deep Dive: >5k word manuscript backlog (Cluster B)
- Processed: [[traitor-soldier-grandfather]], [[underwater-wars]]
- Mapping complete for economic shadow ([[traitor-soldier-grandfather]]) and underwater resource-war mechanics ([[underwater-wars]]).
- Auditor Note: Both files exhibit strong "Architect" technical descriptors but lack the emotional "Humanist" anchors required for the show-runner briefing.
- Pending: Synthesis of BIC (Biologic/Economic) mapping into the final wiki structure.

## [2026-06-01] audit | Inbox Purge
- Removed unauthorized manuscript: `1976 - Haldeman, Joe - The Forever War V2.TXT`
- Confirmed exclusion from all ingestion pipelines and Creative Wiki archives.
- Updated cluster map to ensure no external source-material drift occurs.
