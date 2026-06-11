# FitFindr — planning.md

> Complete this document before writing any implementation code.
> Your spec and agent diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Your planning.md will be reviewed as part of your submission.
> Update it before starting any stretch features.

---

## Tools

List every tool your agent will use. For each tool, fill in all four fields.
You must have at least 3 tools. The three required tools are listed — add any additional tools below them.

### Tool 1: search_listings

**What it does:**
<!-- Describe what this tool does in 1–2 sentences -->
The search_listings is the tool that will search the items using id, name, title...

**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
- `description` (str): here we have a string this is where the users gives all details by constructing his sentence, where to look and what to look for.
- `size` (str): here also we have a string type, where the user give somthing like small, medium or large..
- `max_price` (float): here we have a float type the user tells the tool what is his buying power and can gives something like $25

**What it returns:**
<!-- Describe the return value — what fields does a result contain? -->
should return a list of matching listing dictionaries.

**What happens if it fails or returns nothing:**
<!-- What should the agent do if no listings match? -->
if no listing match the agent can go for memory or drop someting like the color, or try any other brand, platform or condition to increase the chances of finding a match.

---

### Tool 2: suggest_outfit

**What it does:**
<!-- Describe what this tool does in 1–2 sentences -->
this tool is after the agent find a match it will output those items as sugestion, something 'here what i have found....

**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
- `new_item` (dict): this is a dictionary it represent items that did not exist yet in the user search list or previous items
- `wardrobe` (dict): this is dictionary item and value it represent items that the user already has in his wardrobe

**What it returns:**
<!-- Describe the return value -->
should return an outfit dictionary.”

**What happens if it fails or returns nothing:**
<!-- What should the agent do if the wardrobe is empty or no outfit can be suggested? -->
the agent should tell the user to try different option

---

### Tool 3: create_fit_card

**What it does:**
<!-- Describe what this tool does in 1–2 sentences -->
this tools tell the user how the outfit will look on the user "thrifted this faded band tee off depop for $22 and honestly it was made for my wide-legs 🖤 full look in my stories"

**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
- `outfit` (id(int), title(str), description(str), category(str), style_tags(str), size(str/int), condition(str), price(float), colors(str), brand(str), platform(str)):  all represent the details the tool should focus on while looking for the item.

**What it returns:**
<!-- Describe the return value -->
should return a short formatted text/card

**What happens if it fails or returns nothing:**
<!-- What should the agent do if the outfit data is incomplete? -->
suggest the user to try differently

---

### Additional Tools (if any)

<!-- Copy the block above for any tools beyond the required three -->

---

## Planning Loop

**How does your agent decide which tool to call next?**
<!-- Describe the logic your planning loop uses. What does it look at? What conditions change its behavior? How does it know when it's done? -->
The agent first reads the user query and extracts shopping constraints such as item description, style, size, max price, color, brand, and platform if mentioned. It calls search_listings first to find matching secondhand items. If listings are found, it stores the best match in session state and then calls suggest_outfit to style the item with the user’s wardrobe. After an outfit is created, it calls create_fit_card to generate a polished final recommendation. The agent is done when it has returned a listing, outfit suggestion, and fit card to the user.

---

## State Management

**How does information from one tool get passed to the next?**
<!-- Describe how your agent stores and accesses state within a session. What data is tracked? How is it passed between tool calls? -->
The agent keeps a session state dictionary that stores the original user query, extracted search filters, search results, selected listing, wardrobe items, outfit suggestion, and final fit card. Information from one tool is passed to the next through this state. For example, search_listings returns matching listings, then the selected listing becomes the new_item input for suggest_outfit, and the outfit returned by suggest_outfit becomes the input for create_fit_card.

---

## Error Handling

For each tool, describe the specific failure mode you're handling and what the agent does in response.

| Tool | Failure mode | Agent response |
|------|-------------|----------------|
| search_listings | No results match the query | The agent relaxes one filter, such as color, brand, or platform, and tries again. If there are still no results, it tells the user no exact match was found and suggests changing size, budget, or style.                 |


| suggest_outfit | Wardrobe is empty | The agent suggests a full outfit using only available listings and explains that no wardrobe items were available to pair with the new item. |




| create_fit_card | Outfit input is missing or incomplete |The agent returns a simpler recommendation using the information available and asks the user for missing details if needed. |

---

## Architecture

<!-- Draw a diagram of your agent showing how the components connect:
     User input → Planning Loop → Tools (search_listings, suggest_outfit, create_fit_card)
                                                                          ↕
                                                                   State / Session
     Show what triggers each tool, how state flows between them, and where error paths branch off.
     ASCII art, a Mermaid diagram (https://mermaid.js.org/syntax/flowchart.html), or an embedded
     sketch are all fine. You'll share this diagram with an AI tool when asking it to implement
     the planning loop and each individual tool. -->
User input
↓
Planning Loop
↓
Extract item description, size, max price, style, and color
↓
search_listings
↓
Store matching listings in session state
↓
suggest_outfit
↓
Combine selected listing with wardrobe items
↓
create_fit_card
↓
Generate final styled recommendation
↓
Final answer to user

State / Session stores:

original query
search filters
retrieved listings
selected listing
wardrobe
outfit suggestion
final fit card

---

## AI Tool Plan

<!-- For each part of the implementation below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, your agent diagram)
     - What you expect it to produce
     - How you'll verify the output matches your spec before moving on

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Tool 1 spec (inputs, return value, failure mode) and ask it to implement
     search_listings() using load_listings() from the data loader — then test it against 3 queries
     before trusting it" is a plan. -->

**Milestone 3 — Individual tool implementations:**
I will use ChatGPT to help implement each tool one at a time. I will give it the tool descriptions, input parameters, return format, and failure behavior from this planning document. I expect it to produce Python functions for search_listings, suggest_outfit, and create_fit_card. I will verify each function by testing it with at least 3 inputs, including one failure case.

**Milestone 4 — Planning loop and state management:**
I will use ChatGPT to help implement the planning loop that decides which tool to call next. I will give it my Architecture, Planning Loop, and State Management sections. I expect it to produce code that takes a user query, calls the tools in the correct order, stores intermediate results in state, and returns a final answer. I will verify it by running the complete example interaction and checking that each tool receives the correct input.

---

## A Complete Interaction (Step by Step)

Write out what a full user interaction looks like from start to finish — tool call by tool call. Use a specific example query.

**Example user query:** "I'm looking for a vintage graphic tee under $30. I mostly wear baggy jeans and chunky sneakers. What's out there and how would I style it?"

**Step 1:**
<!-- What does the agent do first? Which tool is called? With what input? -->
The agent extracts the search constraints: description = "vintage graphic tee", max_price = 30, and style = "vintage/streetwear". It calls search_listings with those values.

**Step 2:**
<!-- What happens next? What was returned from step 1? What tool is called now? 
-->
search_listings returns matching listings from listings.json, including item id, title, description, category, size, condition, price, colors, brand, and platform. The agent selects the best match and stores it in session state.

**Step 3:**
<!-- Continue until the full interaction is complete -->
The agent calls create_fit_card using the outfit. This tool creates a short, styled recommendation explaining how the outfit looks and why the pieces work together.

**Final output to user:**
<!-- What does the user actually see at the end? -->
"I found a vintage graphic tee under $30 from the listings. I would style it with your baggy jeans and chunky sneakers for a relaxed streetwear look. Fit card: thrifted vintage graphic tee + baggy jeans + chunky sneakers — casual, oversized, and easy to wear."
