from pathlib import Path
from bs4 import BeautifulSoup
import json
import re

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
CLEANED_DIR = PROJECT_ROOT / "data" / "cleaned"

CLEANED_DIR.mkdir(parents=True, exist_ok=True)

REMOVE_TAGS = {"script", "style", "noscript", "sup"}

SKIP_CLASSES = {
    "mw-editsection",
    "reference",
    "reflist",
    "navbox",
    "vertical-navbox",
    "toc",
    "thumbcaption",
    "haudio",
    "mw-jump-link"
}


def normalize_whitespace(text: str) -> str:
    text = re.sub(r"\xa0", " ", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def clean_text(text: str) -> str:
    return normalize_whitespace(text.strip())


def remove_noise(soup: BeautifulSoup):
    for tag in soup.find_all(list(REMOVE_TAGS)):
        tag.decompose()

    for cls in SKIP_CLASSES:
        for tag in soup.select(f".{cls}"):
            tag.decompose()


def extract_table(table):
    headers = []
    rows = []

    first_row = table.find("tr")
    if first_row:
        ths = first_row.find_all("th")
        if ths:
            headers = [clean_text(th.get_text(" ", strip=True)) for th in ths]

    for tr in table.find_all("tr"):
        cells = tr.find_all(["td", "th"])
        row = [clean_text(cell.get_text(", ", strip=True)) for cell in cells]
        if row:
            rows.append(row)

    return {
        "headers": headers,
        "rows": rows
    }


def extract_content(soup: BeautifulSoup):
    sections = []
    tables = []

    current_heading = "Introduction"
    current_lines = []

    main_content = soup.find("div", class_="mw-parser-output")
    if not main_content:
        main_content = soup

    for elem in main_content.find_all(recursive=False):
        if getattr(elem, "name", None) is None:
            continue

        if elem.name in ["h1", "h2", "h3", "h4"]:
            if current_lines:
                section_text = "\n".join(current_lines).strip()
                if section_text:
                    sections.append({
                        "heading": current_heading,
                        "content": section_text
                    })
                current_lines = []

            current_heading = clean_text(elem.get_text(" ", strip=True))

        elif elem.name == "p":
            text = clean_text(elem.get_text(" ", strip=True))
            if text:
                current_lines.append(text)

        elif elem.name in ["ul", "ol"]:
            for li in elem.find_all("li", recursive=False):
                text = clean_text(li.get_text(" ", strip=True))
                if text:
                    current_lines.append(f"- {text}")

        elif elem.name == "table":
            table_data = extract_table(elem)
            if table_data["rows"]:
                tables.append({
                    "section": current_heading,
                    "table": table_data
                })

        elif elem.name == "div":
            tables_in_div = elem.find_all("table")
            if tables_in_div:
                for table in tables_in_div:
                    table_data = extract_table(table)
                    if table_data["rows"]:
                        tables.append({
                            "section": current_heading,
                            "table": table_data
                        })
            else:
                text = clean_text(elem.get_text(" ", strip=True))
                if text and len(text.split()) > 8:
                    current_lines.append(text)

    if current_lines:
        section_text = "\n".join(current_lines).strip()
        if section_text:
            sections.append({
                "heading": current_heading,
                "content": section_text
            })

    return {
        "sections": sections,
        "tables": tables
    }


def extract_html(raw_data: dict):
    data = raw_data.get("data", {})
    parse = data.get("parse", {})

    html = parse.get("text")
    if isinstance(html, dict):
        html = html.get("*")

    return html


def process_file(file_path: Path):
    with open(file_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    title = raw_data.get("title", file_path.stem)
    source = raw_data.get("source", "unknown")

    html = extract_html(raw_data)
    if not html:
        print(f"Skipping {file_path.name}: no HTML content found")
        return

    soup = BeautifulSoup(html, "html.parser")
    remove_noise(soup)
    extracted = extract_content(soup)

    cleaned = {
        "title": title,
        "source": source,
        "sections": extracted["sections"],
        "tables": extracted["tables"]
    }

    output_file = CLEANED_DIR / file_path.name
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(cleaned, f, ensure_ascii=False, indent=2)

    print(f"Cleaned: {file_path.name}")


def main():
    files = sorted(RAW_DIR.glob("*.json"))
    print(f"Found {len(files)} raw files in {RAW_DIR}")

    for file_path in files:
        try:
            process_file(file_path)
        except Exception as e:
            print(f"Failed to clean {file_path.name}: {e}")


if __name__ == "__main__":
    main()