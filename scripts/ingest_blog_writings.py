import os
import re
import datetime
from bs4 import BeautifulSoup
import docx

# Directories
WIKI_DIR = "/mnt/c/Users/Cole/creative-wiki"
DRAFTS_DIR = os.path.join(WIKI_DIR, "raw/drafts")
SOURCE_DIR = "/home/cole/data_to_backup/misc/writings of a madman/Blog Writing"

files_to_ingest = [
    {
        "source": os.path.join(SOURCE_DIR, "No ordinary Saturday Night.docx"),
        "target_name": "no-ordinary-saturday-night.md",
        "title": "No Ordinary Saturday Night",
        "created": "2015-04-26",
    },
    {
        "source": os.path.join(SOURCE_DIR, "Rage Against the Hype Machine.docx"),
        "target_name": "rage-against-the-hype-machine.md",
        "title": "Rage Against the Hype Machine",
        "created": "2015-05-01",
    },
    {
        "source": os.path.join(SOURCE_DIR, "Playbook Instructions Cole Dowden.docx"),
        "target_name": "playbook-instructions-cole-dowden.md",
        "title": "Playbook Instructions Cole Dowden",
        "created": "2015-03-01",
    },
    {
        "source": os.path.join(SOURCE_DIR, "Confessions of DFS Player.docx"),
        "target_name": "confessions-of-a-dfs-player.md",
        "title": "Confessions of a DFS Player",
        "created": "2015-10-01",
    },
    {
        "source": os.path.join(SOURCE_DIR, "May 2015 Blog Posts/published on personal blog/24412053.edited.txt"),
        "target_name": "fifa-congress-and-the-bomb-threat.md",
        "title": "FIFA Congress and the Bomb Threat",
        "created": "2015-05-29",
    },
    {
        "source": os.path.join(SOURCE_DIR, "research and references/Unpublished NFL Piece.docx"),
        "target_name": "unpublished-nfl-piece.md",
        "title": "Unpublished NFL Piece",
        "created": "2015-06-01",
    },
    {
        "source": os.path.join(SOURCE_DIR, "research and references/Cards Hacking Scandal.docx"),
        "target_name": "cards-hacking-scandal.md",
        "title": "Cards Hacking Scandal",
        "created": "2015-06-16",
    },
    {
        "source": os.path.join(SOURCE_DIR, "April 2015 Blog posts/Wizards DFS Playbook Post draft 1.html"),
        "target_name": "wizards-dfs-playbook-post-draft-1.md",
        "title": "Wizards DFS Playbook Post Draft 1",
        "created": "2015-04-27",
    },
    {
        "source": os.path.join(SOURCE_DIR, "April 2015 Blog posts/Redskins Draft Posibilities Draft.txt"),
        "target_name": "redskins-draft-possibilities-draft.md",
        "title": "Redskins Draft Possibilities Draft",
        "created": "2015-04-29",
    },
    {
        "source": os.path.join(SOURCE_DIR, "April 2015 Blog posts/Hawks Nets Series I expect a game 8.txt"),
        "target_name": "hawks-nets-series-i-expect-a-game-8.md",
        "title": "Hawks Nets Series I Expect a Game 8",
        "created": "2015-04-28",
    },
]

def extract_text(path):
    if path.endswith(".docx"):
        doc = docx.Document(path)
        paragraphs = []
        for p in doc.paragraphs:
            text = p.text.strip()
            if text:
                paragraphs.append(text)
        return "\n\n".join(paragraphs)
    elif path.endswith(".html"):
        with open(path, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f.read(), "html.parser")
            paragraphs = []
            for p in soup.find_all("p"):
                text = p.get_text().strip()
                if text:
                    paragraphs.append(text)
            if not paragraphs:
                return soup.get_text().strip()
            return "\n\n".join(paragraphs)
    else:  # .txt or other text-based files
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read().strip()

def main():
    os.makedirs(DRAFTS_DIR, exist_ok=True)
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    
    for item in files_to_ingest:
        src = item["source"]
        target_file = os.path.join(DRAFTS_DIR, item["target_name"])
        title = item["title"]
        created = item["created"]
        
        print(f"Processing: {src}")
        if not os.path.exists(src):
            print(f"Error: Source file does not exist: {src}")
            continue
            
        content = extract_text(src)
        
        # Build YAML frontmatter conforming to SCHEMA.md
        frontmatter = f"""---
title: "{title}"
created: {created}
updated: {today}
type: draft
tags: [meta, draft]
sources: [raw/drafts/{item["target_name"]}]
canon_status: draft
---

"""
        full_content = frontmatter + content
        
        with open(target_file, "w", encoding="utf-8") as f:
            f.write(full_content)
        print(f"Written to: {target_file}")

    print("\nIngestion complete. Rebuilding the web wiki...")
    try:
        import sys
        # Add root to sys.path to find build_web_wiki
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if root_dir not in sys.path:
            sys.path.append(root_dir)
        import build_web_wiki
        build_web_wiki.build_wiki()
    except Exception as e:
        print(f"Warning: Could not automatically rebuild the web wiki: {e}")

if __name__ == "__main__":
    main()
