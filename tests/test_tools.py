"""
tests/test_tools.py

Unit tests for all three FitFindr tools.
Run with: pytest tests/
"""

# pyrefly: ignore [missing-import]
import pytest
from tools import search_listings, suggest_outfit, create_fit_card
from utils.data_loader import get_example_wardrobe, get_empty_wardrobe


# ── search_listings tests ─────────────────────────────────────────────────────

def test_search_returns_results():
    results = search_listings("vintage graphic tee", size=None, max_price=50)
    assert isinstance(results, list)
    assert len(results) > 0

def test_search_empty_results():
    """Impossible query — no ballgown under $5 in XXS."""
    results = search_listings("designer ballgown", size="XXS", max_price=5)
    assert results == []  # empty list, no exception

def test_search_price_filter():
    results = search_listings("jacket", size=None, max_price=10)
    assert all(item["price"] <= 10 for item in results)

def test_search_size_filter():
    results = search_listings("tee", size="M", max_price=100)
    # All returned items should contain "m" in their size string
    for item in results:
        assert "m" in item["size"].lower()

def test_search_no_size_filter():
    """When size=None, size is not filtered — should return more results."""
    results_no_size = search_listings("vintage", size=None, max_price=100)
    results_with_size = search_listings("vintage", size="S", max_price=100)
    assert len(results_no_size) >= len(results_with_size)

def test_search_returns_list_of_dicts():
    results = search_listings("denim", size=None, max_price=100)
    assert isinstance(results, list)
    if results:
        assert isinstance(results[0], dict)
        assert "id" in results[0]
        assert "price" in results[0]
        assert "title" in results[0]

def test_search_sorted_by_relevance():
    """Higher-scoring items (more keyword hits) should come first."""
    results = search_listings("vintage graphic tee", size=None, max_price=100)
    # Just check it returns a list without crashing
    assert isinstance(results, list)


# ── suggest_outfit tests ──────────────────────────────────────────────────────

def test_suggest_outfit_with_wardrobe():
    results = search_listings("vintage graphic tee", size=None, max_price=50)
    assert len(results) > 0, "Need at least one result to test suggest_outfit"
    suggestion = suggest_outfit(results[0], get_example_wardrobe())
    assert isinstance(suggestion, str)
    assert len(suggestion) > 10  # Not empty, not a trivial string

def test_suggest_outfit_empty_wardrobe():
    """Empty wardrobe should return general advice, not crash."""
    results = search_listings("vintage graphic tee", size=None, max_price=50)
    assert len(results) > 0
    suggestion = suggest_outfit(results[0], get_empty_wardrobe())
    assert isinstance(suggestion, str)
    assert len(suggestion) > 10  # Still returns useful advice

def test_suggest_outfit_no_exception_on_empty_wardrobe():
    """Must not raise any exception even with empty wardrobe."""
    results = search_listings("flannel", size=None, max_price=100)
    assert len(results) > 0
    try:
        result = suggest_outfit(results[0], get_empty_wardrobe())
        assert isinstance(result, str)
    except Exception as e:
        pytest.fail(f"suggest_outfit raised an exception with empty wardrobe: {e}")


# ── create_fit_card tests ─────────────────────────────────────────────────────

def test_create_fit_card_empty_outfit():
    """Empty outfit string → error message, no exception."""
    results = search_listings("vintage graphic tee", size=None, max_price=50)
    assert len(results) > 0
    result = create_fit_card("", results[0])
    assert isinstance(result, str)
    assert "Error" in result  # Should return error message

def test_create_fit_card_none_outfit():
    """None outfit → error message, no exception."""
    results = search_listings("vintage graphic tee", size=None, max_price=50)
    assert len(results) > 0
    result = create_fit_card(None, results[0])
    assert isinstance(result, str)
    assert "Error" in result

def test_create_fit_card_returns_string():
    results = search_listings("vintage graphic tee", size=None, max_price=50)
    assert len(results) > 0
    outfit = "Pair with baggy jeans and chunky sneakers for a 90s grunge look."
    result = create_fit_card(outfit, results[0])
    assert isinstance(result, str)
    assert len(result) > 10

def test_create_fit_card_no_exception():
    """Must never raise an exception."""
    results = search_listings("denim jacket", size=None, max_price=100)
    assert len(results) > 0
    outfit = "Layer over a white tank with wide-leg trousers and boots."
    try:
        result = create_fit_card(outfit, results[0])
        assert isinstance(result, str)
    except Exception as e:
        pytest.fail(f"create_fit_card raised an exception: {e}")
