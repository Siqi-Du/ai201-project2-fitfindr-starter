"""
tests/test_agent.py

Unit tests for the agent planning loop (agent.py).
Focuses on verifying that the agent handles errors gracefully and returns
a correct session dict with an 'error' message when something goes wrong.
"""

# pyrefly: ignore [missing-import]
import pytest
from agent import run_agent
from utils.data_loader import get_example_wardrobe


def test_agent_no_search_results():
    """
    Test Case: No search results found.
    
    What it does:
        Passes a query that is guaranteed to find 0 matches in the dataset
        ("designer ballgown size XXS under $5").
        
    What it verifies:
        1. The agent loop does not crash (no exceptions).
        2. `session["error"]` is populated with a helpful error message.
        3. `session["selected_item"]` and other downstream fields remain None.
    """
    wardrobe = get_example_wardrobe()
    session = run_agent(query="designer ballgown size XXS under $5", wardrobe=wardrobe)
    
    assert session["error"] is not None
    assert "No listings found" in session["error"]
    assert "Try a higher budget or broader keywords" in session["error"]
    assert session["selected_item"] is None
    assert session["outfit_suggestion"] is None
    assert session["fit_card"] is None


def test_agent_empty_query():
    """
    Test Case: Empty search query.
    
    What it does:
        Passes an empty string as the query.
        
    What it verifies:
        1. The agent handles the empty string gracefully.
        2. `session["error"]` should be populated because an empty query 
           either fails to parse properly or returns no valid search results.
    """
    wardrobe = get_example_wardrobe()
    session = run_agent(query="", wardrobe=wardrobe)
    
    assert session["error"] is not None
    assert isinstance(session["error"], str)


def test_agent_happy_path():
    """
    Test Case: Happy path (successful search).
    
    What it does:
        Passes a query that will definitely find a match in the dataset
        ("vintage graphic tee").
        
    What it verifies:
        1. The agent completes the entire pipeline without crashing.
        2. `session["error"]` is None.
        3. All output fields (`selected_item`, `outfit_suggestion`, `fit_card`)
           are successfully populated with strings/dicts.
    """
    wardrobe = get_example_wardrobe()
    session = run_agent(query="vintage graphic tee under $30", wardrobe=wardrobe)
    
    assert session["error"] is None
    assert session["selected_item"] is not None
    assert isinstance(session["outfit_suggestion"], str)
    assert isinstance(session["fit_card"], str)
