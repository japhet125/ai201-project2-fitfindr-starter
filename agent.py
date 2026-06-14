"""
agent.py

The FitFindr planning loop. Orchestrates the three tools in response to a
natural language user query, passing state between them via a session dict.

Complete tools.py and test each tool in isolation before implementing this file.

Usage (once implemented):
    from agent import run_agent
    from utils.data_loader import get_example_wardrobe

    result = run_agent(
        query="vintage graphic tee under $30, size M",
        wardrobe=get_example_wardrobe(),
    )
    print(result["fit_card"])
    print(result["error"])   # None on success
"""


import re
from tools import search_listings, suggest_outfit, create_fit_card


# ── session state ─────────────────────────────────────────────────────────────

def _new_session(query: str, wardrobe: dict) -> dict:
    """
    Initialize and return a fresh session dict for one user interaction.

    The session dict is the single source of truth for everything that happens
    during a run — it stores the original query, parsed parameters, tool results,
    and any error that caused early termination.

    You may add fields to this dict as needed for your implementation.
    """
    return {
        "query": query,              # original user query
        "parsed": {},                # extracted description / size / max_price
        "search_results": [],        # list of matching listing dicts
        "selected_item": None,       # top result, passed into suggest_outfit
        "wardrobe": wardrobe,        # user's wardrobe dict
        "outfit_suggestion": None,   # string returned by suggest_outfit
        "fit_card": None,            # string returned by create_fit_card
        "error": None,               # set if the interaction ended early
    }


# ── planning loop ─────────────────────────────────────────────────────────────
def run_agent(query: str, wardrobe: dict) -> dict:
    session = _new_session(query, wardrobe)

    # Step 2: Parse query
    query_lower = query.lower()

    # Extract max price like "$30" or "under 30"
    price_match = re.search(r"\$?(\d+(?:\.\d+)?)", query_lower)
    max_price = float(price_match.group(1)) if price_match else None

    # Extract size
    size_match = re.search(r"\b(size\s*)?(xxs|xs|s|m|l|xl|xxl)\b", query_lower)
    size = size_match.group(2).upper() if size_match else None

    # Clean description by removing price/size words
    description = query_lower
    description = re.sub(r"under\s+\$?\d+(?:\.\d+)?", "", description)
    description = re.sub(r"\$?\d+(?:\.\d+)?", "", description)
    description = re.sub(r"\bsize\s*(xxs|xs|s|m|l|xl|xxl)\b", "", description)
    description = re.sub(r"\b(xxs|xs|s|m|l|xl|xxl)\b", "", description)
    description = description.replace("looking for", "")
    description = description.replace("i'm", "")
    description = description.replace("im", "")
    description = description.strip(" ,.")

    session["parsed"] = {
        "description": description,
        "size": size,
        "max_price": max_price,
    }

    # Step 3: Search listings
    search_results = search_listings(
        description=description,
        size=size,
        max_price=max_price,
    )

    session["search_results"] = search_results

    if not search_results:
        session["error"] = (
            "I couldn't find any listings that match your request. "
            "Try increasing your budget, removing the size filter, or using a broader style description."
        )
        return session

    # Step 4: Select top result
    selected_item = search_results[0]
    session["selected_item"] = selected_item

    # Step 5: Suggest outfit
    outfit_suggestion = suggest_outfit(selected_item, wardrobe)
    session["outfit_suggestion"] = outfit_suggestion

    # Step 6: Create fit card
    fit_card = create_fit_card(outfit_suggestion, selected_item)
    session["fit_card"] = fit_card

    # Step 7: Return session
    return session 

# ── CLI test ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    from utils.data_loader import get_example_wardrobe, get_empty_wardrobe

    print("=== Happy path: graphic tee ===\n")
    session = run_agent(
        query="looking for a vintage graphic tee under $30",
        wardrobe=get_example_wardrobe(),
    )
    if session["error"]:
        print(f"Error: {session['error']}")
    else:
        print(f"Found: {session['selected_item']['title']}")
        print(f"\nOutfit: {session['outfit_suggestion']}")
        print(f"\nFit card: {session['fit_card']}")

    print("\n\n=== No-results path ===\n")
    session2 = run_agent(
        query="designer ballgown size XXS under $5",
        wardrobe=get_example_wardrobe(),
    )
    print(f"Error message: {session2['error']}")
