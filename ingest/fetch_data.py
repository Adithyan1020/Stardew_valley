import json
import os
import re
import time
import requests

API_URL = "https://stardewvalleywiki.com/mediawiki/api.php"
OUTPUT_DIR = "data/error_raw"
SEEDS_FILE = "error_seed.json"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def slugify(text):
    return re.sub(r'[^a-zA-Z0-9]+', '_', text).strip('_').lower()

def load_titles():
    with open(SEEDS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    titles = []
    for page in data.get("pages", []):
        titles.append(page["title"])
    return titles

def fetch_page(title):
    params = {
        "action": "parse",
        "page": title,
        "prop": "text|wikitext",
        "format": "json",
        "formatversion": 2
    }

    r = requests.get(API_URL, params=params, timeout=30)
    r.raise_for_status()
    return r.json()

def save_page(title, data):
    filename = os.path.join(OUTPUT_DIR, f"{slugify(title)}.json")
    with open(filename, "w", encoding="utf-8") as f:
        json.dump({
            "title": title,
            "source": "stardewvalleywiki",
            "data": data
        }, f, ensure_ascii=False, indent=2)

def main():
    titles = load_titles()
    print(f"Found {len(titles)} pages")

    for i, title in enumerate(titles, 1):
        try:
            print(f"[{i}/{len(titles)}] Fetching: {title}")
            data = fetch_page(title)
            save_page(title, data)
            time.sleep(1)
        except Exception as e:
            print(f"Failed: {title} -> {e}")

if __name__ == "__main__":
    main()