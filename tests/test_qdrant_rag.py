"""Unit tests for Embedded Qdrant Policy Vector Store and retrieval."""

import pytest
from credsure.rag.policy_loader import PolicyDocumentLoader
from credsure.rag.vector_store import QdrantPolicyVectorStore


def test_policy_loader_seed_chunks():
    """Verify standard underwriting policy seed chunks are well-formed."""
    loader = PolicyDocumentLoader(policy_dir="./data/policies")
    chunks = loader.load_all_chunks()

    assert len(chunks) >= 7
    categories = {c["rule_category"] for c in chunks}
    assert "score_thresholds" in categories
    assert "utilization" in categories
    assert "delinquency" in categories
    assert "basel_capital" in categories


def test_qdrant_vector_search():
    """Verify embedded Qdrant indexes chunks and performs cosine retrieval."""
    loader = PolicyDocumentLoader(policy_dir="./data/policies")
    chunks = loader.load_all_chunks()

    vstore = QdrantPolicyVectorStore(storage_path="./data/qdrant_storage")
    indexed = vstore.index_policies(chunks)
    assert indexed > 0

    # Search for score approval thresholds
    results = vstore.search("minimum FICO credit score for automated approval", limit=3)
    assert len(results) > 0
    top_result = results[0]
    assert "text" in top_result
    assert "section_title" in top_result
    assert top_result["score"] >= 0.0

    # Search with metadata filter
    cat_results = vstore.search("revolving debt", limit=2, rule_category="utilization")
    assert len(cat_results) > 0
    assert cat_results[0]["rule_category"] == "utilization"
