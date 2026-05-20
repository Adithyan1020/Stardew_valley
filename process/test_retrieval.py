from pathlib import Path
import chromadb
from sentence_transformers import SentenceTransformer

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CHROMA_DIR = PROJECT_ROOT / "data" / "chroma"

COLLECTION_NAME = "stardew_chunks_bge"
EMBED_MODEL = "BAAI/bge-small-en-v1.5"


def main():
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    collection = client.get_collection(COLLECTION_NAME)

    model = SentenceTransformer(EMBED_MODEL)

    while True:
        query = input("\nAsk something (or 'exit'): ").strip()
        if query.lower() == "exit":
            break

        query_embedding = model.encode([query], normalize_embeddings=True).tolist()[0]

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=5
        )

        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        for i, (doc, meta, dist) in enumerate(zip(docs, metas, distances), start=1):
            print(f"\nResult #{i}")
            print(f"Score/Distance: {dist}")
            print(f"Title: {meta.get('title')}")
            print(f"Section: {meta.get('section')}")
            print(f"Chunk Type: {meta.get('chunk_type')}")
            print(f"Text: {doc[:500]}...")


if __name__ == "__main__":
    main()