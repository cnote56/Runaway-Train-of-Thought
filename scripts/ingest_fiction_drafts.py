import os
import re
import datetime
import subprocess
import docx
from striprtf.striprtf import rtf_to_text

# Directories
WIKI_DIR = r"C:\Users\Cole\creative-wiki"
DRAFTS_DIR = os.path.join(WIKI_DIR, "raw", "drafts")
SOURCE_DIR = r"//wsl.localhost/Ubuntu/home/cole/data_to_backup/misc/writings of a madman/fiction/almost done"

def clean_filename(title):
    # Convert title to a lowercase hyphenated slug
    slug = title.strip().lower()
    slug = re.sub(r"'s", "s", slug)  # Ted's -> teds
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = slug.strip("-")
    return slug

def extract_text_doc(path):
    # Use antiword to extract text from .doc files
    try:
        result = subprocess.run(["antiword", path], capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except Exception as e:
        print(f"Error running antiword on {path}: {e}")
        return None

def extract_text_docx(path):
    try:
        doc = docx.Document(path)
        paragraphs = []
        for p in doc.paragraphs:
            text = p.text.strip()
            if text:
                paragraphs.append(text)
        return "\n\n".join(paragraphs)
    except Exception as e:
        print(f"Error parsing .docx {path}: {e}")
        return None

def extract_text_rtf(path):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            rtf_content = f.read()
        return rtf_to_text(rtf_content).strip()
    except Exception as e:
        print(f"Error parsing .rtf {path}: {e}")
        return None

def main():
    os.makedirs(DRAFTS_DIR, exist_ok=True)
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # Files to ignore (already in wiki or duplicates)
    ignore_files = {
        "teds last night(1).doc",
        "the peanut butter underground.doc",
        "the peanut butter underground.doc.docx",
        "the peanut butter underground.docx",
        "the peanut butter underground.wps.doc",
        "the trophy tree.doc",
    }
    
    # Also ignore zone identifier files
    if not os.path.exists(SOURCE_DIR):
        print(f"Error: Source directory {SOURCE_DIR} does not exist!")
        return
        
    all_items = os.listdir(SOURCE_DIR)
    
    for filename in all_items:
        # Skip directories, zone identifiers, and files in ignore list
        if filename.endswith(":Zone.Identifier") or filename.lower() in ignore_files:
            continue
            
        src_path = os.path.join(SOURCE_DIR, filename)
        if os.path.isdir(src_path):
            continue
            
        ext = os.path.splitext(filename)[1].lower()
        if ext not in [".doc", ".docx", ".rtf"]:
            continue
            
        # Determine title from filename (removing extension and cleaning up)
        base_name = os.path.splitext(filename)[0]
        # E.g. "Pool hall" -> "Pool Hall", "Single bullet theory" -> "Single Bullet Theory"
        # We can clean up standard casings
        title = base_name.replace("_", " ").strip()
        # Capitalize words beautifully
        title = " ".join([w.capitalize() for w in title.split()])
        
        # Clean slug for filename
        slug = clean_filename(base_name)
        target_file = os.path.join(DRAFTS_DIR, f"{slug}.md")
        
        # Check if already exists in drafts
        if os.path.exists(target_file):
            print(f"Skipping (already exists): {target_file}")
            continue
            
        print(f"Processing: {filename} ({ext})")
        
        content = None
        if ext == ".doc":
            content = extract_text_doc(src_path)
        elif ext == ".docx":
            content = extract_text_docx(src_path)
        elif ext == ".rtf":
            content = extract_text_rtf(src_path)
            
        if not content:
            print(f"Error: Could not extract content from {filename}")
            continue
            
        # Get creation/modification date of the source file
        try:
            mtime = os.path.getmtime(src_path)
            created_date = datetime.datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")
        except Exception:
            created_date = "2026-05-23" # Fallback to today
            
        frontmatter = f"""---
title: "{title}"
created: {created_date}
updated: {today}
type: draft
tags: [fiction, draft]
sources: [raw/drafts/{slug}.md]
canon_status: draft
---

"""
        full_content = frontmatter + content
        
        with open(target_file, "w", encoding="utf-8") as f:
            f.write(full_content)
        print(f"Successfully ingested to: {target_file}")

    print("\nIngestion complete! Rebuilding the web wiki...")
    try:
        import sys
        # Add root directory of wiki to path
        if WIKI_DIR not in sys.path:
            sys.path.append(WIKI_DIR)
        import build_web_wiki
        build_web_wiki.build_wiki()
    except Exception as e:
        print(f"Error rebuilding the web wiki: {e}")

if __name__ == "__main__":
    main()
