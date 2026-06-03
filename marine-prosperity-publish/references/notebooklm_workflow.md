# NotebookLM Workflow — Step-by-Step

End-to-end example of publishing one MPpI policy brief and generating an infographic.

## Prerequisites

- Brief exists at `policy_briefs/policy_brief_<slug>.md`
- NotebookLM MCP server connected (tools `mcp__notebooklm-mcp__*` visible)
- User has authenticated within the last few hours

If you see `Authentication expired`, ask the user to run:

```
! notebooklm-mcp-auth
```

The `!` prefix runs the command inside the Claude Code session so the browser auth-flow output returns to context. Use `save_auth_tokens` only as a fallback (it requires manually pasted tokens).

## Step 1 — Choose strategy

Ask the user:

> Will this brief be its own notebook, or should I add it to an existing region notebook?

If region notebook, list existing notebooks first:

```python
mcp__notebooklm-mcp__notebook_list(max_results=50)
```

Identify the target notebook by title (e.g. `Marine Prosperity Index — Gulf of California Briefs (2026)`).

## Step 2 — Create or open notebook

```python
nb = mcp__notebooklm-mcp__notebook_create(
    title="Marine Prosperity Index — Bahía de Kino Policy Brief"
)
notebook_id = nb["notebook_id"]   # confirm exact key from response
```

## Step 3 — Add brief as source

```python
with open("policy_briefs/policy_brief_bahia_de_kino.md") as f:
    md = f.read()

src = mcp__notebooklm-mcp__notebook_add_text(
    notebook_id=notebook_id,
    title="Policy Brief — Bahía de Kino",
    text=md,
)
source_id = src["source_id"]
```

For DOCX content, prefer pasting the underlying markdown — NotebookLM's chunker handles markdown headings more reliably than DOCX structure for infographic extraction.

## Step 4 — Confirm with user, then generate

Ask:

> Generate the infographic now? (NotebookLM charges per generation; this will create one landscape infographic.)

On approval:

```python
mcp__notebooklm-mcp__infographic_create(
    notebook_id=notebook_id,
    source_ids=[source_id],
    orientation="landscape",
    detail_level="standard",
    language="en",
    focus_prompt=(
        "Frame this as a Marine Prosperity Index brief. Center the infographic on: "
        "Balance (evenness across axes), Level (overall performance), and Prosperity "
        "Pp = Balance × Level. Show the three axes (Nature, Livelihood, Well-being) "
        "with their scores vs national averages. Call out the binding constraint "
        "(limiting axis) and present the four policy scenarios with their Balance "
        "deltas. Use the prosperity category as the headline classification."
    ),
    confirm=True,
)
```

## Step 5 — Poll until ready

```python
import time
while True:
    s = mcp__notebooklm-mcp__studio_status(notebook_id=notebook_id)
    items = s.get("items", [])
    statuses = [it.get("status") for it in items]
    if all(st in ("ready", "failed") for st in statuses):
        break
    print("…still processing:", statuses)
    time.sleep(20)
```

In Claude Code, prefer waiting via Monitor + an until-loop rather than tight `sleep` polling. Most infographics complete in 60–180 s.

## Step 6 — Surface URLs

```python
for it in s["items"]:
    print(f"{it['type']}: {it.get('url')}  [{it['status']}]")
```

Report the notebook URL and per-artifact URLs back to the user.

## Step 7 — Optional follow-ups

After the infographic, the user often also wants:

- **Audio overview (podcast)** — `audio_overview_create(notebook_id=..., confirm=True, focus_prompt="Frame for coastal policymakers; 7-minute brief")`
- **Mind map** — `mind_map_create(notebook_id=..., confirm=True)` — useful for showing the three-axis structure
- **Slide deck** — `slide_deck_create(notebook_id=..., confirm=True)` — for stakeholder webinars

Each requires `confirm=True` after explicit user authorization.

## Regional cohort workflow

For multiple briefs in one notebook:

```python
nb = mcp__notebooklm-mcp__notebook_create(
    title="Marine Prosperity Index — Gulf of California Briefs (2026)"
)
notebook_id = nb["notebook_id"]

source_ids = []
for slug in ["alto_golfo", "bahia_de_los_angeles", "bahia_de_kino",
             "el_manglito", "la_manga", "la_reforma", "la_ribera",
             "punta_chueca", "san_basilio", "san_carlos", "bahia_de_banderas"]:
    md = open(f"policy_briefs/policy_brief_{slug}.md").read()
    name = slug.replace("_", " ").title()
    src = mcp__notebooklm-mcp__notebook_add_text(
        notebook_id=notebook_id,
        title=f"Policy Brief — {name}",
        text=md,
    )
    source_ids.append(src["source_id"])

# Synthesis infographic across all sources
mcp__notebooklm-mcp__infographic_create(
    notebook_id=notebook_id,
    source_ids=source_ids,
    orientation="landscape",
    detail_level="detailed",
    focus_prompt=(
        "Cross-compare the Gulf of California communities. Show each one's "
        "prosperity category, limiting axis, and Pp value. Group by category "
        "(Balanced Prosperity / Balanced but Developing / Imbalanced Growth / "
        "Lagging). Highlight the regional pattern: how many communities are "
        "Nature-limited vs Livelihood-limited."
    ),
    confirm=True,
)
```
