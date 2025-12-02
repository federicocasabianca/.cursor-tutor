import zipfile
import json
from collections import Counter, defaultdict
from pathlib import Path
import re


# Resolve project root as the directory above this script (../)
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# ---------- CONFIG ----------
TAXONOMY_DIR = PROJECT_ROOT / "data" / "taxonomy"
ZIP_FILES = sorted(TAXONOMY_DIR.glob("*.zip"))  # All ZIP files in taxonomy dir
TOP_N = 10
OUTPUT_MD = PROJECT_ROOT / "docs" / "query_length_buckets.md"
NATURAL_COMPLEX_PATH = PROJECT_ROOT / "docs" / "Natural_Complex_Queries.txt"
NATURAL_4PLUS_EXAMPLES = 4  # number of natural-language examples to show for 4+ bucket
# ----------------------------


# Grade level phrases that should be treated as a single semantic term
# (mirrors the patterns used in other scripts, focusing on multi-token variants)
GRADE_LEVEL_PHRASES = [
    # Single grades
    "klasse 1",
    "klasse 2",
    "klasse 3",
    "klasse 4",
    "klasse 5",
    "klasse 6",
    "klasse 7",
    "klasse 8",
    "klasse 9",
    "klasse 10",
    "klasse 11",
    "klasse 12",
    # Special levels
    "vorschule",
    "kita",
    # Abbreviations with dot and space
    "kl. 1",
    "kl. 2",
    "kl. 3",
    "kl. 4",
    "kl. 5",
    "kl. 6",
    "kl. 7",
    "kl. 8",
    "kl. 9",
    "kl. 10",
    "kl. 11",
    "kl. 12",
    # Abbreviations with space
    "kl 1",
    "kl 2",
    "kl 3",
    "kl 4",
    "kl 5",
    "kl 6",
    "kl 7",
    "kl 8",
    "kl 9",
    "kl 10",
    "kl 11",
    "kl 12",
    # Common ranges
    "klasse 1-2",
    "klasse 1-3",
    "klasse 1-4",
    "klasse 1-6",
    "klasse 2-3",
    "klasse 2-4",
    "klasse 3-4",
    "klasse 3-6",
    "klasse 4-5",
    "klasse 5-6",
    "klasse 5-7",
    "klasse 7-10",
    "klasse 1 - 4",
]

# Connector tokens that should NOT count as query terms
CONNECTOR_TOKENS = {"and", "wer", "mit"}


def get_bucket_name(query: str) -> str | None:
    """
    Assign a query to a bucket based on number of *semantic* terms.

    Considerations:
    - Grade level phrases like "klasse 1" (and variants) are treated as ONE term.
    - Connector tokens such as "and", "wer", "mit" are NOT counted as terms.

    Buckets:
    - "1_word": exactly 1 term
    - "2_words": exactly 2 terms
    - "3_words": exactly 3 terms
    - "4_plus": 4 or more terms
    """
    if not query:
        return None

    # Normalize
    q = str(query).lower().strip()

    # Collapse grade-level phrases to a single token (replace internal spaces with underscores)
    for phrase in GRADE_LEVEL_PHRASES:
        pattern = r"\b" + re.escape(phrase) + r"\b"
        replacement = phrase.replace(" ", "_")
        q = re.sub(pattern, replacement, q)

    # Tokenize
    tokens = [t for t in q.split() if t]

    # Remove connector tokens from the count
    semantic_tokens = [t for t in tokens if t not in CONNECTOR_TOKENS]
    n = len(semantic_tokens)

    if n == 1:
        return "1_word"
    if n == 2:
        return "2_words"
    if n == 3:
        return "3_words"
    if n >= 4:
        return "4_plus"
    return None


def load_natural_4plus_examples(path: Path, max_examples: int = NATURAL_4PLUS_EXAMPLES) -> list[str]:
    """
    Load a few example natural-language queries for the 4+ bucket
    from the Natural_Complex_Queries.txt report.

    We look for lines shaped like:
      '   1. query text here (complexity: 9, freq: 146)'
      '   1. query text here (natural: 9, freq: 146)'

    and keep the query text before the first '('.
    Only include queries that fall into the '4_plus' bucket by our
    current semantic token logic.
    """
    examples: list[str] = []

    if not path.exists():
        return examples

    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return examples

    for line in text.splitlines():
        line = line.rstrip()
        # Match numbered entries like "   1. some query (complexity: ...)"
        m = re.match(r"^\s*\d+\.\s+(.*)$", line)
        if not m:
            continue

        candidate = m.group(1)
        # Strip trailing metadata like "(complexity: ...", "(natural: ...", etc.
        if "(" in candidate:
            candidate = candidate.split("(", 1)[0].rstrip()

        if not candidate:
            continue

        if get_bucket_name(candidate) != "4_plus":
            continue

        if candidate not in examples:
            examples.append(candidate)

        if len(examples) >= max_examples:
            break

    return examples


def stream_queries_from_zip(zip_path: Path):
    """
    Yield (query, frequency) pairs from all JSON files inside a ZIP.

    Assumes each JSON file is line-delimited JSON objects with at least:
      - "query": str
      - "frequency": int
    (mirrors the pattern used in existing scripts in this project).
    """
    with zipfile.ZipFile(zip_path, "r") as z:
        for file_name in z.namelist():
            if not file_name.endswith(".json"):
                continue
            with z.open(file_name) as f:
                for raw_line in f:
                    try:
                        line = raw_line.decode("utf-8", errors="ignore").strip().rstrip(",")
                    except Exception:
                        continue

                    if not line or not line.startswith("{"):
                        continue

                    try:
                        obj = json.loads(line)
                    except Exception:
                        continue

                    query = obj.get("query", "")
                    # Default to 0 if missing; skip non-positive frequencies
                    try:
                        freq = int(obj.get("frequency", 0))
                    except Exception:
                        freq = 0

                    if not query or freq <= 0:
                        continue

                    yield query, freq


def main():
    if not ZIP_FILES:
        print(f"No ZIP files found in {TAXONOMY_DIR}")
        return

    # Buckets: bucket_name -> Counter({query: total_frequency})
    buckets: dict[str, Counter] = defaultdict(Counter)
    total_queries = 0

    print("=" * 80)
    print(f"Processing {len(ZIP_FILES)} ZIP files from: {TAXONOMY_DIR}")
    print("=" * 80)

    for zip_path in ZIP_FILES:
        print(f"  - {zip_path.name}")
        for query, freq in stream_queries_from_zip(zip_path):
            bucket = get_bucket_name(query)
            if bucket is None:
                continue
            buckets[bucket][query] += freq
            total_queries += freq

    print("\nFinished aggregation.")
    print(f"Total query frequency counted across all buckets: {total_queries:,}")

    # Prepare Markdown output
    bucket_labels = {
        "1_word": "1-word queries",
        "2_words": "2-word queries",
        "3_words": "3-word queries",
        "4_plus": "4+ word queries",
    }

    lines: list[str] = []
    lines.append("# Query Length Buckets\n")
    lines.append(f"Source directory: `{TAXONOMY_DIR}`")
    lines.append(f"Number of ZIP files processed: {len(ZIP_FILES)}")
    lines.append(f"Total query frequency aggregated: {total_queries:,}")
    lines.append("")

    # Pre-load natural language examples for the 4+ bucket (if available)
    natural_4plus_examples = load_natural_4plus_examples(NATURAL_COMPLEX_PATH, NATURAL_4PLUS_EXAMPLES)

    for bucket_key in ["1_word", "2_words", "3_words", "4_plus"]:
        label = bucket_labels[bucket_key]
        counter = buckets.get(bucket_key, Counter())
        total_bucket_freq = sum(counter.values())
        unique_queries = len(counter)

        lines.append(f"## {label}")
        lines.append(f"- Total frequency: **{total_bucket_freq:,}**")
        lines.append(f"- Unique queries: **{unique_queries:,}**")
        lines.append("")

        # For the 4+ bucket, show a few handpicked natural-language examples on top
        if bucket_key == "4_plus" and natural_4plus_examples:
            lines.append("**Example natural-language queries in this bucket:**")
            for q in natural_4plus_examples:
                safe_q = str(q).replace("|", "\\|")
                lines.append(f"- {safe_q}")
            lines.append("")

        if not counter:
            lines.append("_No queries found for this bucket._")
            lines.append("")
            continue

        lines.append("| Rank | Query | Frequency |")
        lines.append("| ---- | ----- | --------- |")

        for rank, (query, freq) in enumerate(counter.most_common(TOP_N), start=1):
            # Escape pipe characters to keep Markdown table valid
            safe_query = str(query).replace("|", "\\|")
            lines.append(f"| {rank} | {safe_query} | {freq:,} |")

        lines.append("")  # blank line after each table

    OUTPUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("=" * 80)
    print(f"Top {TOP_N} most frequent queries per length bucket written to:")
    print(f"  {OUTPUT_MD}")
    print("=" * 80)


if __name__ == "__main__":
    main()


