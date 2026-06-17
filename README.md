# FitFindr — Starter Kit

This starter kit contains everything you need to begin Project 2.

## What's Included

```
ai201-project2-fitfindr-starter/
├── data/
│   ├── listings.json          # 40 mock secondhand listings
│   └── wardrobe_schema.json   # Wardrobe format + example wardrobe
├── utils/
│   └── data_loader.py         # Helper functions for loading the data
├── planning.md                # Your planning template — fill this out first
└── requirements.txt           # Python dependencies
```

## Setup

**macOS / Linux:**
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Windows:**
```bash
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
```

Set your Groq API key in a `.env` file (get a free key at [console.groq.com](https://console.groq.com)):
```
GROQ_API_KEY=your_key_here
```

## The Mock Listings Dataset

`data/listings.json` contains 40 mock secondhand listings across categories (tops, bottoms, outerwear, shoes, accessories) and styles (vintage, y2k, grunge, cottagecore, streetwear, and more).

Each listing has: `id`, `title`, `description`, `category`, `style_tags`, `size`, `condition`, `price`, `colors`, `brand`, and `platform`.

Load it with:
```python
from utils.data_loader import load_listings
listings = load_listings()
```

## The Wardrobe Schema

`data/wardrobe_schema.json` defines the format your agent uses to represent a user's existing wardrobe. It includes:

- `schema`: field definitions for a wardrobe item
- `example_wardrobe`: a sample wardrobe with 10 items you can use for testing
- `empty_wardrobe`: a starting template for a new user

Load an example wardrobe with:
```python
from utils.data_loader import get_example_wardrobe
wardrobe = get_example_wardrobe()
```

## Tool Inventory

**`search_listings`**
- **Inputs:** `description` (str), `size` (str), `max_price` (float)
- **Return value:** A list of dictionaries `list[dict]` containing matching items, sorted by relevance score.

**`suggest_outfit`**
- **Inputs:** `new_item` (dict), `wardrobe` (dict)
- **Return value:** A string (`str`) containing the styling advice.

**`create_fit_card`**
- **Inputs:** `outfit` (str), `new_item` (dict)
- **Return value:** A string (`str`) containing a short social media style caption.

---

## Interaction Walkthrough

**User query:** "I'm looking for a vintage graphic tee under $30. I mostly wear baggy jeans and chunky sneakers. What's out there and how would I style it?"

**Step 1 — Tool called:**
- Tool: `search_listings`
- Input: `description="vintage graphic tee"`, `size=None`, `max_price=30.0`
- Why this tool: To find the thrifted item matching the user's budget and description.
- Output: Returns a list of matching items, e.g., `[{"title": "Y2K Baby Tee — Butterfly Print", "price": 18.0, ...}]`

**Step 2 — Tool called:**
- Tool: `suggest_outfit`
- Input: `new_item={"title": "Y2K Baby Tee...", ...}`, `wardrobe={"items": [...]}`
- Why this tool: To provide a complete outfit idea combining the newly found item with the user's existing wardrobe.
- Output: "Pair this faded graphic tee with your baggy straight-leg jeans and chunky white sneakers for a classic 90s grunge feel."

**Step 3 — Tool called:**
- Tool: `create_fit_card`
- Input: `outfit="Pair this faded graphic...", new_item={"title": "Y2K Baby Tee...", ...}`
- Why this tool: To generate an engaging social media post caption for the completed outfit.
- Output: "thrifted this faded band tee off depop for $19 and honestly it was made for my baggy jeans 🖤 90s grunge but make it effortless"

**Final output to user:**
User receives the selected item details, the styling advice, and the generated social media fit card.

---

## Error Handling and Fail Points

| Tool | Failure mode | Agent response |
|------|-------------|----------------|
| `search_listings` | No matching results found for the query | Returns `[]`. The agent detects the empty list, sets `session["error"]` to ask the user to loosen their constraints, and returns early without calling other tools. |
| `suggest_outfit` | Wardrobe is empty (`items = []`) | The LLM prompt falls back to general styling advice without referencing specific pieces. It returns a valid string without throwing an exception. |
| `create_fit_card` | Outfit input is an empty string or None | Returns an error string (e.g., "Error: outfit description is required...") instead of calling the LLM or throwing a Python exception. |

---

## Spec Reflection

**One way planning.md helped during implementation:**
Writing `planning.md` first clearly established the contract for each tool, especially regarding failure modes. Because I had pre-decided that empty searches would return `[]` instead of throwing an error, implementing the state machine in `agent.py` was much simpler as I knew exactly what edge cases to check for.

**One divergence from your spec, and why:**
In our initial planning phase, we assumed `search_listings` should sort results by price ascending. However, during implementation, we realized the actual instructions required us to calculate a relevance score based on keyword matches and sort by that score. So we diverged from our initial plan and changed the logic to sort by relevance score descending to ensure the most accurate item is selected.

---

## Where to Start

1. **Read `planning.md` and fill it out before writing any code.**
2. Verify the data loads correctly by running `python utils/data_loader.py`.
3. Build and test each tool individually before connecting them through your planning loop.

Your implementation files go in this same directory. There's no required file structure for your agent code — organize it however makes sense for your design.
