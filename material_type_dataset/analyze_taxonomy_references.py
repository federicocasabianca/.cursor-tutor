#!/usr/bin/env python3
"""
Analyze query data stored inside JSON lines compressed in ZIP archives and
determine what percentage of queries reference titles defined in the taxonomy
CSV files (`taxonomy_grade_levels.csv` and `taxonomy_schooltypes.csv`).

Usage:
    python analyze_taxonomy_references.py \
        --taxonomy-dir /path/to/taxonomy \
        --zip-dir /path/to/zips

Both arguments default to the taxonomy directory that sits next to this
script, so you can typically just run:

    python analyze_taxonomy_references.py

The script reports the percentage of matching queries per archive, overall
percentage across all records, and the percentage across unique queries.
"""

from __future__ import annotations

import argparse
import csv
import json
import unicodedata
import zipfile
from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Set, Tuple


TAXONOMY_FILES = (
    "taxonomy_grade_levels.csv",
    "taxonomy_schooltypes.csv",
)

CATEGORIES = ("grade_levels", "schooltypes")
CATEGORY_LABELS = {
    "grade_levels": "Grade level matches",
    "schooltypes": "Schooltype matches",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Compute the percentage of queries that reference taxonomy titles "
            "across all JSON lines contained in ZIP archives."
        )
    )
    default_taxonomy_dir = Path(__file__).resolve().parent / "taxonomy"
    parser.add_argument(
        "--taxonomy-dir",
        type=Path,
        default=default_taxonomy_dir,
        help="Directory containing the taxonomy CSV files.",
    )
    parser.add_argument(
        "--zip-dir",
        type=Path,
        default=default_taxonomy_dir,
        help="Directory containing the ZIP files with query JSON data.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Optional limit on the number of query records to process.",
    )
    return parser.parse_args()


def normalize_text(value: str) -> str:
    """
    Normalize text for consistent comparisons:
    - Unicode normalize to NFKD and strip diacritics
    - Casefold for case-insensitive comparisons
    - Replace non-alphanumeric characters with spaces
    - Collapse consecutive whitespace
    """
    value = unicodedata.normalize("NFKD", value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = value.casefold()

    normalized_chars: List[str] = []
    for ch in value:
        if ch.isalnum():
            normalized_chars.append(ch)
        else:
            normalized_chars.append(" ")

    normalized = "".join(normalized_chars).strip()
    return " ".join(normalized.split())


def load_taxonomy_titles(taxonomy_dir: Path) -> List[Tuple[str, str]]:
    titles: List[Tuple[str, str]] = []
    category_map = {
        "taxonomy_grade_levels.csv": "grade_levels",
        "taxonomy_schooltypes.csv": "schooltypes",
    }
    for filename in TAXONOMY_FILES:
        csv_path = taxonomy_dir / filename
        if not csv_path.exists():
            raise FileNotFoundError(f"Expected taxonomy file not found: {csv_path}")
        category = category_map.get(filename)
        with csv_path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            if "title" not in reader.fieldnames:
                raise ValueError(f"CSV file {csv_path} lacks a 'title' column.")
            for row in reader:
                title = row.get("title", "").strip()
                if title:
                    titles.append((title, category))
    return titles


def build_title_token_map(
    titles: Iterable[Tuple[str, str]]
) -> Dict[str, List[Tuple[Tuple[str, ...], str]]]:
    """
    Organize taxonomy titles for efficient matching.

    Returns a mapping from the first normalized token to a list of tuples
    containing the remaining token sequence and the originating taxonomy
    category.
    """
    token_map: Dict[str, List[Tuple[Tuple[str, ...], str]]] = defaultdict(list)
    seen: Set[Tuple[Tuple[str, ...], str]] = set()

    for title, category in titles:
        normalized = normalize_text(title)
        if not normalized:
            continue
        tokens = tuple(normalized.split())
        if not tokens:
            continue
        key = (tokens, category)
        if key in seen:
            continue
        seen.add(key)
        token_map[tokens[0]].append((tokens, category))

    # Sort token lists once for deterministic iteration order (longer first).
    for first_token in token_map:
        token_map[first_token].sort(key=lambda item: len(item[0]), reverse=True)

    return token_map


def query_references_taxonomy(
    tokens: Sequence[str], title_map: Dict[str, List[Tuple[Tuple[str, ...], str]]]
) -> Set[str]:
    matches: Set[str] = set()
    if not tokens:
        return matches
    for index, token in enumerate(tokens):
        candidates = title_map.get(token)
        if not candidates:
            continue
        for candidate_tokens, category in candidates:
            length = len(candidate_tokens)
            if index + length > len(tokens):
                continue
            if tuple(tokens[index : index + length]) == candidate_tokens:
                matches.add(category)
    return matches


def _iter_json_lines_with_merging(text: str, source: str) -> Iterable[dict]:
    """
    Parse JSON lines content while tolerating records that span multiple physical
    lines (e.g., because the raw data contains literal newline characters within
    quoted strings). Newlines encountered inside strings are effectively
    collapsed into spaces.
    """

    buffer = ""
    for raw_line in text.split("\n"):
        piece = raw_line.strip()
        if not piece and not buffer:
            continue
        if buffer:
            buffer = f"{buffer} {piece}".strip()
        else:
            buffer = piece
        if not buffer:
            continue
        try:
            record = json.loads(buffer)
        except json.JSONDecodeError:
            continue
        if isinstance(record, dict):
            yield record
        buffer = ""

    if buffer.strip():
        try:
            record = json.loads(buffer)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON content in {source}: {exc}") from exc
        if isinstance(record, dict):
            yield record


def iter_zip_json_records(zip_path: Path) -> Iterable[dict]:
    with zipfile.ZipFile(zip_path) as archive:
        json_members = [name for name in archive.namelist() if name.lower().endswith(".json")]
        if not json_members:
            return
        for member in json_members:
            name_only = Path(member).name
            if member.startswith("__MACOSX/") or name_only.startswith("._"):
                continue
            with archive.open(member) as handle:
                raw_bytes = handle.read()
            try:
                text = raw_bytes.decode("utf-8")
            except UnicodeDecodeError:
                text = raw_bytes.decode("utf-8", errors="replace")
            text = text.replace("\r\n", "\n").replace("\r", "\n").strip()
            if not text:
                continue

            if text.lstrip().startswith("["):
                try:
                    data = json.loads(text)
                except json.JSONDecodeError as exc:
                    sanitized = text.replace("\n", " ")
                    try:
                        data = json.loads(sanitized)
                    except json.JSONDecodeError as exc2:
                        raise ValueError(f"Invalid JSON array in {zip_path}::{member}: {exc2}") from exc2

                if isinstance(data, dict):
                    data = data.get("data", [])

                if isinstance(data, list):
                    for record in data:
                        if isinstance(record, dict):
                            yield record
                    continue

                raise ValueError(
                    f"Unexpected JSON structure in {zip_path}::{member}: expected list, got {type(data).__name__}"
                )

            source = f"{zip_path}::{member}"
            for record in _iter_json_lines_with_merging(text, source):
                yield record


def analyze_queries(
    zip_dir: Path,
    title_map: Dict[str, List[Tuple[Tuple[str, ...], str]]],
    limit: int | None = None,
) -> Tuple[
    List[Tuple[Path, int, int, Dict[str, int]]],
    int,
    int,
    Dict[str, int],
    int,
    int,
    Dict[str, int],
]:
    per_archive_stats: List[Tuple[Path, int, int, Dict[str, int]]] = []
    overall_total = 0
    overall_matches = 0
    overall_category_matches = {category: 0 for category in CATEGORIES}
    unique_queries: Dict[str, Set[str]] = {}

    processed_records = 0

    for zip_path in sorted(zip_dir.glob("*.zip")):
        archive_total = 0
        archive_matches = 0
        archive_category_matches = {category: 0 for category in CATEGORIES}

        for record in iter_zip_json_records(zip_path):
            query = record.get("query")
            if not isinstance(query, str):
                continue

            archive_total += 1
            overall_total += 1

            normalized_query = normalize_text(query)
            tokens = normalized_query.split()

            categories = query_references_taxonomy(tokens, title_map)
            match = bool(categories)
            if match:
                archive_matches += 1
                overall_matches += 1
                for category in categories:
                    archive_category_matches[category] += 1
                    overall_category_matches[category] += 1

            if query not in unique_queries:
                unique_queries[query] = set(categories)
            else:
                unique_queries[query].update(categories)

            processed_records += 1
            if limit is not None and processed_records >= limit:
                break

        per_archive_stats.append(
            (zip_path, archive_total, archive_matches, dict(archive_category_matches))
        )

        if limit is not None and processed_records >= limit:
            break

    unique_total = len(unique_queries)
    unique_matches = sum(1 for matched in unique_queries.values() if matched)
    unique_category_matches = {category: 0 for category in CATEGORIES}
    for categories in unique_queries.values():
        for category in categories:
            unique_category_matches[category] += 1

    return (
        per_archive_stats,
        overall_total,
        overall_matches,
        overall_category_matches,
        unique_total,
        unique_matches,
        unique_category_matches,
    )


def percentage(part: int, whole: int) -> float:
    if whole == 0:
        return 0.0
    return (part / whole) * 100


def main() -> None:
    args = parse_args()
    taxonomy_dir = args.taxonomy_dir
    zip_dir = args.zip_dir

    titles = load_taxonomy_titles(taxonomy_dir)
    title_map = build_title_token_map(titles)

    (
        per_archive_stats,
        overall_total,
        overall_matches,
        overall_category_matches,
        unique_total,
        unique_matches,
        unique_category_matches,
    ) = analyze_queries(zip_dir, title_map, limit=args.limit)

    print("Per-archive results:")
    for zip_path, total, matches, category_counts in per_archive_stats:
        pct = percentage(matches, total)
        print(f"  {zip_path.name}: {matches}/{total} queries reference taxonomy ({pct:.2f}%)")
        for category in CATEGORIES:
            count = category_counts[category]
            cat_pct = percentage(count, total)
            print(f"    {CATEGORY_LABELS[category]}: {count} ({cat_pct:.2f}%)")

    print("\nOverall results:")
    overall_pct = percentage(overall_matches, overall_total)
    print(f"  Total records: {overall_total}")
    print(f"  Matches: {overall_matches}")
    print(f"  Percentage: {overall_pct:.2f}%")
    for category in CATEGORIES:
        count = overall_category_matches[category]
        cat_pct = percentage(count, overall_total)
        print(f"  {CATEGORY_LABELS[category]}: {count} ({cat_pct:.2f}%)")

    print("\nUnique query results:")
    unique_pct = percentage(unique_matches, unique_total)
    print(f"  Unique queries: {unique_total}")
    print(f"  Unique matches: {unique_matches}")
    print(f"  Percentage: {unique_pct:.2f}%")
    for category in CATEGORIES:
        count = unique_category_matches[category]
        cat_pct = percentage(count, unique_total)
        print(f"  {CATEGORY_LABELS[category]}: {count} ({cat_pct:.2f}%)")


if __name__ == "__main__":
    main()

