"""
tools.py

The three required FitFindr tools. Each tool is a standalone function that
can be called and tested independently before being wired into the agent loop.

Complete and test each tool before moving to agent.py.

Tools:
    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)              → str
    create_fit_card(outfit, new_item)               → str
"""

import os

from dotenv import load_dotenv
from groq import Groq

from utils.data_loader import load_listings

load_dotenv()


# ── Groq client ───────────────────────────────────────────────────────────────

def _get_groq_client():
    """Initialize and return a Groq client using GROQ_API_KEY from .env."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY not set. Add it to a .env file in the project root."
        )
    return Groq(api_key=api_key)


# ── Tool 1: search_listings ───────────────────────────────────────────────────

def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Search the mock listings dataset for items matching the description,
    optional size, and optional price ceiling.
    """
    listings = load_listings()

    if not description or not description.strip():
        return []

    keywords = description.lower().strip().split()
    matches = []

    for item in listings:
        # Price filter
        if max_price is not None and item["price"] > max_price:
            continue

        # Size filter
        if size is not None:
            user_size = size.lower().strip()
            item_size = str(item.get("size", "")).lower()

            if user_size not in item_size:
                continue
        searchable_text = " ".join([
            str(item.get("title") or ""),
            str(item.get("description") or ""),
            str(item.get("category") or ""),
            str(item.get("brand") or ""),
            str(item.get("platform") or ""),
            " ".join(item.get("style_tags") or []),
            " ".join(item.get("colors") or []),
        ]).lower()
        score = 0

        for word in keywords:
            if word in searchable_text:
                score += 1

        if score > 0:
            item_with_score = dict(item)
            item_with_score["score"] = score
            matches.append(item_with_score)

    matches.sort(key=lambda item: item["score"], reverse=True)

    return matches


# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    """
    Given a thrifted item and the user's wardrobe, suggest 1–2 complete outfits.
    """
    client = _get_groq_client()

    wardrobe_items = wardrobe.get("items", []) if wardrobe else []

    item_summary = f"""
Item title: {new_item.get("title")}
Description: {new_item.get("description")}
Category: {new_item.get("category")}
Style tags: {", ".join(new_item.get("style_tags") or [])}
Size: {new_item.get("size")}
Condition: {new_item.get("condition")}
Price: ${new_item.get("price")}
Colors: {", ".join(new_item.get("colors") or [])}
Brand: {new_item.get("brand") or "unknown"}
Platform: {new_item.get("platform") or "unknown"}
"""

    if not wardrobe_items:
        prompt = f"""
You are FitFindr, a secondhand fashion styling assistant.

The user is considering this thrifted item:

{item_summary}

The user has not provided any wardrobe items.

Suggest 1–2 general outfit ideas for styling this item.
Be specific, practical, and casual.
Mention what types of bottoms, shoes, and accessories would pair well.
"""
    else:
        wardrobe_summary = ""

        for item in wardrobe_items:
            wardrobe_summary += (
                f"- {item.get('name') or item.get('title')}: "
                f"{item.get('category', 'unknown category')}, "
                f"colors: {', '.join(item.get('colors') or [])}, "
                f"style: {', '.join(item.get('style_tags') or [])}\n"
            )

        prompt = f"""
You are FitFindr, a secondhand fashion styling assistant.

The user is considering this thrifted item:

{item_summary}

The user already owns these wardrobe items:

{wardrobe_summary}

Suggest 1–2 complete outfits using the thrifted item and specific wardrobe pieces.
Explain briefly why the pieces work together.
Keep the tone friendly, stylish, and practical.
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful fashion styling assistant. Give grounded styling advice using only the item and wardrobe details provided.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.4,
    )

    return response.choices[0].message.content


# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def create_fit_card(outfit: str, new_item: dict) -> str:
    """
    Generate a short, shareable outfit caption for the thrifted find.
    """
    if not outfit or not outfit.strip():
        return "I can't create a fit card because the outfit suggestion is missing."

    client = _get_groq_client()

    item_title = new_item.get("title", "this thrifted item")
    price = new_item.get("price", "unknown price")
    platform = new_item.get("platform") or "secondhand platform"
    colors = ", ".join(new_item.get("colors") or [])
    style_tags = ", ".join(new_item.get("style_tags") or [])

    prompt = f"""
Create a short social-media-style outfit caption.

Thrifted item:
- Title: {item_title}
- Price: ${price}
- Platform: {platform}
- Colors: {colors}
- Style tags: {style_tags}

Outfit suggestion:
{outfit}

Requirements:
- 2 to 4 sentences only
- Casual and authentic, like an OOTD post
- Mention the item name, price, and platform naturally once
- Capture the outfit vibe in specific terms
- Do not sound like a formal product description
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "You write casual, stylish, social-media-ready outfit captions.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.8,
    )

    return response.choices[0].message.content

if __name__ == "__main__":
    results = search_listings("vintage graphic tee", size=None, max_price=50)
    new_item = results[0]

    test_wardrobe = {
        "items": [
            {
                "name": "Baggy light wash jeans",
                "category": "bottoms",
                "colors": ["light blue"],
                "style_tags": ["streetwear", "casual"],
            },
            {
                "name": "Chunky white sneakers",
                "category": "shoes",
                "colors": ["white"],
                "style_tags": ["streetwear", "casual"],
            },
        ]
    }

    outfit = suggest_outfit(new_item, test_wardrobe)

    print("\nOutfit suggestion:\n")
    print(outfit)

    fit_card = create_fit_card(outfit, new_item)

    print("\nFit card:\n")
    print(fit_card)

    print("\nMissing outfit test:\n")
    print(create_fit_card("", new_item))

    