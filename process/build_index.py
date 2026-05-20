from pathlib import Path
import json
import chromadb
from sentence_transformers import SentenceTransformer

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CHUNKS_FILE = PROJECT_ROOT / "data" / "chunks" / "chunks.jsonl"
CHROMA_DIR = PROJECT_ROOT / "data" / "chroma"

COLLECTION_NAME = "stardew_chunks_bge"
EMBED_MODEL = "BAAI/bge-small-en-v1.5"
BATCH_SIZE = 64


def load_chunks(path):
    records = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def batched(seq, size):
    for i in range(0, len(seq), size):
        yield seq[i:i + size]


def main():
    chunks = load_chunks(CHUNKS_FILE)
    print(f"Loaded {len(chunks)} chunks")

    model = SentenceTransformer(EMBED_MODEL)
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))

    collection = client.get_or_create_collection(name=COLLECTION_NAME)

    ids = [c["id"] for c in chunks]
    documents = [c["text"] for c in chunks]
    metadatas = []

    for c in chunks:
        meta = {
            "title": c.get("title", ""),
            "source": c.get("source", ""),
            "section": c.get("section", ""),
            "chunk_type": c.get("chunk_type", ""),
            "chunk_index": c.get("chunk_index", 0),
        }

        extra_meta = c.get("metadata", {})
        for k, v in extra_meta.items():
            if isinstance(v, (str, int, float, bool)):
                meta[k] = v
            elif isinstance(v, list):
                meta[k] = ", ".join(str(x) for x in v)

        metadatas.append(meta)

    for batch_num, batch in enumerate(batched(list(zip(ids, documents, metadatas)), BATCH_SIZE), start=1):
        batch_ids = [x[0] for x in batch]
        batch_docs = [x[1] for x in batch]
        batch_meta = [x[2] for x in batch]

        embeddings = model.encode(batch_docs, normalize_embeddings=True).tolist()

        collection.add(
            ids=batch_ids,
            documents=batch_docs,
            metadatas=batch_meta,
            embeddings=embeddings
        )

        print(f"Indexed batch {batch_num}: {len(batch_ids)} chunks")

    print(f"Done. Collection '{COLLECTION_NAME}' stored in {CHROMA_DIR}")


if __name__ == "__main__":
    main()