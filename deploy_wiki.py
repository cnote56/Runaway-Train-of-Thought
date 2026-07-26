import argparse
import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime

# Resolve the directory of the creative-wiki
WIKI_DIR = Path(__file__).parent.resolve()

def run_cmd(args, cwd=None, capture_output=True):
    """Runs a system command and returns stdout and exit code."""
    try:
        shell = isinstance(args, str)
        res = subprocess.run(
            args,
            cwd=cwd,
            text=True,
            capture_output=capture_output,
            shell=shell,
        )
        stdout_str = res.stdout.strip() if res.stdout else ""
        return stdout_str, res.returncode
    except Exception as e:
        return str(e), -1

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build and deploy the creative wiki with optional Git remote setup.",
    )
    parser.add_argument(
        "--remote-url",
        help="GitHub repository URL to add as origin when no remote is configured.",
    )
    parser.add_argument(
        "--branch",
        help="Git branch to push. Defaults to current branch or main.",
    )
    parser.add_argument(
        "--no-push",
        action="store_true",
        help="Create a local commit without pushing to remote.",
    )
    parser.add_argument(
        "--commit-message",
        help="Custom commit message. Defaults to automatic deploy message.",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    print("=" * 70)
    print("           CREATIVE WIKI ONE-CLICK DEPLOYER")
    print("=" * 70)

    # Step 1: Recompile the wiki HTML
    print("\n[Step 1/3] Compiling modern interactive index.html...")
    build_script = WIKI_DIR / "build_web_wiki.py"
    if not build_script.exists():
        print(f"ERROR: build_web_wiki.py not found at {build_script}!")
        sys.exit(1)
        
    out, code = run_cmd([sys.executable, str(build_script)], cwd=WIKI_DIR, capture_output=False)
    if code != 0:
        print("ERROR: Failed to compile the web wiki!")
        sys.exit(1)
    
    # Step 2: Initialize Git if not present
    print("\n[Step 2/3] Checking Git Repository status...")
    git_dir = WIKI_DIR / ".git"
    if not git_dir.exists():
        print("No Git repository found in 'creative-wiki/'. Initializing a new one...")
        out, code = run_cmd("git init", cwd=WIKI_DIR)
        if code == 0:
            print("Successfully initialized a local Git repository in 'creative-wiki/'.")
            # Create a simple .gitignore if it doesn't exist
            gitignore = WIKI_DIR / ".gitignore"
            if not gitignore.exists():
                with open(gitignore, "w", encoding="utf-8") as f:
                    f.write("# Ignore heavy Obsidian caches or operating system files\n")
                    f.write(".obsidian/workspace.json\n")
                    f.write(".obsidian/workspace-mobile.json\n")
                    f.write(".obsidian/cache/\n")
                    f.write("__pycache__/\n")
                    f.write("*.pyc\n")
                    f.write(".DS_Store\n")
                print("Created a default .gitignore file.")
        else:
            print(f"ERROR: Failed to initialize git: {out}")
            sys.exit(1)

    # Check branch name or create 'main'
    out, code = run_cmd("git branch --show-current", cwd=WIKI_DIR)
    current_branch = args.branch or (out if (code == 0 and out) else "main")
    if not out and code == 0:
        # No commits yet, let's make sure it defaults to main
        run_cmd("git checkout -b main", cwd=WIKI_DIR)
        current_branch = args.branch or "main"

    # Step 3: Check Remote Origin
    remote_url = args.remote_url
    origin_url, origin_code = run_cmd("git remote get-url origin", cwd=WIKI_DIR)
    has_remote = origin_code == 0 and bool(origin_url)

    if not has_remote and remote_url:
        print(f"Adding remote origin from --remote-url: {remote_url}")
        out, code = run_cmd(f"git remote add origin {remote_url}", cwd=WIKI_DIR)
        if code != 0:
            print(f"ERROR: Failed to add remote origin: {out}")
            sys.exit(1)
        has_remote = True

    if not has_remote:
        print("\n" + "!" * 70)
        print(" ACTION REQUIRED: No remote GitHub repository linked yet!")
        print("!" * 70)
        print("Before you can deploy, you need to:")
        print("  1. Go to https://github.com/new")
        print("  2. Create a new repository (e.g., 'creative-wiki')")
        print("     - Do NOT initialize it with README, .gitignore, or license.")
        print("  3. Add your remote origin, or rerun this script with:")
        print("     python deploy_wiki.py --remote-url <your-github-repo-url>")
        print("!" * 70 + "\n")
        
        # Stage and commit locally.
        print("Staging and committing your files locally first...")
        run_cmd("git add .", cwd=WIKI_DIR)
        run_cmd('git commit -m "Initial commit of compiled story bible"', cwd=WIKI_DIR)
        print("Committed files locally. Please add a remote origin to push!")
        sys.exit(0)

    if args.no_push:
        print("\n[Step 3/3] Staging and committing locally without pushing...")
        run_cmd("git add .", cwd=WIKI_DIR)
        status_out, _ = run_cmd("git status --porcelain", cwd=WIKI_DIR)
        if not status_out:
            print("No new changes detected. Wiki is already up to date locally.")
            sys.exit(0)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        commit_msg = args.commit_message or f"Local deploy: Update story wiki ({timestamp})"
        print(f"Committing changes: '{commit_msg}'")
        run_cmd(f'git commit -m "{commit_msg}"', cwd=WIKI_DIR)
        print("Local commit complete. Remote push skipped by --no-push.")
        sys.exit(0)

    # Step 4: Stage, Commit, and Push
    print("\n[Step 3/3] Staging, committing, and deploying to GitHub...")
    
    # Stage everything
    run_cmd("git add .", cwd=WIKI_DIR)
    
    # Check if there are changes to commit
    status_out, _ = run_cmd("git status --porcelain", cwd=WIKI_DIR)
    if not status_out:
        print("No new changes detected. Wiki is already up to date on GitHub!")
        sys.exit(0)
        
    # Commit
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    commit_msg = f"Auto-deploy: Update story wiki ({timestamp})"
    print(f"Committing changes: '{commit_msg}'")
    run_cmd(f'git commit -m "{commit_msg}"', cwd=WIKI_DIR)
    
    # Push
    print(f"Pushing to GitHub remote branch '{current_branch}'...")
    push_out, push_code = run_cmd(f"git push origin {current_branch}", cwd=WIKI_DIR)
    
    if push_code == 0:
        print("\n" + "=" * 70)
        print(" 🎉 SUCCESS: Your creative wiki has been updated and pushed to GitHub!")
        print("=" * 70)
        print("If GitHub Pages is enabled on your repository, your updates will be live in a minute!")
    else:
        # If it failed, check if we need to set upstream
        if "no upstream branch" in push_out.lower() or "has no upstream branch" in push_out.lower():
            print(f"Setting upstream tracking for '{current_branch}'...")
            run_cmd(f"git push --set-upstream origin {current_branch}", cwd=WIKI_DIR, capture_output=False)
        else:
            print(f"ERROR: Failed to push to GitHub! Details:\n{push_out}")
            sys.exit(1)

if __name__ == "__main__":
    main()
