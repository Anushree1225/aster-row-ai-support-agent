from app.rag.retriever import retrieve


def test_returns_relevant_policy():
    results = retrieve(
        "How many days do I have to return an item?",
        top_k=3,
    )

    assert len(results) > 0

    top_result = results[0]

    assert "returns" in top_result["source"].lower()


def test_retrieval_returns_scores():
    results = retrieve(
        "What is the return policy?",
        top_k=3,
    )

    assert len(results) > 0

    for result in results:
        assert "score" in result
        assert isinstance(result["score"], float)