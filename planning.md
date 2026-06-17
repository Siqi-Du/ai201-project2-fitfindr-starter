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
Searches the mock listings dataset and returns items that match the user's description, size, and maximum price. It filters by keyword match against title, description, and style_tags, then filters by size (if provided) and price ceiling. Results are sorted by price ascending so the cheapest match comes first.

**Input parameters:**
- `description` (str): A free-text keyword the user is looking for, e.g. "vintage graphic tee". Matched against title, description, and style_tags fields.
- `size` (str or None): The clothing size to filter by, e.g. "M", "W30". If None, size is not filtered.
- `max_price` (float): The maximum price the user is willing to pay. Only items with price ≤ max_price are returned.

**What it returns:**
A list of listing dicts (may be empty). Each dict contains all fields from listings.json: `id` (str), `title` (str), `description` (str), `category` (str), `style_tags` (list[str]), `size` (str), `condition` (str), `price` (float), `colors` (list[str]), `brand` (str or None), `platform` (str). Results sorted by relevance score descending (score = number of user keywords found in the listing's title + description + style_tags + category). Example: `[{"id": "lst_033", "title": "Vintage Band Tee — Faded Grey", "price": 19.0, "platform": "depop", ...}]`

**What happens if it fails or returns nothing:**
Returns an empty list `[]`. The agent checks `if len(results) == 0`, sets `session["error"] = "No listings found for '[description]' under $[max_price]. Try a higher budget or broader keywords like 'tee' instead of 'graphic tee'."` and returns the session immediately without calling suggest_outfit or create_fit_card.

---

### Tool 2: suggest_outfit

**What it does:**
Given a newly found secondhand item and the user's current wardrobe, uses the Groq LLM to suggest one complete outfit combination. The LLM is given the new item's title, category, colors, and style_tags plus the full list of wardrobe items, and it returns a 2–3 sentence styling recommendation.

**Input parameters:**
- `new_item` (dict): The listing dict selected from search_listings results. Must have at minimum: `title` (str), `category` (str), `colors` (list[str]), `style_tags` (list[str]), `price` (float), `platform` (str).
- `wardrobe` (dict): A wardrobe dict with an `items` key containing a list of wardrobe item dicts. Each wardrobe item has: `id` (str), `name` (str), `category` (str), `colors` (list[str]), `style_tags` (list[str]), `notes` (str or None).

**What it returns:**
A non-empty string containing the outfit suggestion, e.g. "Pair this faded graphic tee with your baggy straight-leg jeans and chunky white sneakers. Tuck the front corner slightly for shape. Add the black denim jacket on top for a classic 90s grunge feel."

**What happens if it fails or returns nothing:**
If `wardrobe["items"]` is empty, the LLM prompt changes to ask for general styling advice without referencing a specific wardrobe — the function still returns a useful string like "This tee pairs well with wide-leg jeans or baggy cargos. Finish with chunky sneakers or combat boots." It never raises an exception or returns an empty string.

---

### Tool 3: create_fit_card

**What it does:**
Generates a short, casual, shareable caption for the outfit — the kind of text someone would post on Instagram or TikTok. Uses the Groq LLM with a higher temperature (0.9+) so each call produces a different result. The output should sound human and enthusiastic, not like a product description.

**Input parameters:**
- `outfit` (str): The outfit suggestion string returned by suggest_outfit. Must be non-empty.
- `new_item` (dict): The listing dict for the thrifted item. Used to pull in price, platform, and title for the caption.

**What it returns:**
A single string of 1–2 sentences in casual social media style, e.g. "thrifted this faded band tee off depop for $19 and honestly it was made for my baggy jeans 🖤 90s grunge but make it effortless". Always different for different inputs due to high LLM temperature.

**What happens if it fails or returns nothing:**
If `outfit` is an empty string or None, returns the error string `"Error: outfit description is required to generate a fit card."` without calling the LLM. If the LLM call fails (network error, etc.), catches the exception and returns `"Error: could not generate fit card. Please try again."` — never raises an exception to the caller.

---

### Additional Tools (if any)

None for required features. Stretch feature (price comparison tool) would be added here if implemented.

---

## Planning Loop

**How does your agent decide which tool to call next?**

The planning loop in `run_agent()` follows this conditional logic:

1. **Call** `search_listings(description, size, max_price)` with the user's inputs.
2. **Check result**: `if len(results) == 0` → set `session["error"]` with a helpful message, return session immediately. Do NOT proceed to step 3 or 4.
3. **If results found**: set `session["selected_item"] = results[0]` (cheapest match after price-sort). Call `suggest_outfit(new_item=session["selected_item"], wardrobe=wardrobe)`.
4. **Check result**: `if not outfit_suggestion or outfit_suggestion.startswith("Error")` → set `session["error"]`, return session early.
5. **If outfit found**: set `session["outfit_suggestion"] = outfit_suggestion`. Call `create_fit_card(outfit=session["outfit_suggestion"], new_item=session["selected_item"])`.
6. Set `session["fit_card"] = fit_card_result`. Return session.

The loop always stops early if any tool returns an empty or error result — it never calls a later tool with bad input.

---

## State Management

**How does information from one tool get passed to the next?**

A single `session` dict is created at the start of `run_agent()` and passed by reference through all steps:

```python
session = {
    "query": description,          # original user query
    "selected_item": None,         # set after search_listings succeeds
    "outfit_suggestion": None,     # set after suggest_outfit succeeds
    "fit_card": None,              # set after create_fit_card succeeds
    "error": None,                 # set if any tool fails, triggers early return
}
```

Data flow: `search_listings` → writes `session["selected_item"]` → `suggest_outfit` reads it → writes `session["outfit_suggestion"]` → `create_fit_card` reads both → writes `session["fit_card"]`. No tool re-asks the user for data that is already in session.

---

## Error Handling

For each tool, describe the specific failure mode you're handling and what the agent does in response.

| Tool | Failure mode | Agent response |
|------|-------------|----------------|
| search_listings | No results match the query | Returns `[]`. Agent sets `session["error"] = "No listings found for '[query]' under $[max_price]. Try a higher budget or broader keywords."` and returns immediately without calling other tools. |
| suggest_outfit | Wardrobe is empty (`items = []`) | LLM prompt switches to general styling advice mode. Returns a useful suggestion string without referencing specific wardrobe pieces. Agent continues normally — this is not treated as an error. |
| create_fit_card | Outfit input is empty string or None | Returns error string `"Error: outfit description is required to generate a fit card."` without calling LLM. Agent sets `session["error"]` to this string. |

---

## Architecture

```
User Input (description, size, max_price, wardrobe)
    │
    ▼
run_agent() — Planning Loop
    │
    ├─► search_listings(description, size, max_price)
    │       │
    │       ├── results == []  ──────────────────────────────────────────┐
    │       │                                                            │
    │       └── results = [item, ...]                                    │
    │               │                                                    │
    │       session["selected_item"] = results[0]                        │
    │               │                                                    │
    ├─► suggest_outfit(new_item=selected_item, wardrobe=wardrobe)        │
    │       │                                                            │
    │       ├── wardrobe empty → general advice (no early exit)          │
    │       │                                                            │
    │       └── outfit_suggestion = "Pair with your jeans..."            │
    │               │                                                    │
    │       session["outfit_suggestion"] = outfit_suggestion             │
    │               │                                                    │
    └─► create_fit_card(outfit=outfit_suggestion, new_item=selected_item)│
            │                                                            │
            ├── outfit == "" → error string (no LLM call) ──────────────┤
            │                                                            │
            └── fit_card = "thrifted this tee for $19..."               │
                    │                                                    │
            session["fit_card"] = fit_card                              │
                    │                                                    │
                    ▼                                                    ▼
            Return session (success)                    Return session (session["error"] set)
```

---

## AI Tool Plan

**Milestone 3 — Individual tool implementations:**

For `search_listings`: Give Antigravity the Tool 1 spec block from this planning.md (what it does, exact input params, return value, failure mode). Ask it to implement the function in tools.py using `load_listings()` from utils/data_loader.py. Verify the generated code: (1) filters by all three parameters, (2) handles size=None correctly, (3) returns [] not exception when no match, (4) sorts by price ascending.

For `suggest_outfit`: Give Antigravity the Tool 2 spec block. Ask it to implement using Groq llama-3.3-70b-versatile with GROQ_API_KEY from .env. Verify: (1) prompt includes both new_item fields and wardrobe items list, (2) empty wardrobe triggers different prompt not crash, (3) returns a non-empty string.

For `create_fit_card`: Give Antigravity the Tool 3 spec block. Ask it to implement with LLM temperature ≥ 0.9. Verify: (1) empty outfit returns error string not exception, (2) running same input 3 times produces 3 different captions.

**Milestone 4 — Planning loop and state management:**

Give Antigravity the Planning Loop section + State Management section + Architecture diagram from this planning.md. Ask it to implement `run_agent()` in agent.py. Verify: (1) session dict initialized with all 5 keys, (2) empty search result triggers early return without calling suggest_outfit, (3) selected_item in session matches what was passed to suggest_outfit (print both to confirm), (4) all three tools run end-to-end on the example query.

---

## A Complete Interaction (Step by Step)

Write out what a full user interaction looks like from start to finish — tool call by tool call. Use a specific example query.

**Example user query:** "I'm looking for a vintage graphic tee under $30. I mostly wear baggy jeans and chunky sneakers. What's out there and how would I style it?"

**Step 1:**
Agent calls `search_listings(description="vintage graphic tee", size=None, max_price=30.0)`.
The tool filters all 40 listings from `listings.json` by keyword match (title/description/style_tags contain "vintage" or "graphic tee") and price ≤ 30. Returns a list of matching items — e.g., `lst_006` (Graphic Tee — 2003 Tour Bootleg Style, $24, depop) and `lst_033` (Vintage Band Tee — Faded Grey, $19, depop). Agent stores `results[0]` as `session["selected_item"]`.

**Step 2:**
Agent calls `suggest_outfit(new_item=session["selected_item"], wardrobe=get_example_wardrobe())`.
The example wardrobe contains baggy straight-leg jeans (w_001), chunky white sneakers (w_007), black combat boots (w_008), etc. The LLM receives the new item info + wardrobe items and returns a styled outfit suggestion string like: "Pair this faded graphic tee with your baggy straight-leg jeans and chunky white sneakers. Tuck the front corner for shape and leave sleeves as-is for that 90s grunge feel." Agent stores this in `session["outfit_suggestion"]`.

**Step 3:**
Agent calls `create_fit_card(outfit=session["outfit_suggestion"], new_item=session["selected_item"])`.
The LLM generates a short, shareable caption: "thrifted this faded band tee off depop for $19 and it was made for my baggy jeans 🖤 90s grunge but make it effortless". Agent stores in `session["fit_card"]`.

**Final output to user:**
User sees three panels:
1. **Search result**: "Vintage Band Tee — Faded Grey — $19 — depop — good condition"
2. **Outfit suggestion**: The full styling advice from step 2
3. **Fit card**: The shareable caption from step 3

**Error path:** If Step 1 returns `[]` (no matches), agent sets `session["error"] = "No listings found for 'vintage graphic tee' under $30. Try raising your budget or using broader keywords like 'graphic tee' or 'band tee'."` and returns immediately — Steps 2 and 3 are never called.