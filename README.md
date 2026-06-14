# FitFindr — Project 2

FitFindr is a secondhand fashion agent that helps users find thrifted clothing items and style them with an existing wardrobe. The agent searches a mock listings dataset, suggests outfit combinations, and creates a short social-media-style fit card.

## Project Overview

This project demonstrates a tool-using AI agent. Instead of only answering from a prompt, the agent makes decisions about which tool to call next, stores intermediate results in session state, and handles failure cases gracefully.

The agent uses three tools:

1. `search_listings`
2. `suggest_outfit`
3. `create_fit_card`

The full flow is:

```text
User query
↓
Planning loop
↓
search_listings
↓
selected_item stored in session
↓
suggest_outfit
↓
outfit_suggestion stored in session
↓
create_fit_card
↓
final response
```

## Setup

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```text
GROQ_API_KEY=your_key_here
```

Run the app:

```bash
python app.py
```

Then open the local Gradio URL shown in the terminal.

## Tool Inventory

### Tool 1: `search_listings(description, size=None, max_price=None)`

**Purpose:**
Searches the mock secondhand listings dataset for items matching a user’s description, optional size, and optional maximum price.

**Inputs:**

* `description` (`str`): The item or style the user is searching for, such as `"vintage graphic tee"`.
* `size` (`str | None`): Optional size filter, such as `"M"` or `"XXS"`.
* `max_price` (`float | None`): Optional price ceiling.

**Output:**
Returns a list of matching listing dictionaries. Each listing can contain fields such as `id`, `title`, `description`, `category`, `style_tags`, `size`, `condition`, `price`, `colors`, `brand`, `platform`, and `score`.

**Failure behavior:**
If no listings match, the tool returns an empty list `[]` instead of raising an exception.

### Tool 2: `suggest_outfit(new_item, wardrobe)`

**Purpose:**
Takes the selected thrifted item and the user’s wardrobe, then generates one or two outfit suggestions.

**Inputs:**

* `new_item` (`dict`): The selected listing from `search_listings`.
* `wardrobe` (`dict`): A wardrobe dictionary containing an `items` list.

**Output:**
Returns a string with outfit ideas. When the wardrobe has items, the suggestions use specific pieces from the wardrobe. When the wardrobe is empty, the tool gives general styling advice.

**Failure behavior:**
If the wardrobe is empty, the tool still returns useful styling advice instead of crashing.

### Tool 3: `create_fit_card(outfit, new_item)`

**Purpose:**
Creates a short, shareable outfit caption for the thrifted item and outfit suggestion.

**Inputs:**

* `outfit` (`str`): The outfit suggestion created by `suggest_outfit`.
* `new_item` (`dict`): The selected listing.

**Output:**
Returns a 2–4 sentence fit card or social-media-style caption.

**Failure behavior:**
If the outfit string is empty, the tool returns a descriptive error message instead of raising an exception.

## Planning Loop

The planning loop is implemented in `run_agent()` inside `agent.py`.

The agent first initializes a session dictionary. Then it parses the user query to extract a description, size, and maximum price. It calls `search_listings()` using those parsed values. If no listings are found, the agent stores an error message in `session["error"]` and stops early.

If listings are found, the agent selects the top result and stores it in `session["selected_item"]`. That selected item is passed into `suggest_outfit()` along with the wardrobe. The returned outfit suggestion is stored in `session["outfit_suggestion"]`. Finally, the agent passes the outfit suggestion and selected item into `create_fit_card()` and stores the result in `session["fit_card"]`.

The agent does not call every tool unconditionally. It only calls `suggest_outfit()` and `create_fit_card()` when `search_listings()` returns at least one matching listing.

## State Management

The agent uses a session dictionary to store information during one interaction.

The session stores:

* `query`: the original user query
* `parsed`: extracted description, size, and max price
* `search_results`: listings returned by `search_listings`
* `selected_item`: the top listing selected for styling
* `wardrobe`: the user’s wardrobe
* `outfit_suggestion`: the output from `suggest_outfit`
* `fit_card`: the output from `create_fit_card`
* `error`: an error message if the agent stops early

This state object allows data to move clearly from one tool to the next. For example, the selected listing from `search_listings()` becomes the `new_item` input for `suggest_outfit()`. The outfit suggestion then becomes the `outfit` input for `create_fit_card()`.

## Error Handling

### No search results

Test query:

```text
designer ballgown size XXS under $5
```

Result:

```text
I couldn't find any listings that match your request. Try increasing your budget, removing the size filter, or using a broader style description.
```

The agent stops early and does not call the outfit or fit card tools.

### Empty wardrobe

When the user selects the empty wardrobe option, the agent still creates general outfit advice for the selected item. This avoids crashing when a new user has no saved wardrobe items.

### Missing outfit input

When `create_fit_card()` receives an empty outfit string, it returns:

```text
I can't create a fit card because the outfit suggestion is missing.
```

This prevents the system from failing with a Python exception.

## Example Interaction

User query:

```text
vintage graphic tee under $30
```

Top listing found:

```text
Y2K Baby Tee — Butterfly Print
Price: $18
Platform: depop
Colors: white, pink, purple
```

The agent then suggests outfits using the example wardrobe, such as pairing the tee with baggy jeans and chunky sneakers. Finally, it creates a fit card caption describing the item and outfit vibe.

## Interface

The Gradio interface has:

* A text input for the shopping query
* A wardrobe selector
* A panel for the top listing
* A panel for the outfit suggestion
* A panel for the fit card

For a successful query, all three panels populate. For a no-results query, the first panel shows the error message and the other two panels remain blank.

## Spec Reflection

One way the spec helped me was by forcing me to define each tool before writing code. This made it easier to test each function separately and understand what each function should return. The planning loop section also helped me avoid calling all tools unconditionally.

One way my implementation changed from the original plan was that I kept `suggest_outfit()` returning a string instead of an outfit dictionary. This matched the starter code signature and made it easier to pass the generated outfit directly into `create_fit_card()`.

## AI Usage

### Instance 1

**What I gave the AI:**
I gave ChatGPT my Tool 1 specification for `search_listings`, including the input parameters, return format, and failure behavior.

**What it produced:**
It produced a Python function that loads listings, filters by price and size, scores matches by keyword overlap, and returns a sorted list.

**What I changed or overrode:**
I adjusted the code to handle `None` values in listing fields such as `brand`, because one listing had `brand: None` and caused a string join error.

### Instance 2

**What I gave the AI:**
I gave ChatGPT my planning loop, state management section, and agent architecture.

**What it produced:**
It produced a `run_agent()` implementation that parses the query, calls `search_listings`, stores the selected item in session state, calls `suggest_outfit`, and then calls `create_fit_card`.

**What I changed or overrode:**
I tested the no-results branch and confirmed that the agent stops early when no listings are found. I also verified that the fit card stays blank in the UI for no-results queries.

## Demo Notes

The demo video should show:

1. A successful query such as `"vintage graphic tee under $30"`.
2. The selected listing, outfit suggestion, and fit card.
3. A no-results query such as `"designer ballgown size XXS under $5"`.
4. The agent’s graceful error response.
5. A short explanation of how state passes from `selected_item` to `outfit_suggestion` to `fit_card`.
