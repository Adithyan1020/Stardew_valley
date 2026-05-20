from pathlib import Path
import json
import re
from collections import Counter

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CLEANED_DIR = PROJECT_ROOT / "data" / "cleaned"
CHUNKS_DIR = PROJECT_ROOT / "data" / "chunks"
OUTPUT_FILE = CHUNKS_DIR / "chunks.jsonl"

CHUNKS_DIR.mkdir(parents=True, exist_ok=True)

MAX_CHARS = 1200
OVERLAP_CHARS = 150


def normalize_whitespace(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"\xa0", " ", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def slugify(text: str) -> str:
    text = text or "untitled"
    return re.sub(r"[^a-zA-Z0-9]+", "_", text).strip("_").lower() or "untitled"


def apply_overlap(chunks, overlap_chars):
    if overlap_chars <= 0 or len(chunks) <= 1:
        return chunks

    overlapped = [chunks[0]]

    for i in range(1, len(chunks)):
        prev_chunk = chunks[i - 1]
        curr_chunk = chunks[i]

        overlap_text = prev_chunk[-overlap_chars:]
        if " " in overlap_text:
            overlap_text = overlap_text.split(" ", 1)[-1]

        merged = f"{overlap_text} {curr_chunk}".strip()
        overlapped.append(merged)

    return overlapped


def force_split(text, max_chars, overlap_chars):
    chunks = []
    start = 0
    text = text.strip()

    while start < len(text):
        end = min(start + max_chars, len(text))
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(text):
            break

        start = max(end - overlap_chars, start + 1)

    return chunks


def recursive_split(text, max_chars=MAX_CHARS, overlap_chars=OVERLAP_CHARS, separators=None, level=0):
    if separators is None:
        separators = ["\n\n", "\n", ". ", " "]

    text = normalize_whitespace(text)

    if not text:
        return []

    if len(text) <= max_chars:
        return [text]

    if level >= len(separators):
        return force_split(text, max_chars, overlap_chars)

    sep = separators[level]
    parts = text.split(sep)

    chunks = []
    current = ""

    for i, part in enumerate(parts):
        segment = part
        if i < len(parts) - 1:
            segment += sep

        if len(current) + len(segment) <= max_chars:
            current += segment
        else:
            if current.strip():
                chunks.append(current.strip())

            if len(segment) > max_chars:
                chunks.extend(
                    recursive_split(
                        segment,
                        max_chars=max_chars,
                        overlap_chars=overlap_chars,
                        separators=separators,
                        level=level + 1
                    )
                )
                current = ""
            else:
                current = segment

    if current.strip():
        chunks.append(current.strip())

    return apply_overlap(chunks, overlap_chars)


def chunk_section(doc_title, source, section_heading, content, section_num, file_stem):
    content = normalize_whitespace(content)
    if not content:
        return []

    split_chunks = recursive_split(content)

    chunk_records = []
    file_slug = slugify(file_stem)  # Use file stem instead of doc title for uniqueness
    title_slug = slugify(doc_title)
    section_slug = slugify(section_heading)
    
    # Include file name, section number, and chunk index for complete uniqueness
    unique_section_id = f"file{file_slug}_sec{section_num}_{section_slug}"

    for idx, chunk_text in enumerate(split_chunks):
        chunk_records.append({
            "id": f"{title_slug}__{unique_section_id}__chunk{idx}",
            "title": doc_title,
            "source": source,
            "section": section_heading,
            "chunk_type": "section",
            "chunk_index": idx,
            "text": chunk_text,
            "metadata": {
                "doc_title": doc_title,
                "section_path": section_heading,
                "section_num": section_num,
                "file_name": file_stem
            }
        })

    return chunk_records


def chunk_table(doc_title, source, section_heading, table_index, table_data, section_num, file_stem):
    headers = table_data.get("headers", []) or []
    rows = table_data.get("rows", []) or []

    chunk_records = []
    file_slug = slugify(file_stem)
    title_slug = slugify(doc_title)
    section_slug = slugify(section_heading)
    
    # Include file name, section number, and table index for uniqueness
    unique_section_id = f"file{file_slug}_sec{section_num}_{section_slug}"

    for row_idx, row in enumerate(rows):
        if not row:
            continue

        if headers and len(headers) == len(row):
            row_text = " | ".join(f"{h}: {v}" for h, v in zip(headers, row))
        else:
            row_text = " | ".join(str(cell) for cell in row)

        row_text = normalize_whitespace(row_text)
        if not row_text:
            continue

        chunk_records.append({
            "id": f"{title_slug}__{unique_section_id}__table{table_index}__row{row_idx}",
            "title": doc_title,
            "source": source,
            "section": section_heading,
            "chunk_type": "table_row",
            "chunk_index": row_idx,
            "text": row_text,
            "metadata": {
                "doc_title": doc_title,
                "section_path": section_heading,
                "section_num": section_num,
                "table_index": table_index,
                "headers": ", ".join(headers) if headers else "",
                "file_name": file_stem
            }
        })

    return chunk_records


def process_file(file_path: Path):
    with open(file_path, "r", encoding="utf-8") as f:
        doc = json.load(f)

    file_stem = file_path.stem  # Get the filename without extension
    title = doc.get("title", file_stem)
    source = doc.get("source", "unknown")
    sections = doc.get("sections", []) or []
    tables = doc.get("tables", []) or []

    all_chunks = []

    for section_num, section in enumerate(sections):
        heading = section.get("heading", "Untitled")
        content = section.get("content", "")
        all_chunks.extend(
            chunk_section(title, source, heading, content, section_num, file_stem)
        )

    for table_idx, table_entry in enumerate(tables):
        section_heading = table_entry.get("section", "Untitled")
        table_data = table_entry.get("table", {})

        matched_section_num = 0
        for i, sec in enumerate(sections):
            if sec.get("heading", "Untitled") == section_heading:
                matched_section_num = i
                break

        all_chunks.extend(
            chunk_table(
                title,
                source,
                section_heading,
                table_idx,
                table_data,
                matched_section_num,
                file_stem
            )
        )

    return all_chunks


def validate_unique_ids(chunks):
    ids = [chunk["id"] for chunk in chunks]
    counts = Counter(ids)
    duplicates = [chunk_id for chunk_id, count in counts.items() if count > 1]

    if duplicates:
        print(f"\n❌ Found {len(duplicates)} duplicate chunk IDs (total {len(chunks)} chunks)")
        print("\nFirst 10 duplicate IDs:")
        for dup in duplicates[:10]:
            print(f"  - {dup}")
            # Show which chunks have this ID
            matching_chunks = [chunk for chunk in chunks if chunk["id"] == dup]
            for chunk in matching_chunks[:2]:
                print(f"    File: {chunk['metadata'].get('file_name', 'unknown')}")
                print(f"    Section: {chunk.get('section', 'unknown')}")
                print(f"    Type: {chunk.get('chunk_type', 'unknown')}")
                print()
        raise ValueError(f"Found {len(duplicates)} duplicate chunk IDs. Fix ID generation before indexing.")
    else:
        print(f"\nOK: All {len(chunks)} chunks have unique IDs")


def main():
    files = sorted(CLEANED_DIR.glob("*.json"))
    print(f"Found {len(files)} cleaned files in {CLEANED_DIR}")

    all_chunks = []

    for file_path in files:
        try:
            chunks = process_file(file_path)
            all_chunks.extend(chunks)
            print(f"Chunked: {file_path.name} -> {len(chunks)} chunks")
        except Exception as e:
            print(f"Failed to chunk {file_path.name}: {e}")

    validate_unique_ids(all_chunks)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        for chunk in all_chunks:
            out.write(json.dumps(chunk, ensure_ascii=False) + "\n")

    print(f"\nSaved {len(all_chunks)} chunks to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()