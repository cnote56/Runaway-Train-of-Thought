#!/usr/bin/env python3
"""Find and remove duplicate files by content hash."""

from __future__ import annotations

import argparse
import hashlib
import logging
import sys
from pathlib import Path


def setup_logger(log_file: Path) -> logging.Logger:
    logger = logging.getLogger("remove_duplicates")
    logger.setLevel(logging.INFO)
    if logger.handlers:
        logger.handlers.clear()

    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s", "%Y-%m-%d %H:%M:%S")

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    logger.propagate = False
    return logger


def compute_file_hash(file_path: Path, chunk_size: int = 8192) -> str:
    """Return the SHA-256 hash of a file."""
    hash_obj = hashlib.sha256()
    with file_path.open("rb") as file_obj:
        for chunk in iter(lambda: file_obj.read(chunk_size), b""):
            hash_obj.update(chunk)
    return hash_obj.hexdigest()


def find_duplicates(directory: Path, logger: logging.Logger) -> dict[str, list[Path]]:
    """Scan a directory recursively and group files by hash."""
    if not directory.exists():
        raise FileNotFoundError(f"Directory does not exist: {directory}")
    if not directory.is_dir():
        raise NotADirectoryError(f"Not a directory: {directory}")

    files_by_hash: dict[str, list[Path]] = {}
    logger.info("Scanning directory %s", directory)

    for file_path in directory.rglob("*"):
        if not file_path.is_file():
            continue

        try:
            hash_value = compute_file_hash(file_path)
            files_by_hash.setdefault(hash_value, []).append(file_path)
        except Exception as exc:
            logger.warning("Could not hash %s: %s", file_path, exc)

    duplicates = {hash_value: paths for hash_value, paths in files_by_hash.items() if len(paths) > 1}
    logger.info("Found %d duplicate groups", len(duplicates))
    return duplicates


def remove_duplicates(duplicates: dict[str, list[Path]], delete: bool, logger: logging.Logger) -> None:
    """Print duplicate groups and optionally delete all but one copy."""
    if not duplicates:
        logger.info("No duplicate files found.")
        return

    for hash_value, paths in duplicates.items():
        logger.info("Duplicate group (SHA-256=%s):", hash_value)
        for index, path in enumerate(paths, start=1):
            prefix = "KEEP" if index == 1 else "DELETE"
            logger.info("  %s: %s", prefix, path)

        if delete:
            for duplicate_path in paths[1:]:
                try:
                    duplicate_path.unlink()
                    logger.info("Deleted %s", duplicate_path)
                except Exception as exc:
                    logger.error("Failed to delete %s: %s", duplicate_path, exc)


def confirm_deletion() -> bool:
    """Ask the user to confirm destructive deletion."""
    try:
        answer = input("Delete duplicate files? Type yes to confirm: ").strip().lower()
    except EOFError:
        return False
    return answer in {"yes", "y"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Find duplicate files by content hash and optionally delete duplicates.",
    )
    parser.add_argument(
        "directory",
        type=Path,
        nargs="?",
        default=Path.cwd(),
        help="Directory to scan for duplicates (default: current working directory).",
    )
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--delete",
        action="store_true",
        help="Delete duplicate files, keeping the first instance from each group.",
    )
    mode_group.add_argument(
        "--dry-run",
        action="store_true",
        help="Print duplicate groups without deleting files (default behavior).",
    )
    parser.add_argument(
        "--log-file",
        type=Path,
        default=None,
        help="Path to append log entries for this run (default: remove_duplicates.log in current working directory).",
    )
    parser.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="Confirm deletion without prompting when --delete is used.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    log_file = args.log_file or Path.cwd() / "remove_duplicates.log"
    logger = setup_logger(log_file)
    logger.info("Using log file %s", log_file)

    duplicates = find_duplicates(args.directory, logger)

    if args.delete:
        if args.yes or confirm_deletion():
            logger.info("Starting deletion of duplicate files")
            remove_duplicates(duplicates, delete=True, logger=logger)
        else:
            logger.info("Deletion canceled by user")
            logger.info("Duplicate groups are listed below")
            remove_duplicates(duplicates, delete=False, logger=logger)
    else:
        logger.info("Running in dry-run mode")
        remove_duplicates(duplicates, delete=False, logger=logger)

    logger.info("Run complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
