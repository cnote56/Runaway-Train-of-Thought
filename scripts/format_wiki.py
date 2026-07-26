import os
from pathlib import Path

def format_files(wiki_dir):
    wiki_path = Path(wiki_dir)
    count = 0
    for txt_file in wiki_path.glob("*.txt"):
        # Rename to .md
        md_file = txt_file.with_suffix(".md")
        
        # Read content
        with open(txt_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Add minimal YAML frontmatter if missing
        if not content.startswith("---"):
            title = txt_file.stem
            new_content = f"---\ntitle: {title}\n---\n\n{content}"
        else:
            new_content = content
            
        # Write to .md
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        # Remove old .txt
        os.remove(txt_file)
        count += 1
    print(f"Processed {count} files.")

if __name__ == "__main__":
    format_files("C:/Users/Cole/creative-wiki/")
