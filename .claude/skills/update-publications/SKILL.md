---
name: update-publications
description: Add the lab's newest papers to the website. Use when asked to update, sync, or add publications, or to check Flavio Calmon's Google Scholar for new papers. Finds papers on Scholar that are missing from publications.json, verifies their metadata on arXiv or the publisher's page, and adds them in the site's format.
---

# Updating publications from Google Scholar

The publication list on `research.html` is rendered from `publications.json`. New papers come from Flavio Calmon's Google Scholar profile, sorted by date:
https://scholar.google.com/citations?hl=en&user=P8N_YH4AAAAJ&view_op=list_works&sortby=pubdate

Scholar is the list of what exists, but its metadata is not reliable enough to publish as is: it truncates author lists ("..."), abbreviates names to initials, drops math symbols from titles ("Best-of-" for "Best-of-n"), and dates conference papers by the proceedings year. Take titles and authors from arXiv or the publisher instead.

## 1. Find the candidates

From the repository root:

```bash
python3 .claude/skills/update-publications/find_new_papers.py --since 2025
```

This fetches the Scholar list, drops every paper whose title already appears in `publications.json`, and looks each remaining paper up on arXiv, by ID when Scholar shows one and by title otherwise. It prints JSON and changes nothing. If Scholar returns no rows, it is rate-limiting you; wait and retry. Do not switch to a summarizing web fetch, which loses author lists.

## 2. Decide what to add

Go through the candidates one by one:

- **Duplicates within Scholar.** Scholar often lists the same paper twice, for example the arXiv version and the conference version, or two title variants with the same arXiv ID. Add one entry per paper.
- **Near-matches.** A candidate can be a paper that is already in the file under a different title, such as an arXiv title that changed at publication. Before adding it, search `publications.json` for its arXiv ID and distinctive title words.
- **Skip non-papers** such as editorials, special-issue introductions, and theses, unless the user asks for them.
- **No arXiv match** (`"arxiv": null`). Open the paper's Scholar detail page (`view_op=view_citation&citation_for_view=<scholar_id>`). It gives the full author names, the venue, and a publisher link. Use the Scholar author list only if it isn't truncated.

When unsure whether something should be added, list it for the user instead of guessing.

## 3. Write each entry

Add new entries at the top of `publications.json`, newest first. Edit the file as text and leave existing entries alone, so the diff shows only additions. Validate with `python3 -c "import json; json.load(open('publications.json'))"` afterwards.

```json
{
    "id": "cs61",
    "title": "Title as on arXiv, with LaTeX removed ($f$-divergence -> f-divergence)",
    "authors": "Full Name, Full Name, Flavio du Pin Calmon",
    "venue": "Full venue name (ACRONYM)",
    "year": 2026,
    "type": "conference",
    "category": ["Privacy", "Machine Learning"],
    "keywords": "three, short, keywords",
    "tldr": null,
    "abstract": "Abstract from arXiv, or null",
    "pub_website": "Publisher or proceedings URL, or null",
    "arxiv_website": "https://arxiv.org/abs/XXXX.XXXXX",
    "code_repository": null,
    "bibtex": null
}
```

- **`id`:** a prefix plus the next unused number: `cs`/`c` for conference papers (new ones use `cs`), `j` for journals, `pre` for preprints, and `p` for patents. Check the current maximum before assigning; ids must be unique.
- **`authors`:** full names, comma-separated, exactly as the paper lists them. Lab members must use the canonical spelling in `authors.json` (`"lab"` values), such as "Flavio du Pin Calmon" or "Carol Long", so they render in bold. A lab member missing from `authors.json` (check `people.json`, including alumni and visitors) must be added under `"lab"`. Be careful with shared surnames: an external co-author can share a lab member's surname (e.g. Andre P. Calmon, Fernando Diaz), so match on first name as well.
- **`venue`:** spell the full name out with the acronym in parentheses, following the existing entries, e.g. "International Conference on Machine Learning (ICML)" or "IEEE Transactions on Information Theory". For preprints use "arXiv preprint" with `"type": "preprint"`.
- **`year`:** for conference papers, the year of the conference, not the proceedings year Scholar reports (NeurIPS 2025 papers are 2025). For preprints, the arXiv submission year.
- **`award`** (optional): oral, spotlight, or best-paper status, when the arXiv comment or venue says so, e.g. `"award": "Oral Presentation"`.
- **`category`:** one or more of the existing filters on the Research page: Fairness, Information Theory, Interpretability, Large Language Models, Machine Learning, Privacy. Reuse these rather than inventing new ones.

The arXiv `comment` field often states the venue ("Accepted at ISIT 2025", "NeurIPS'25 position papers track"). Use it to set the venue instead of leaving an accepted paper as a preprint.

## 4. Check and report

1. Open `research.html` with the dev server running (`npx live-server --port=8080`). Confirm that the new papers appear at the top, lab members are bold, and the links work.
2. Tell the user:
   - what you added
   - what you skipped, and why
   - anything you were unsure about, such as a possible lab member you couldn't confirm, a venue you inferred, or a paper with no arXiv or publisher link

Do not commit unless asked.

If a new paper should be featured on the home page, its id goes in `publication-config.json` under `theory`, `aiml`, or `applications`. Only do this when the user asks.
