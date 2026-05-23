import os
import re
import json
import urllib.parse
from pathlib import Path

# Base directory for the wiki is resolved dynamically based on this script's location for portability
WIKI_DIR = Path(__file__).parent.resolve()
OUTPUT_HTML = WIKI_DIR / "index.html"

WIKILINK_RE = re.compile(r'\[\[([^\]|]+)(?:\|([^\]]+))?\]\]')

def parse_markdown_file(content):
    """
    Parses a markdown file's YAML frontmatter and splits it from the body.
    Supports block lists and inline lists.
    """
    metadata = {}
    body = content
    
    lines = content.splitlines()
    if lines and lines[0].strip() == "---":
        fm_lines = []
        body_start_idx = 1
        for i, line in enumerate(lines[1:], start=1):
            if line.strip() == "---":
                body_start_idx = i + 1
                break
            fm_lines.append(line)
        else:
            # No ending --- found, treat entire file as body
            body_start_idx = 0
            fm_lines = []
            
        if fm_lines:
            body = "\n".join(lines[body_start_idx:])
            current_key = None
            for line in fm_lines:
                # Skip comments and empty lines
                if not line.strip() or line.strip().startswith("#"):
                    continue
                
                # Check if it is a list item under a key
                if line.strip().startswith("-") and current_key:
                    val = line.strip()[1:].strip()
                    if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                        val = val[1:-1]
                    if isinstance(metadata.get(current_key), list):
                        metadata[current_key].append(val)
                    else:
                        metadata[current_key] = [val]
                    continue
                
                if ":" in line:
                    parts = line.split(":", 1)
                    key = parts[0].strip()
                    val = parts[1].strip()
                    current_key = key
                    
                    if not val:
                        # Might be a list starting on the next lines
                        metadata[key] = []
                    elif val.startswith("[") and val.endswith("]"):
                        # Inline list [a, b, c]
                        vals = [v.strip().strip('"').strip("'") for v in val[1:-1].split(",") if v.strip()]
                        metadata[key] = vals
                    else:
                        if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                            val = val[1:-1]
                        metadata[key] = val
                        
    return metadata, body.strip()

def get_word_count(text):
    """Simple word counter."""
    clean_text = re.sub(r'[#*`_\[\]()\-+]', ' ', text)
    words = clean_text.split()
    return len(words)

def compute_wiki_stats(pages):
    """
    Computes comprehensive writing stats and metrics for the wiki contents.
    """
    total_pages = len(pages)
    total_words = sum(p.get("word_count", 0) for p in pages)
    avg_words_per_page = round(total_words / total_pages, 1) if total_pages > 0 else 0
    
    def count_syllables(word):
        word = word.lower().strip(".:;?!,()\"'")
        if not word: 
            return 0
        vowels = "aeiouy"
        count = 0
        if word[0] in vowels:
            count += 1
        for index in range(1, len(word)):
            if word[index] in vowels and word[index - 1] not in vowels:
                count += 1
        if word.endswith("e"):
            count -= 1
        if word.endswith("le") and len(word) > 2 and word[-3] not in vowels:
            count += 1
        if count == 0:
            count = 1
        return count

    category_counts = {}
    category_words = {}
    story_drafts_count = 0
    
    for p in pages:
        g = p.get("group", "core")
        category_counts[g] = category_counts.get(g, 0) + 1
        category_words[g] = category_words.get(g, 0) + p.get("word_count", 0)
        if g == "drafts":
            story_drafts_count += 1

    readability_texts = []
    for p in pages:
        if p.get("group") in ["drafts", "fragments", "core"]:
            readability_texts.append(p.get("content", ""))
            
    combined_text = "\n".join(readability_texts)
    
    # Sentence count
    sentences = re.split(r"[.!?]+(?=\s|$)", combined_text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 5]
    sentence_count = len(sentences)
    
    # Word list for syllables
    words_for_syllable = re.findall(r"\b[a-zA-Z']+\b", combined_text)
    word_count_raw = len(words_for_syllable)
    
    total_syllables = sum(count_syllables(w) for w in words_for_syllable)
    
    asl = word_count_raw / sentence_count if sentence_count > 0 else 0
    asw = total_syllables / word_count_raw if word_count_raw > 0 else 0
    
    flesch_reading_ease = 206.835 - (1.015 * asl) - (84.6 * asw) if (asl > 0 and asw > 0) else 0
    flesch_reading_ease = max(0, min(100, round(flesch_reading_ease, 1)))
    
    fk_grade = 0.39 * asl + 11.8 * asw - 15.59 if (asl > 0 and asw > 0) else 0
    fk_grade = max(0, round(fk_grade, 1))
    
    # Hubs centrality based on backlink count
    sorted_by_backlinks = sorted(pages, key=lambda x: len(x.get("backlinks", [])), reverse=True)
    hubs = []
    for p in sorted_by_backlinks[:5]:
        if len(p.get("backlinks", [])) > 0:
            hubs.append({
                "title": p["title"],
                "path": p["path"],
                "count": len(p["backlinks"]),
                "group": p["group"]
            })

    return {
        "total_pages": total_pages,
        "total_words": total_words,
        "avg_words_per_page": avg_words_per_page,
        "category_counts": category_counts,
        "category_words": category_words,
        "story_drafts_count": story_drafts_count,
        "avg_sentence_length": round(asl, 1),
        "flesch_reading_ease": flesch_reading_ease,
        "fk_grade": fk_grade,
        "hubs": hubs
    }

def build_wiki():
    print(f"Scanning wiki directory: {WIKI_DIR}")
    if not WIKI_DIR.exists():
        print(f"Error: {WIKI_DIR} does not exist!")
        return
    
    pages = []
    
    # Recursively find all markdown files
    for md_file in WIKI_DIR.rglob("*.md"):
        # Skip output files or cache files
        if "node_modules" in md_file.parts or ".git" in md_file.parts:
            continue
            
        rel_path = md_file.relative_to(WIKI_DIR).as_posix() # use forward slashes for URLs
        
        # Read file contents
        try:
            with open(md_file, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading {md_file}: {e}")
            continue
            
        metadata, body = parse_markdown_file(content)
        
        # Extract title
        title = metadata.get("title")
        if not title:
            # Try to extract first H1 heading
            h1_match = re.search(r'^#\s+(.+)$', body, re.MULTILINE)
            if h1_match:
                title = h1_match.group(1).strip()
            else:
                title = md_file.stem.replace("-", " ").title()
        
        # Word count
        word_count = get_word_count(body)
        
        # Determine category/group based on file path
        group = "core"
        if "entities/characters" in rel_path:
            group = "characters"
        elif "entities/locations" in rel_path:
            group = "locations"
        elif "entities/organizations" in rel_path:
            group = "organizations"
        elif "entities/items" in rel_path:
            group = "items"
        elif "entities/" in rel_path:
            group = "entities"
        elif "concepts" in rel_path:
            group = "concepts"
        elif "plots" in rel_path:
            group = "plots"
        elif "raw/drafts" in rel_path:
            group = "drafts"
        elif "raw/fragments" in rel_path:
            group = "fragments"
        elif "raw/" in rel_path:
            group = "raw"
            
        pages.append({
            "path": rel_path,
            "title": title,
            "metadata": metadata,
            "content": body,
            "word_count": word_count,
            "group": group,
            "backlinks": []
        })
        
    # Build target-resolution map for [[wikilinks]] and images
    resolver_map = {}
    for p in pages:
        rel_path = p['path']
        basename = Path(rel_path).stem.lower()
        resolver_map[basename] = rel_path
        resolver_map[rel_path.lower()] = rel_path
        resolver_map[os.path.splitext(rel_path)[0].lower()] = rel_path

    # Scan for static assets (images) and add them to the resolver map
    image_extensions = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".bmp"}
    try:
        for img_file in WIKI_DIR.rglob("*"):
            if img_file.suffix.lower() in image_extensions:
                if "node_modules" in img_file.parts or ".git" in img_file.parts:
                    continue
                rel_path = img_file.relative_to(WIKI_DIR).as_posix()
                basename = img_file.name.lower()
                stem = img_file.stem.lower()
                resolver_map[basename] = rel_path
                resolver_map[stem] = rel_path
                resolver_map[rel_path.lower()] = rel_path
    except Exception as e:
        print(f"Warning: error scanning for images: {e}")

    # Compute backlinks and outgoing links
    for p in pages:
        outgoing_targets = []
        for match in WIKILINK_RE.finditer(p['content']):
            target = match.group(1).split('#')[0].strip()
            outgoing_targets.append(target)
            
        outgoing_targets = list(set(outgoing_targets))
        
        for target in outgoing_targets:
            clean_target = target.lower()
            if clean_target.endswith('.md'):
                clean_target = clean_target[:-3]
                
            resolved_path = resolver_map.get(clean_target)
            if not resolved_path:
                basename_target = Path(clean_target).name
                resolved_path = resolver_map.get(basename_target)
                
            if resolved_path and resolved_path != p['path']:
                target_page = next((x for x in pages if x['path'] == resolved_path), None)
                if target_page:
                    backlink_info = {
                        "path": p['path'],
                        "title": p['title'],
                        "group": p['group']
                    }
                    if backlink_info not in target_page['backlinks']:
                        target_page['backlinks'].append(backlink_info)

    # Collect unique tags
    all_tags = set()
    for p in pages:
        tags = p['metadata'].get('tags', [])
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",") if t.strip()]
        for tag in tags:
            all_tags.add(tag)
            
    # Calculate comprehensive writing metrics and stats
    stats = compute_wiki_stats(pages)
            
    wiki_data = {
        "pages": pages,
        "resolver_map": resolver_map,
        "tags": sorted(list(all_tags)),
        "stats": stats,
        "last_updated": Path(OUTPUT_HTML).stat().st_mtime if OUTPUT_HTML.exists() else 0
    }
    
    # Get HTML template and replace placeholder
    html_content = get_html_template()
    html_content = html_content.replace('"WIKI_DATA_JSON_PLACEHOLDER"', json.dumps(wiki_data, ensure_ascii=False))
    
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    print(f"Successfully compiled creative web wiki!")
    print(f"Output saved to: {OUTPUT_HTML}")
    print(f"Total pages compiled: {len(pages)}")
    print(f"Total tags: {len(all_tags)}")

def get_html_template():
    """Returns the raw HTML document string with placeholder."""
    return r"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Creative Wiki & Lore Vault</title>
    <!-- Tailwind CSS CDN (For structural layout) -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- FontAwesome for beautiful icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <!-- Marked.js for markdown parsing -->
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    
    <!-- Highlight.js for code block syntax highlighting -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.8.0/styles/github-dark.min.css" id="highlight-theme">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.8.0/highlight.min.js"></script>

    <!-- Custom portable CSS stylesheet (handles premium formatting, theme palettes, and group-colored highlights) -->
    <link rel="stylesheet" href="style.css">

    <script>
        tailwind.config = {
            darkMode: 'class',
            theme: {
                extend: {
                    colors: {
                        cyber: {
                            50: '#eef2ff',
                            100: '#e0e7ff',
                            500: '#3b82f6',
                            600: '#2563eb',
                            700: '#1d4ed8',
                        }
                    }
                }
            }
        }
    </script>
</head>
<body class="bg-slate-50 text-slate-900 dark:bg-slate-950 dark:text-slate-100 transition-colors duration-200">
    <!-- Wiki Application Data Placeholder -->
    <script id="wiki-data" type="application/json">
        "WIKI_DATA_JSON_PLACEHOLDER"
    </script>

    <!-- App Wrapper -->
    <div class="flex h-screen overflow-hidden flex-col md:flex-row">
        
        <!-- Left Sidebar -->
        <aside id="sidebar" class="w-full md:w-80 flex flex-col border-r border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shrink-0 z-20">
            <!-- Sidebar Header -->
            <div class="p-4 border-b border-slate-200 dark:border-slate-800 flex flex-col gap-3">
                <div class="flex items-center justify-between">
                    <div class="flex items-center gap-2">
                        <span class="text-cyber-500 text-xl" id="wiki-logo-icon"><i class="fa-solid fa-wand-magic-sparkles"></i></span>
                        <h1 class="text-lg font-bold tracking-tight bg-gradient-to-r from-blue-600 to-indigo-500 dark:from-blue-400 dark:to-cyan-400 bg-clip-text text-transparent" id="wiki-title">Creative Vault</h1>
                    </div>
                    <div class="flex items-center gap-1">
                        <button id="wikipedia-toggle" class="p-2 text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors" title="Toggle Wikipedia Mode">
                            <i class="fa-brands fa-wikipedia-w"></i>
                        </button>
                        <button id="theme-toggle" class="p-2 text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors" title="Toggle theme">
                            <i id="theme-toggle-icon" class="fa-solid fa-moon"></i>
                        </button>
                    </div>
                </div>
                <!-- Search Box -->
                <div class="relative">
                    <span class="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none text-slate-400">
                        <i class="fa-solid fa-magnifying-glass"></i>
                    </span>
                    <input type="text" id="search-input" class="w-full pl-9 pr-8 py-2 text-sm bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyber-500 focus:border-transparent" placeholder="Search characters, plots, lore...">
                    <button id="clear-search" class="absolute inset-y-0 right-0 flex items-center pr-3 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hidden">
                        <i class="fa-solid fa-circle-xmark"></i>
                    </button>
                </div>
            </div>

            <!-- Scrollable Page List -->
            <nav id="sidebar-nav" class="flex-1 overflow-y-auto p-2 space-y-4">
                <!-- Group templates will be injected here -->
            </nav>

            <!-- Sidebar Footer / Tag Cloud -->
            <div class="p-4 border-t border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950/40">
                <div class="flex items-center justify-between mb-2">
                    <span class="text-xs font-semibold uppercase tracking-wider text-slate-400">Filter by Tag</span>
                    <button id="clear-tag-filter" class="text-xs text-cyber-500 hover:underline hidden">Clear</button>
                </div>
                <div id="tag-cloud" class="flex flex-wrap gap-1 max-h-24 overflow-y-auto">
                    <!-- Tags will be injected here -->
                </div>
            </div>
        </aside>

        <!-- Main Workspace Area -->
        <main class="flex-1 flex flex-col overflow-hidden relative">
            
            <!-- Mobile Toggle Bar -->
            <div class="md:hidden flex items-center justify-between p-4 bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 shrink-0">
                <button id="mobile-menu-toggle" class="p-2 text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 rounded">
                    <i class="fa-solid fa-bars"></i> Menu
                </button>
                <div class="font-bold text-sm bg-gradient-to-r from-blue-600 to-indigo-500 dark:from-blue-400 dark:to-cyan-400 bg-clip-text text-transparent">Creative Vault</div>
            </div>

            <!-- Split View: Editor/Reader and Relationships -->
            <div class="flex-1 flex flex-col lg:flex-row overflow-hidden">
                
                <!-- Main Reader Panel -->
                <section id="reader-panel" class="flex-1 overflow-y-auto p-6 md:p-8 bg-slate-50 dark:bg-slate-950/20">
                    <div class="max-w-3xl mx-auto space-y-6">
                        
                        <!-- Page Header -->
                        <div id="page-header" class="border-b border-slate-200 dark:border-slate-800 pb-4">
                            <div class="flex flex-wrap items-center gap-2 text-xs font-semibold text-cyber-500 mb-1 uppercase tracking-wider" id="page-group-breadcrumbs">
                                <!-- Breadcrumbs -->
                            </div>
                            <h2 id="page-title" class="text-3xl md:text-4xl font-extrabold tracking-tight text-slate-900 dark:text-white mb-3">Welcome to the Wiki</h2>
                            
                            <!-- Badges & Metadata Row -->
                            <div class="flex flex-wrap items-center gap-3 text-sm text-slate-500 dark:text-slate-400" id="page-meta-row">
                                <!-- Badges (canon status, tags, word count) -->
                            </div>
                        </div>

                        <!-- Rendered Markdown Body -->
                        <article id="prose-content" class="prose-custom max-w-none text-slate-800 dark:text-slate-200">
                            <!-- Rendered Markdown -->
                        </article>
                    </div>
                </section>

                <!-- Context & Relations Sidebar -->
                <section id="context-sidebar" class="w-full lg:w-80 border-t lg:border-t-0 lg:border-l border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-6 overflow-y-auto shrink-0 space-y-6">
                    <!-- Page Attributes Card -->
                    <div>
                        <h3 class="text-xs font-bold uppercase tracking-widest text-slate-400 mb-3"><i class="fa-solid fa-circle-info mr-1"></i> File Properties</h3>
                        <div class="bg-slate-50 dark:bg-slate-950/40 border border-slate-200/60 dark:border-slate-800/60 rounded-xl p-4 space-y-3 text-xs">
                            <div class="flex justify-between">
                                <span class="text-slate-400">Local Path:</span>
                                <span id="file-path" class="font-mono text-slate-500 dark:text-slate-300 break-all select-all text-right cursor-pointer hover:text-cyber-500 transition-colors" title="Click to copy path"></span>
                            </div>
                            <div class="flex justify-between">
                                <span class="text-slate-400">Canon Status:</span>
                                <span id="file-canon" class="font-semibold uppercase tracking-wider"></span>
                            </div>
                            <div class="flex justify-between">
                                <span class="text-slate-400">Word Count:</span>
                                <span id="file-words" class="font-semibold text-slate-600 dark:text-slate-300"></span>
                            </div>
                            <div class="flex justify-between">
                                <span class="text-slate-400">Last Synced:</span>
                                <span id="file-updated" class="text-slate-500 dark:text-slate-300"></span>
                            </div>
                        </div>
                    </div>

                    <!-- Obsidian Connection Buttons -->
                    <div class="flex flex-col gap-2">
                        <a id="obsidian-link" href="#" class="flex items-center justify-center gap-2 py-2 px-3 bg-indigo-50 hover:bg-indigo-100 dark:bg-indigo-950/40 dark:hover:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400 border border-indigo-200 dark:border-indigo-800 rounded-xl text-xs font-semibold transition-colors">
                            <i class="fa-solid fa-leaf"></i> Open in Obsidian
                        </a>
                        <button id="copy-wiki-link" class="flex items-center justify-center gap-2 py-2 px-3 bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 border border-slate-300 dark:border-slate-700 rounded-xl text-xs font-semibold transition-colors">
                            <i class="fa-solid fa-copy"></i> Copy [[Wikilink]]
                        </button>
                    </div>

                    <!-- Backlinks Panel -->
                    <div>
                        <h3 class="text-xs font-bold uppercase tracking-widest text-slate-400 mb-3"><i class="fa-solid fa-link mr-1"></i> Backlinks (<span id="backlinks-count">0</span>)</h3>
                        <div id="backlinks-list" class="space-y-2">
                            <!-- Backlinks will be injected here -->
                        </div>
                    </div>
                </section>
            </div>
        </main>
    </div>

    <!-- Core App Logic -->
    <script>
        // Load data injected from Python build process
        const wikiData = JSON.parse(document.getElementById('wiki-data').textContent);
        const pages = wikiData.pages;
        const resolverMap = wikiData.resolver_map;
        const tags = wikiData.tags;

        // Statistics Dashboard Generator for Landing Page
        function generateStatsDashboardHtml() {
            if (!wikiData.stats) return '';
            const s = wikiData.stats;
            
            let readabilityLabel = "Standard";
            let readabilityColor = "text-blue-500 dark:text-blue-400";
            if (s.flesch_reading_ease >= 90) {
                readabilityLabel = "Very Easy";
                readabilityColor = "text-emerald-500 dark:text-emerald-400";
            } else if (s.flesch_reading_ease >= 80) {
                readabilityLabel = "Easy";
                readabilityColor = "text-emerald-500 dark:text-emerald-400";
            } else if (s.flesch_reading_ease >= 70) {
                readabilityLabel = "Fairly Easy";
                readabilityColor = "text-teal-500 dark:text-teal-400";
            } else if (s.flesch_reading_ease >= 60) {
                readabilityLabel = "Standard";
                readabilityColor = "text-blue-500 dark:text-blue-400";
            } else if (s.flesch_reading_ease >= 50) {
                readabilityLabel = "Fairly Hard";
                readabilityColor = "text-amber-500 dark:text-amber-400";
            } else if (s.flesch_reading_ease >= 30) {
                readabilityLabel = "Difficult";
                readabilityColor = "text-orange-500 dark:text-orange-400";
            } else {
                readabilityLabel = "Very Difficult";
                readabilityColor = "text-rose-500 dark:text-rose-400";
            }

            const groups = ['characters', 'locations', 'concepts', 'drafts', 'core'];
            const totalWordsForPct = groups.reduce((acc, g) => acc + (s.category_words[g] || 0), 0) || 1;
            
            let progressHtml = '';
            groups.forEach(g => {
                const words = s.category_words[g] || 0;
                const count = s.category_counts[g] || 0;
                const pct = Math.min(100, Math.round((words / totalWordsForPct) * 100));
                const gMeta = groupTitles[g] || { title: g, icon: 'fa-file' };
                
                let barColor = 'bg-blue-500';
                if (g === 'characters') barColor = 'bg-indigo-500';
                else if (g === 'locations') barColor = 'bg-emerald-500';
                else if (g === 'concepts') barColor = 'bg-purple-500';
                else if (g === 'drafts') barColor = 'bg-rose-500';
                
                progressHtml += `
                    <div class="space-y-1">
                        <div class="flex items-center justify-between text-xs font-medium">
                            <span class="flex items-center gap-1.5"><i class="fa-solid ${gMeta.icon} text-slate-400 dark:text-slate-500 w-3.5"></i> ${gMeta.title} (${count})</span>
                            <span class="text-slate-500 dark:text-slate-400">${words.toLocaleString()} words (${pct}%)</span>
                        </div>
                        <div class="h-1.5 w-full bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                            <div class="${barColor} h-full rounded-full" style="width: ${pct}%"></div>
                        </div>
                    </div>
                `;
            });

            let hubsHtml = '';
            if (s.hubs && s.hubs.length > 0) {
                s.hubs.forEach(h => {
                    const hMeta = groupTitles[h.group] || { title: 'Core', icon: 'fa-file' };
                    hubsHtml += `
                        <a href="#/page/${h.path}" class="flex items-center justify-between p-2 rounded-lg border border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-950/25 hover:border-cyber-500/40 hover:bg-white dark:hover:bg-slate-900 transition-all text-xs">
                            <span class="flex items-center gap-2 font-semibold">
                                <i class="fa-solid ${hMeta.icon} text-slate-400 dark:text-slate-500"></i>
                                <span class="truncate max-w-[180px] text-slate-800 dark:text-slate-200">${h.title}</span>
                            </span>
                            <span class="px-2 py-0.5 bg-cyber-50 text-cyber-700 dark:bg-cyber-950/40 dark:text-cyber-400 border border-cyber-100 dark:border-cyber-900/50 rounded-full text-[10px] font-bold">
                                ${h.count} references
                            </span>
                        </a>
                    `;
                });
            } else {
                hubsHtml = '<div class="text-slate-400 italic text-xs">No references computed yet.</div>';
            }

            return `
                <div class="mb-8 border-b border-slate-200 dark:border-slate-800 pb-6">
                    <h2 class="text-sm font-semibold uppercase tracking-wider text-slate-400 dark:text-slate-500 mb-4 flex items-center gap-2">
                        <i class="fa-solid fa-chart-line text-cyber-500"></i> Universe Statistics & Metrics
                    </h2>
                    
                    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                        <div class="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/50 flex flex-col justify-between">
                            <div class="flex items-center justify-between">
                                <span class="text-xs text-slate-400 dark:text-slate-500 font-medium uppercase">Universe Size</span>
                                <span class="p-1.5 bg-blue-50 dark:bg-blue-950/30 rounded-lg text-blue-500 dark:text-blue-400 text-xs"><i class="fa-solid fa-cube"></i></span>
                            </div>
                            <div class="mt-2">
                                <div class="text-2xl font-black">${s.total_pages}</div>
                                <div class="text-[10px] text-slate-400 dark:text-slate-500 mt-1">Compiled markdown files</div>
                            </div>
                        </div>

                        <div class="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/50 flex flex-col justify-between">
                            <div class="flex items-center justify-between">
                                <span class="text-xs text-slate-400 dark:text-slate-500 font-medium uppercase">Total Wordcount</span>
                                <span class="p-1.5 bg-indigo-50 dark:bg-indigo-950/30 rounded-lg text-indigo-500 dark:text-indigo-400 text-xs"><i class="fa-solid fa-keyboard"></i></span>
                            </div>
                            <div class="mt-2">
                                <div class="text-2xl font-black">${s.total_words.toLocaleString()}</div>
                                <div class="text-[10px] text-slate-400 dark:text-slate-500 mt-1">Avg ${Math.round(s.avg_words_per_page)} words per page</div>
                            </div>
                        </div>

                        <div class="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/50 flex flex-col justify-between">
                            <div class="flex items-center justify-between">
                                <span class="text-xs text-slate-400 dark:text-slate-500 font-medium uppercase">Readability</span>
                                <span class="p-1.5 bg-emerald-50 dark:bg-emerald-950/30 rounded-lg text-emerald-500 dark:text-emerald-400 text-xs"><i class="fa-solid fa-glasses"></i></span>
                            </div>
                            <div class="mt-2">
                                <div class="text-xl font-black truncate ${readabilityColor}">${readabilityLabel}</div>
                                <div class="text-[10px] text-slate-400 dark:text-slate-500 mt-1">Flesch Ease: ${s.flesch_reading_ease} (Grade ${s.fk_grade})</div>
                            </div>
                        </div>

                        <div class="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/50 flex flex-col justify-between">
                            <div class="flex items-center justify-between">
                                <span class="text-xs text-slate-400 dark:text-slate-500 font-medium uppercase">Sentence Length</span>
                                <span class="p-1.5 bg-rose-50 dark:bg-rose-950/30 rounded-lg text-rose-500 dark:text-rose-400 text-xs"><i class="fa-solid fa-feather-pointed"></i></span>
                            </div>
                            <div class="mt-2">
                                <div class="text-2xl font-black">${s.avg_sentence_length} <span class="text-xs font-normal text-slate-400">words</span></div>
                                <div class="text-[10px] text-slate-400 dark:text-slate-500 mt-1">Average pacing of story prose</div>
                            </div>
                        </div>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mt-4">
                        <div class="p-5 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/50 space-y-4">
                            <h3 class="text-xs font-bold uppercase tracking-wider text-slate-400 dark:text-slate-500 flex items-center gap-1.5">
                                <i class="fa-solid fa-chart-pie"></i> Word Weight & Size Distribution
                            </h3>
                            <div class="space-y-3">
                                ${progressHtml}
                            </div>
                        </div>

                        <div class="p-5 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/50 space-y-4">
                            <h3 class="text-xs font-bold uppercase tracking-wider text-slate-400 dark:text-slate-500 flex items-center gap-1.5">
                                <i class="fa-solid fa-circle-nodes"></i> Top Universe Lore Hubs
                            </h3>
                            <div class="space-y-2">
                                ${hubsHtml}
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }

        // Group metadata and mappings
        const groupTitles = {
            'core': { title: 'Core Files', icon: 'fa-book-open', order: 1 },
            'characters': { title: 'Characters', icon: 'fa-users', order: 2 },
            'locations': { title: 'Locations', icon: 'fa-map-location-dot', order: 3 },
            'organizations': { title: 'Organizations', icon: 'fa-shield-halved', order: 4 },
            'items': { title: 'Items & Relics', icon: 'fa-wand-sparkles', order: 5 },
            'concepts': { title: 'Concepts & Lore', icon: 'fa-hurricane', order: 6 },
            'plots': { title: 'Plots & Outlines', icon: 'fa-film', order: 7 },
            'drafts': { title: 'Stories & Drafts', icon: 'fa-file-pen', order: 8, collapsible: true },
            'fragments': { title: 'Fragments & Notes', icon: 'fa-puzzle-piece', order: 9, collapsible: true }
        };

        // State Management
        let currentSearch = "";
        let selectedTagFilter = null;
        let activePagePath = "";
        let collapsedGroups = JSON.parse(localStorage.getItem('wiki_collapsed_groups') || '{}');

        // Document elements
        const themeToggle = document.getElementById('theme-toggle');
        const themeToggleIcon = document.getElementById('theme-toggle-icon');
        const searchInput = document.getElementById('search-input');
        const clearSearchBtn = document.getElementById('clear-search');
        const sidebarNav = document.getElementById('sidebar-nav');
        const tagCloud = document.getElementById('tag-cloud');
        const clearTagFilterBtn = document.getElementById('clear-tag-filter');
        const mobileMenuToggle = document.getElementById('mobile-menu-toggle');
        const sidebar = document.getElementById('sidebar');
        const wikipediaToggle = document.getElementById('wikipedia-toggle');

        // --- THEME ENGINE ---
        function updateHighlightTheme(isDark) {
            const hlTheme = document.getElementById('highlight-theme');
            if (hlTheme) {
                hlTheme.href = isDark 
                    ? 'https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.8.0/styles/github-dark.min.css' 
                    : 'https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.8.0/styles/github.min.css';
            }
        }

        function initTheme() {
            // Wikipedia Theme Check
            const isWiki = localStorage.getItem('theme_wikipedia') === 'true';
            if (isWiki) {
                document.documentElement.classList.add('wikipedia-theme');
                document.body.classList.add('wikipedia-theme');
                wikipediaToggle.classList.add('text-blue-600', 'dark:text-blue-400');
                
                // Change logo to a clean styled Wikipedia style
                document.getElementById('wiki-logo-icon').innerHTML = '<i class="fa-solid fa-globe text-blue-600"></i>';
                document.getElementById('wiki-title').textContent = 'Creative Wiki';
                document.getElementById('wiki-title').className = 'text-lg font-serif tracking-tight text-slate-800 dark:text-slate-200';
            } else {
                document.documentElement.classList.remove('wikipedia-theme');
                document.body.classList.remove('wikipedia-theme');
                wikipediaToggle.classList.remove('text-blue-600', 'dark:text-blue-400');
                
                // Restore standard logo
                document.getElementById('wiki-logo-icon').innerHTML = '<i class="fa-solid fa-wand-magic-sparkles"></i>';
                document.getElementById('wiki-title').textContent = 'Creative Vault';
                document.getElementById('wiki-title').className = 'text-lg font-bold tracking-tight bg-gradient-to-r from-blue-600 to-indigo-500 dark:from-blue-400 dark:to-cyan-400 bg-clip-text text-transparent';
            }

            const savedTheme = localStorage.getItem('theme');
            const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            const isDark = savedTheme === 'dark' || (!savedTheme && systemPrefersDark);
            if (isDark) {
                document.documentElement.classList.add('dark');
                themeToggleIcon.className = 'fa-solid fa-sun';
            } else {
                document.documentElement.classList.remove('dark');
                themeToggleIcon.className = 'fa-solid fa-moon';
            }
            updateHighlightTheme(isDark);
        }

        wikipediaToggle.addEventListener('click', () => {
            const isWiki = document.documentElement.classList.contains('wikipedia-theme');
            if (isWiki) {
                localStorage.setItem('theme_wikipedia', 'false');
            } else {
                localStorage.setItem('theme_wikipedia', 'true');
            }
            initTheme();
            if (activePagePath) {
                navigateToPage(activePagePath);
            }
        });

        themeToggle.addEventListener('click', () => {
            if (document.documentElement.classList.contains('dark')) {
                document.documentElement.classList.remove('dark');
                localStorage.setItem('theme', 'light');
                themeToggleIcon.className = 'fa-solid fa-moon';
                updateHighlightTheme(false);
            } else {
                document.documentElement.classList.add('dark');
                localStorage.setItem('theme', 'dark');
                themeToggleIcon.className = 'fa-solid fa-sun';
                updateHighlightTheme(true);
            }
        });

        // --- HELPER FUNCTIONS ---
        function slugify(text) {
            return text.toString().toLowerCase().trim()
                .replace(/\s+/g, '-')
                .replace(/[^\w\-]+/g, '')
                .replace(/\-\-+/g, '-');
        }

        function resolveTarget(target, map) {
            const cleanTarget = target.trim().toLowerCase();
            const lookup = cleanTarget.endsWith('.md') ? cleanTarget.slice(0, -3) : cleanTarget;
            
            if (map[lookup]) return map[lookup];
            
            const basename = lookup.split('/').pop();
            if (map[basename]) return map[basename];
            
            return null;
        }

        // Footnote rendering
        function renderFootnotes(markdown) {
            let footnoteIndex = 1;
            const footnotes = [];
            
            let processed = markdown.replace(/\^\[([\s\S]*?)\]/g, (match, noteText) => {
                footnotes.push(noteText);
                const currentIdx = footnoteIndex++;
                return `<sup class="footnote-ref text-cyber-500 font-bold hover:text-cyber-600 cursor-pointer px-0.5" data-index="${currentIdx}" id="ref-${currentIdx}" title="${noteText.replace(/"/g, '&quot;')}">[${currentIdx}]</sup>`;
            });
            
            if (footnotes.length > 0) {
                processed += '\n\n---\n\n### References & Sources\n\n<ol class="list-decimal pl-5 text-sm text-slate-500 dark:text-slate-400 space-y-1">';
                footnotes.forEach((note, idx) => {
                    processed += `<li id="note-${idx+1}">${note} <a href="#ref-${idx+1}" class="text-cyber-500 hover:underline">↩</a></li>`;
                });
                processed += '</ol>';
            }
            return processed;
        }

        // Helper to resolve relative paths relative to a base path
        function resolveRelativePath(basePath, relativePath) {
            if (relativePath.startsWith('http://') || relativePath.startsWith('https://') || relativePath.startsWith('data:') || relativePath.startsWith('/')) {
                return relativePath;
            }
            
            const baseParts = basePath.split('/');
            baseParts.pop(); // Remove the filename
            
            const relParts = relativePath.split('/');
            
            for (const part of relParts) {
                if (part === '..') {
                    baseParts.pop();
                } else if (part === '.' || part === '') {
                    // Do nothing
                } else {
                    baseParts.push(part);
                }
            }
            
            return baseParts.join('/');
        }

        // Custom Wiki Image parser for ![[image_name|options]]
        function parseWikiImages(markdown, map, currentPagePath) {
            const wikiImageRegex = /!\[\[([^\]|]+)(?:\|([^\]]+))?\]\]/g;
            
            return markdown.replace(wikiImageRegex, (match, target, options) => {
                let cleanTarget = target.trim().toLowerCase();
                let resolvedPath = resolveTarget(cleanTarget, map);
                
                if (!resolvedPath) {
                    return `<span class="wiki-image-broken bg-rose-50 dark:bg-rose-950/20 text-rose-600 dark:text-rose-400 border border-rose-200 dark:border-rose-800 rounded-xl px-3 py-1.5 text-xs inline-flex items-center gap-1.5 my-2" title="Image '${target}' not found"><i class="fa-solid fa-image-slash"></i> [Image: ${target} not found]</span>`;
                }
                
                let width = '';
                let height = '';
                let alt = target;
                
                if (options) {
                    options = options.trim();
                    const dimMatch = options.match(/^(\d+)(?:x(\d+))?$/);
                    if (dimMatch) {
                        width = dimMatch[1];
                        if (dimMatch[2]) {
                            height = dimMatch[2];
                        }
                    } else {
                        alt = options;
                    }
                }
                
                let style = 'max-width: 100%; height: auto; display: block; margin: 1.5rem auto; border-radius: 0.75rem; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);';
                if (width) style += ` width: ${width}px;`;
                if (height) style += ` height: ${height}px;`;
                
                let imgHtml = `<img src="${resolvedPath}" alt="${alt}" style="${style}" class="wiki-image shadow-md dark:shadow-slate-900 border border-slate-200 dark:border-slate-800"`;
                if (width) imgHtml += ` width="${width}"`;
                if (height) imgHtml += ` height="${height}"`;
                imgHtml += '>';
                
                if (options && !options.match(/^\d+(?:x\d+)?$/)) {
                    return `
<div class="wiki-image-container flex flex-col items-center my-6 bg-slate-50 dark:bg-slate-900/40 p-3 rounded-2xl border border-slate-100 dark:border-slate-800 max-w-xl mx-auto">
    ${imgHtml}
    <div class="wiki-image-caption text-xs text-slate-500 dark:text-slate-400 mt-2 text-center font-medium">${options}</div>
</div>`;
                }
                
                return imgHtml;
            });
        }

        // Custom Wiki Link parser
        function parseWikiLinks(html, map) {
            return html.replace(/\[\[([^\]|]+)(?:\|([^\]]+))?\]\]/g, (match, target, label) => {
                let [cleanTarget, anchor] = target.split('#');
                let displayLabel = label || cleanTarget;
                
                let resolvedPath = resolveTarget(cleanTarget, map);
                if (resolvedPath) {
                    let hash = `#/page/${resolvedPath}`;
                    if (anchor) {
                        hash += `#${slugify(anchor)}`;
                    }
                    
                    // Look up target page properties to append specific styling category
                    const targetPage = pages.find(p => p.path === resolvedPath);
                    const group = targetPage ? targetPage.group : 'core';
                    
                    return `<a href="${hash}" class="wiki-link wiki-link-${group}" data-target="${resolvedPath}">${displayLabel}</a>`;
                } else {
                    return `<span class="wiki-link-broken" title="Lore page '${cleanTarget}' does not exist yet">${displayLabel}</span>`;
                }
            });
        }

        // --- RENDER SIDEBAR ---
        function renderSidebar() {
            sidebarNav.innerHTML = '';
            
            const groupedPages = {};
            Object.keys(groupTitles).forEach(k => groupedPages[k] = []);
            
            pages.forEach(p => {
                const group = p.group || 'core';
                
                const matchesSearch = currentSearch === "" || 
                    p.title.toLowerCase().includes(currentSearch.toLowerCase()) || 
                    p.content.toLowerCase().includes(currentSearch.toLowerCase()) ||
                    (p.metadata.tags && p.metadata.tags.some(t => t.toLowerCase().includes(currentSearch.toLowerCase())));
                    
                const matchesTag = !selectedTagFilter || 
                    (p.metadata.tags && p.metadata.tags.includes(selectedTagFilter));
                    
                if (matchesSearch && matchesTag) {
                    if (groupedPages[group]) {
                        groupedPages[group].push(p);
                    } else {
                        groupedPages['core'].push(p);
                    }
                }
            });

            const sortedGroups = Object.keys(groupTitles).sort((a, b) => groupTitles[a].order - groupTitles[b].order);
            
            sortedGroups.forEach(gKey => {
                const groupInfo = groupTitles[gKey];
                const list = groupedPages[gKey];
                
                if (list.length === 0) return;

                const isCollapsible = groupInfo.collapsible;
                const isCollapsed = collapsedGroups[gKey];

                const groupContainer = document.createElement('div');
                groupContainer.className = 'space-y-1 mb-3';

                const header = document.createElement('div');
                header.className = `flex items-center justify-between px-3 py-1 text-xs font-bold text-slate-400 uppercase tracking-widest ${isCollapsible ? 'cursor-pointer hover:text-slate-200' : ''}`;
                
                let headerContent = `<span><i class="fa-solid ${groupInfo.icon} mr-1.5 opacity-70"></i> ${groupInfo.title}</span>`;
                if (isCollapsible) {
                    headerContent += `<i class="fa-solid ${isCollapsed ? 'fa-chevron-right' : 'fa-chevron-down'} text-[10px] opacity-70"></i>`;
                }
                header.innerHTML = headerContent;

                if (isCollapsible) {
                    header.addEventListener('click', () => {
                        collapsedGroups[gKey] = !collapsedGroups[gKey];
                        localStorage.setItem('wiki_collapsed_groups', JSON.stringify(collapsedGroups));
                        renderSidebar();
                    });
                }

                groupContainer.appendChild(header);

                if (!isCollapsed) {
                    const itemsContainer = document.createElement('div');
                    itemsContainer.className = 'space-y-[2px]';
                    
                    list.sort((a, b) => a.title.localeCompare(b.title));
                    
                    list.forEach(p => {
                        const link = document.createElement('a');
                        link.href = `#/page/${p.path}`;
                        
                        const isActive = p.path === activePagePath;
                        link.className = `flex items-center justify-between px-3 py-1.5 rounded-lg text-sm transition-all duration-150 select-none ${
                            isActive 
                                ? 'bg-cyber-50 dark:bg-cyber-950/50 text-cyber-500 font-semibold border-l-2 border-cyber-500 pl-2.5' 
                                : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800/60 hover:text-slate-900 dark:hover:text-slate-100'
                        }`;
                        
                        let canonIndicator = '';
                        if (p.metadata.canon_status === 'canon') {
                            canonIndicator = '<span class="text-[10px] text-green-500 ml-1.5" title="Canon"><i class="fa-solid fa-circle-check"></i></span>';
                        } else if (p.metadata.canon_status === 'apocrypha') {
                            canonIndicator = '<span class="text-[10px] text-purple-400 ml-1.5" title="Apocrypha"><i class="fa-solid fa-ghost"></i></span>';
                        }
                        
                        link.innerHTML = `
                            <span class="truncate pr-1">${p.title} ${canonIndicator}</span>
                            <span class="text-[10px] text-slate-400 shrink-0 font-mono">${p.word_count} w</span>
                        `;
                        itemsContainer.appendChild(link);
                    });
                    groupContainer.appendChild(itemsContainer);
                }

                sidebarNav.appendChild(groupContainer);
            });
        }

        // --- RENDER TAG CLOUD ---
        function renderTagCloud() {
            tagCloud.innerHTML = '';
            tags.forEach(tag => {
                const isSelected = selectedTagFilter === tag;
                const tagEl = document.createElement('button');
                tagEl.className = `text-xs px-2 py-1 rounded-md border font-medium transition-all duration-150 ${
                    isSelected 
                        ? 'bg-cyber-500 border-cyber-500 text-white shadow-sm' 
                        : 'bg-white dark:bg-slate-900 border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-400 hover:border-slate-300 dark:hover:border-slate-700'
                }`;
                tagEl.textContent = `#${tag}`;
                
                tagEl.addEventListener('click', () => {
                    if (selectedTagFilter === tag) {
                        selectedTagFilter = null;
                        clearTagFilterBtn.classList.add('hidden');
                    } else {
                        selectedTagFilter = tag;
                        clearTagFilterBtn.classList.remove('hidden');
                    }
                    renderTagCloud();
                    renderSidebar();
                });
                
                tagCloud.appendChild(tagEl);
            });
        }

        clearTagFilterBtn.addEventListener('click', () => {
            selectedTagFilter = null;
            clearTagFilterBtn.classList.add('hidden');
            renderTagCloud();
            renderSidebar();
        });

        // --- ROUTING ENGINE ---
        function navigateToPage(path) {
            activePagePath = path;
            renderSidebar();
            
            const page = pages.find(p => p.path === path);
            if (!page) {
                document.getElementById('page-title').textContent = "Select a Wiki Page";
                document.getElementById('prose-content').innerHTML = `
                    <div class="text-center py-16 opacity-60">
                        <i class="fa-solid fa-book-open text-5xl mb-4 text-slate-300 dark:text-slate-700"></i>
                        <p class="text-lg">Click any item in the sidebar to read the creative wiki.</p>
                        <p class="text-sm mt-2">Use the search box above to quickly find characters, events, or world details.</p>
                    </div>
                `;
                document.getElementById('page-group-breadcrumbs').innerHTML = '';
                document.getElementById('page-meta-row').innerHTML = '';
                document.getElementById('file-path').textContent = 'N/A';
                document.getElementById('file-canon').textContent = 'N/A';
                document.getElementById('file-words').textContent = '0 words';
                document.getElementById('file-updated').textContent = 'N/A';
                document.getElementById('backlinks-count').textContent = '0';
                document.getElementById('backlinks-list').innerHTML = '<div class="text-slate-400 italic text-xs">No backlinks found.</div>';
                document.getElementById('obsidian-link').classList.add('pointer-events-none', 'opacity-50');
                return;
            }

            document.getElementById('obsidian-link').classList.remove('pointer-events-none', 'opacity-50');
            const vaultName = "creative-wiki";
            const obsidianUrl = `obsidian://open?vault=${encodeURIComponent(vaultName)}&file=${encodeURIComponent(page.path)}`;
            document.getElementById('obsidian-link').href = obsidianUrl;

            document.getElementById('page-title').textContent = page.title;
            const groupInfo = groupTitles[page.group] || { title: 'Wiki', icon: 'fa-file' };
            document.getElementById('page-group-breadcrumbs').innerHTML = `
                <span class="flex items-center gap-1"><i class="fa-solid ${groupInfo.icon} text-[10px]"></i> ${groupInfo.title}</span>
                <span class="text-slate-300 dark:text-slate-700">/</span>
                <span class="text-slate-400 lowercase select-all">${page.path.split('/').pop()}</span>
            `;

            let metaHtml = '';
            const status = page.metadata.canon_status || 'draft';
            let statusColor = 'bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-950/30 dark:text-amber-400 dark:border-amber-800/50';
            if (status === 'canon') {
                statusColor = 'bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-950/30 dark:text-emerald-400 dark:border-emerald-800/50';
            } else if (status === 'apocrypha') {
                statusColor = 'bg-purple-50 text-purple-700 border-purple-200 dark:bg-purple-950/30 dark:text-purple-400 dark:border-purple-800/50';
            }
            
            metaHtml += `<span class="px-2.5 py-0.5 rounded-full border text-xs font-semibold capitalize ${statusColor}">${status}</span>`;
            
            if (page.metadata.tags) {
                const tagsList = Array.isArray(page.metadata.tags) ? page.metadata.tags : [page.metadata.tags];
                tagsList.forEach(t => {
                    metaHtml += `<span class="px-2 py-0.5 bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 rounded border border-slate-200 dark:border-slate-700 text-xs font-medium cursor-pointer hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors" onclick="selectTagFilterFromBadge('${t}')">#${t}</span>`;
                });
            }
            metaHtml += `<span class="text-xs text-slate-400 ml-auto"><i class="fa-solid fa-hourglass-half mr-1"></i> ${page.word_count} words</span>`;
            document.getElementById('page-meta-row').innerHTML = metaHtml;

            let mdContent = page.content;
            mdContent = parseWikiImages(mdContent, resolverMap, page.path);
            mdContent = renderFootnotes(mdContent);
            const rawHtml = marked.parse(mdContent);
            let linkedHtml = parseWikiLinks(rawHtml, resolverMap);

            if (path === "index.md") {
                linkedHtml = generateStatsDashboardHtml() + linkedHtml;
            }

            // --- WIKIPEDIA CORE RENDERING OVERRIDE ---
            const isWikiTheme = document.documentElement.classList.contains('wikipedia-theme');
            let existingTagline = document.getElementById('wiki-tagline');
            if (existingTagline) existingTagline.remove();

            if (isWikiTheme) {
                document.getElementById('page-group-breadcrumbs').style.display = 'none';
                document.getElementById('page-meta-row').style.display = 'none';
                document.getElementById('context-sidebar').style.display = 'none';
                
                // Inject Wikipedia Subtitle tagline
                const tagline = document.createElement('div');
                tagline.id = 'wiki-tagline';
                tagline.className = 'text-xs text-slate-400 italic mt-1 border-b border-slate-200 dark:border-slate-800 pb-1 mb-2';
                tagline.textContent = 'From Creative Wiki, the free encyclopedia of your universe';
                document.getElementById('page-header').appendChild(tagline);

                // Build Wikipedia floating infobox table
                let backlinksHtml = '';
                if (page.backlinks && page.backlinks.length > 0) {
                    backlinksHtml = page.backlinks.map(bl => `<div class="mb-0.5"><a href="#/page/${bl.path}" class="text-blue-600 dark:text-blue-400 hover:underline font-normal">${bl.title}</a></div>`).join('');
                } else {
                    backlinksHtml = '<div class="text-slate-400 dark:text-slate-500 italic">None</div>';
                }

                let tagsHtml = '';
                if (page.metadata.tags) {
                    const tagsList = Array.isArray(page.metadata.tags) ? page.metadata.tags : [page.metadata.tags];
                    tagsHtml = tagsList.map(t => `<span class="inline-block bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300 rounded px-1.5 py-0.5 text-[10px] mr-1 mb-1 select-all cursor-pointer hover:bg-slate-200 dark:hover:bg-slate-700" onclick="selectTagFilterFromBadge('${t}')">#${t}</span>`).join('');
                } else {
                    tagsHtml = '<span class="text-slate-400 dark:text-slate-500 italic">None</span>';
                }

                const infoboxHtml = `
                    <table class="wikipedia-infobox border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-900/30 text-xs w-64 float-right ml-4 mb-4" style="border-collapse: collapse; font-family: sans-serif;">
                        <tbody>
                            <tr>
                                <th colspan="2" class="text-center font-bold p-1 bg-slate-200 dark:bg-slate-800" style="text-align: center; background-color: #eaecf0; font-size: 110%;">${page.title}</th>
                            </tr>
                            <tr>
                                <td class="font-bold text-slate-500 dark:text-slate-400" style="width: 35%;">Category</td>
                                <td>${groupTitles[page.group] ? groupTitles[page.group].title : 'Core'}</td>
                            </tr>
                            <tr>
                                <td class="font-bold text-slate-500 dark:text-slate-400">Status</td>
                                <td class="capitalize font-semibold">${page.metadata.canon_status || 'draft'}</td>
                            </tr>
                            <tr>
                                <td class="font-bold text-slate-500 dark:text-slate-400">Word Count</td>
                                <td>${page.word_count} words</td>
                            </tr>
                            <tr>
                                <td class="font-bold text-slate-500 dark:text-slate-400">File Path</td>
                                <td class="font-mono text-[10px] break-all select-all text-slate-600 dark:text-slate-300">${page.path}</td>
                            </tr>
                            <tr>
                                <td class="font-bold text-slate-500 dark:text-slate-400">Last Synced</td>
                                <td>${page.metadata.updated || page.metadata.created || 'N/A'}</td>
                            </tr>
                            <tr>
                                <td class="font-bold text-slate-500 dark:text-slate-400">Tags</td>
                                <td><div class="flex flex-wrap">${tagsHtml}</div></td>
                            </tr>
                            <tr>
                                <td class="font-bold text-slate-500 dark:text-slate-400">Backlinks</td>
                                <td>${backlinksHtml}</td>
                            </tr>
                        </tbody>
                    </table>
                `;
                
                linkedHtml = infoboxHtml + linkedHtml;
            } else {
                document.getElementById('page-group-breadcrumbs').style.display = 'flex';
                document.getElementById('page-meta-row').style.display = 'flex';
                document.getElementById('context-sidebar').style.display = 'block';
            }

            // Dynamic Search Term Highlight (Matches visual editor search experience)
            if (currentSearch && currentSearch.length >= 2) {
                try {
                    const escapedSearch = currentSearch.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
                    const regex = new RegExp(`(${escapedSearch})`, 'gi');
                    const tempDiv = document.createElement('div');
                    tempDiv.innerHTML = linkedHtml;
                    
                    const highlightTextNodes = (node) => {
                        if (node.nodeType === 3) { // TEXT_NODE
                            const text = node.nodeValue;
                            if (regex.test(text)) {
                                const span = document.createElement('span');
                                span.innerHTML = text.replace(regex, '<mark class="search-match">$1</mark>');
                                node.parentNode.replaceChild(span, node);
                            }
                        } else if (node.nodeType === 1 && node.nodeName !== 'A' && node.nodeName !== 'SCRIPT' && node.nodeName !== 'STYLE' && node.nodeName !== 'CODE') {
                            Array.from(node.childNodes).forEach(highlightTextNodes);
                        }
                    };
                    Array.from(tempDiv.childNodes).forEach(highlightTextNodes);
                    linkedHtml = tempDiv.innerHTML;
                } catch (e) {
                    console.error("Search highlight error:", e);
                }
            }

            const contentPanel = document.getElementById('prose-content');
            contentPanel.innerHTML = linkedHtml;

            // Trigger code syntax highlighting
            document.querySelectorAll('#prose-content pre code').forEach((el) => {
                hljs.highlightElement(el);
            });

            document.getElementById('file-path').textContent = page.path;
            document.getElementById('file-canon').textContent = status;
            document.getElementById('file-words').textContent = `${page.word_count} words`;
            document.getElementById('file-updated').textContent = page.metadata.updated || page.metadata.created || 'N/A';

            const backlinksCount = page.backlinks.length;
            document.getElementById('backlinks-count').textContent = backlinksCount;
            
            const blContainer = document.getElementById('backlinks-list');
            blContainer.innerHTML = '';
            if (backlinksCount === 0) {
                blContainer.innerHTML = '<div class="text-slate-400 italic text-xs py-1">No incoming links.</div>';
            } else {
                page.backlinks.forEach(bl => {
                    const blGroup = groupTitles[bl.group] || { title: 'Wiki', icon: 'fa-file' };
                    const blCard = document.createElement('a');
                    blCard.href = `#/page/${bl.path}`;
                    blCard.className = 'block p-2 rounded-lg border border-slate-100 dark:border-slate-800 hover:border-cyber-500/50 bg-slate-50/50 dark:bg-slate-950/20 hover:bg-white dark:hover:bg-slate-900 transition-all duration-150';
                    blCard.innerHTML = `
                        <div class="font-semibold text-xs text-slate-800 dark:text-slate-200 truncate">${bl.title}</div>
                        <div class="text-[10px] text-slate-400 mt-0.5 flex items-center gap-1"><i class="fa-solid ${blGroup.icon} text-[9px]"></i> ${blGroup.title}</div>
                    `;
                    blContainer.appendChild(blCard);
                });
            }

            document.getElementById('reader-panel').scrollTop = 0;
            
            if (window.innerWidth < 768) {
                sidebar.classList.add('hidden');
            }
        }

        window.selectTagFilterFromBadge = function(tag) {
            selectedTagFilter = tag;
            clearTagFilterBtn.classList.remove('hidden');
            renderTagCloud();
            renderSidebar();
        }

        // Path copier
        document.getElementById('file-path').addEventListener('click', () => {
            const path = document.getElementById('file-path').textContent;
            navigator.clipboard.writeText(path).then(() => {
                const el = document.getElementById('file-path');
                const oldColor = el.className;
                el.className = "font-mono text-green-500 break-all select-all text-right cursor-pointer";
                const oldText = el.textContent;
                el.textContent = "COPIED PATH!";
                setTimeout(() => {
                    el.className = oldColor;
                    el.textContent = oldText;
                }, 1500);
            });
        });

        // Copy wiki link
        document.getElementById('copy-wiki-link').addEventListener('click', () => {
            const page = pages.find(p => p.path === activePagePath);
            if (!page) return;
            const basename = page.path.split('/').pop().replace('.md', '');
            const wikilink = `[[${basename}]]`;
            
            navigator.clipboard.writeText(wikilink).then(() => {
                const btn = document.getElementById('copy-wiki-link');
                const originalHtml = btn.innerHTML;
                btn.innerHTML = '<i class="fa-solid fa-check"></i> Copied!';
                btn.className = "flex items-center justify-center gap-2 py-2 px-3 bg-green-500 hover:bg-green-600 text-white rounded-xl text-xs font-semibold transition-colors";
                setTimeout(() => {
                    btn.innerHTML = originalHtml;
                    btn.className = "flex items-center justify-center gap-2 py-2 px-3 bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 border border-slate-300 dark:border-slate-700 rounded-xl text-xs font-semibold transition-colors";
                }, 1500);
            });
        });

        function handleRoute() {
            const hash = window.location.hash;
            if (hash.startsWith('#/page/')) {
                const path = hash.replace('#/page/', '');
                let [cleanPath, anchor] = path.split('#');
                navigateToPage(cleanPath);
                
                if (anchor) {
                    setTimeout(() => {
                        const element = document.getElementById(anchor) || document.getElementById(decodeURIComponent(anchor));
                        if (element) {
                            element.scrollIntoView({ behavior: 'smooth' });
                        }
                    }, 300);
                }
            } else {
                navigateToPage("index.md");
            }
        }

        window.addEventListener('hashchange', handleRoute);

        // --- SEARCH BAR SYSTEM ---
        searchInput.addEventListener('input', (e) => {
            currentSearch = e.target.value.trim();
            if (currentSearch !== "") {
                clearSearchBtn.classList.remove('hidden');
            } else {
                clearSearchBtn.classList.add('hidden');
            }
            renderSidebar();
        });

        clearSearchBtn.addEventListener('click', () => {
            searchInput.value = '';
            currentSearch = '';
            clearSearchBtn.classList.add('hidden');
            renderSidebar();
        });

        // --- MOBILE MENU ---
        mobileMenuToggle.addEventListener('click', () => {
            sidebar.classList.toggle('hidden');
        });

        window.addEventListener('resize', () => {
            if (window.innerWidth >= 768) {
                sidebar.classList.remove('hidden');
            } else {
                sidebar.classList.add('hidden');
            }
        });

        // --- ON INITIAL LOADING ---
        initTheme();
        renderTagCloud();
        
        marked.setOptions({
            gfm: true,
            breaks: true,
            headerIds: true,
            mangle: false
        });

        // Custom Marked renderer to style standard markdown images and resolve relative paths
        const renderer = new marked.Renderer();
        renderer.image = function(href, title, text) {
            let resolvedHref = href;
            if (href && !href.startsWith('http') && !href.startsWith('/') && !href.startsWith('data:')) {
                resolvedHref = resolveRelativePath(activePagePath, href);
            }
            return `<img src="${resolvedHref}" alt="${text || ''}" title="${title || ''}" class="wiki-image shadow-md dark:shadow-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl max-w-full my-4" style="max-height: 500px; display: block; margin-left: auto; margin-right: auto;">`;
        };
        marked.use({ renderer });

        if (window.innerWidth < 768) {
            sidebar.classList.add('hidden');
        }
        handleRoute();
    </script>
</body>
</html>
"""

if __name__ == "__main__":
    build_wiki()
