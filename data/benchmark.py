import json
import statistics
from pathlib import Path
from typing import List, Dict, Any, Set, Tuple

import chromadb

CHROMA_PATH = "./chroma"
COLLECTION_NAME = "stardew_chunks_bge"
TOP_K_VALUES = [1, 3, 5, 10]


def precision_at_k(retrieved: List[str], relevant: Set[str], k: int) -> float:
    retrieved_k = retrieved[:k]
    if not retrieved_k:
        return 0.0
    hits = sum(1 for doc_id in retrieved_k if doc_id in relevant)
    return hits / len(retrieved_k)


def recall_at_k(retrieved: List[str], relevant: Set[str], k: int) -> float:
    if not relevant:
        return 0.0
    retrieved_k = retrieved[:k]
    hits = sum(1 for doc_id in retrieved_k if doc_id in relevant)
    return hits / len(relevant)


def hit_at_k(retrieved: List[str], relevant: Set[str], k: int) -> float:
    retrieved_k = retrieved[:k]
    return 1.0 if any(doc_id in relevant for doc_id in retrieved_k) else 0.0


def reciprocal_rank(retrieved: List[str], relevant: Set[str]) -> float:
    for rank, doc_id in enumerate(retrieved, start=1):
        if doc_id in relevant:
            return 1.0 / rank
    return 0.0


def normalize_title(s: str) -> str:
    return " ".join(s.strip().lower().replace("_", " ").split())


def load_benchmark_file(path: str) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, list):
        return data

    if isinstance(data, dict):
        queries = data.get("queries")
        if isinstance(queries, list):
            return queries

    raise ValueError(
        "Benchmark file must be either a list of test cases or an object with a 'queries' list."
    )


def build_title_index(collection) -> Tuple[Dict[str, Set[str]], Dict[str, Set[str]]]:
    result = collection.get(include=["metadatas"])
    ids = result.get("ids", [])
    metadatas = result.get("metadatas", [])

    title_to_ids: Dict[str, Set[str]] = {}
    normalized_to_originals: Dict[str, Set[str]] = {}

    for doc_id, meta in zip(ids, metadatas):
        if not meta:
            continue
        title = meta.get("title", "")
        if not title:
            continue

        norm = normalize_title(title)
        title_to_ids.setdefault(norm, set()).add(doc_id)
        normalized_to_originals.setdefault(norm, set()).add(title)

    return title_to_ids, normalized_to_originals


def extract_relevant_ids_from_titles(
    expected_titles: List[str],
    title_to_ids: Dict[str, Set[str]],
) -> Tuple[Set[str], List[str]]:
    relevant_ids: Set[str] = set()
    missing_titles: List[str] = []

    for title in expected_titles:
        norm = normalize_title(title)
        matched_ids = title_to_ids.get(norm, set())
        if matched_ids:
            relevant_ids.update(matched_ids)
        else:
            missing_titles.append(title)

    return relevant_ids, missing_titles


def retrieve_ids(collection, query: str, n_results: int) -> Dict[str, Any]:
    result = collection.query(
        query_texts=[query],
        n_results=n_results,
        include=["metadatas", "documents", "distances"]
    )

    ids = result.get("ids", [[]])
    documents = result.get("documents", [[]])
    metadatas = result.get("metadatas", [[]])
    distances = result.get("distances", [[]])

    return {
        "ids": ids[0] if ids else [],
        "documents": documents[0] if documents else [],
        "metadatas": metadatas[0] if metadatas else [],
        "distances": distances[0] if distances else [],
    }


def evaluate_query(
    collection,
    test_case: Dict[str, Any],
    max_k: int,
    title_to_ids: Dict[str, Set[str]],
) -> Dict[str, Any]:
    query = test_case["query"]

    if "relevant_ids" in test_case:
        relevant_ids = set(test_case["relevant_ids"])
        missing_titles = []
    elif "expected_titles" in test_case:
        relevant_ids, missing_titles = extract_relevant_ids_from_titles(
            test_case["expected_titles"],
            title_to_ids
        )
    else:
        raise ValueError(
            f"Test case must contain either 'relevant_ids' or 'expected_titles': {query}"
        )

    retrieved = retrieve_ids(collection, query, max_k)
    retrieved_ids = retrieved["ids"]

    metrics = {
        "query": query,
        "expected_titles": test_case.get("expected_titles", []),
        "missing_expected_titles": missing_titles,
        "relevant_count": len(relevant_ids),
        "retrieved_ids": retrieved_ids,
        "retrieved_titles": [
            (m or {}).get("title", "") for m in retrieved["metadatas"]
        ],
        "distances": retrieved["distances"],
        "mrr": reciprocal_rank(retrieved_ids, relevant_ids),
    }

    for k in TOP_K_VALUES:
        if k <= max_k:
            metrics[f"precision@{k}"] = precision_at_k(retrieved_ids, relevant_ids, k)
            metrics[f"recall@{k}"] = recall_at_k(retrieved_ids, relevant_ids, k)
            metrics[f"hit@{k}"] = hit_at_k(retrieved_ids, relevant_ids, k)

    return metrics


def summarize_results(results: List[Dict[str, Any]]) -> Dict[str, float]:
    if not results:
        return {}

    summary = {}

    metric_keys = [
        key for key in results[0].keys()
        if key.startswith("precision@")
        or key.startswith("recall@")
        or key.startswith("hit@")
        or key == "mrr"
    ]

    for key in metric_keys:
        summary[key] = statistics.mean(r[key] for r in results)

    summary["queries_evaluated"] = len(results)
    summary["queries_with_missing_expected_titles"] = sum(
        1 for r in results if r.get("missing_expected_titles")
    )

    return summary


def main():
    benchmark_path = "./benchmark_queries.json"
    test_cases = load_benchmark_file(benchmark_path)

    client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = client.get_collection(COLLECTION_NAME)

    title_to_ids, _ = build_title_index(collection)

    max_k = max(TOP_K_VALUES)
    results = []

    for test_case in test_cases:
        result = evaluate_query(collection, test_case, max_k, title_to_ids)
        results.append(result)

    summary = summarize_results(results)

    print("\n=== Aggregate Metrics ===")
    for key, value in sorted(summary.items()):
        if isinstance(value, float):
            print(f"{key:35s}: {value:.4f}")
        else:
            print(f"{key:35s}: {value}")

    print("\n=== Per Query Results ===")
    for r in results:
        print(f"\nQuery: {r['query']}")
        print(f"MRR: {r['mrr']:.4f}")
        if r["missing_expected_titles"]:
            print("Missing expected titles in collection:", r["missing_expected_titles"])
        for k in TOP_K_VALUES:
            if f"precision@{k}" in r:
                print(
                    f"P@{k}: {r[f'precision@{k}']:.2f} | "
                    f"R@{k}: {r[f'recall@{k}']:.2f} | "
                    f"Hit@{k}: {r[f'hit@{k}']:.0f}"
                )
        print("Top titles:", r["retrieved_titles"][:5])

    output = {
        "summary": summary,
        "results": results
    }

    Path("./benchmark_results.json").write_text(
        json.dumps(output, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )
    print("\nSaved results to benchmark_results.json")


if __name__ == "__main__":
    main()