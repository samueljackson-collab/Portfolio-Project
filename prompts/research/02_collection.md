# Research Collection Patterns

A repeatable harvesting workflow ensures that every query, candidate source, and citation is captured with enough context to rebuild the research trail.

## 1. Search Strategy Matrix
Track combinations of keywords, operators, and data sources.

| Theme | Query Syntax | Target Source | Purpose |
|-------|--------------|---------------|---------|
| Landscape overview | `"{topic}" AND (overview OR "state of" OR landscape)` | General search, Wikipedia, encyclopedias | Build baseline context and vocabulary. |
| Market/industry data | `"{topic}" AND (market OR adoption OR vendor) site:analystdomain.com` | Analyst reports, investor decks | Quantitative trend signals. |
| Technical depth | `"{topic}" AND (architecture OR implementation OR "case study") filetype:pdf` | Technical papers, standards bodies | Implementation evidence. |
| Risk/compliance | `"{topic}" AND (risk OR failure OR incident OR compliance)` | Regulators, CERT advisories, legal databases | Threat and control references. |
| Practitioner insights | `"{topic}" AND (lessons learned OR "postmortem" OR pitfalls)` | Engineering blogs, community forums | Anecdotes and counterpoints. |

### Operator Toolkit
- `site:`, `filetype:`, `inurl:`, `intitle:` for precision targeting.
- `-keyword` to eliminate noisy results (e.g., marketing-heavy terms).
- `before:YYYY-MM-DD` / `after:YYYY-MM-DD` to constrain by publish date.
- Use scholarly databases (Google Scholar, IEEE Xplore, ACM DL) for primary studies.
- Query structured data platforms (data.gov, statista, Kaggle) when metrics are required.

## 2. Harvesting Workflow
1. **Batch queries**: run a prepared list of searches sequentially to avoid context switching.
2. **Capture results**: log top findings with metadata, evidence grade, and access notes into a spreadsheet or research database.
3. **Deduplicate**: compare titles and canonical URLs. Use a hash of title+author+year to suppress duplicates automatically.
4. **Version tracking**: note the retrieval date and version ID (for standards, policies, or vendor docs).
5. **Citation capture**: immediately record bibliographic details (APA/Chicago format) and archive the page (via PDF or Wayback) when feasible.

## 3. Research Notebook Structure
Maintain a structured notebook (Notion, Obsidian, Markdown repo) with consistent headings:
- **Topic overview**: question, scope, definitions.
- **Search log**: queries executed, filters applied, notes.
- **Source table**: status (Queued, Reviewing, Excerpted, Synthesized), evidence grade, key takeaways.
- **Claim tracker**: statements needing support mapped to source IDs.
- **Open issues**: unanswered questions, blockers, decisions pending.

## 4. Automation Hooks
- Use browser extensions or scripts to export search results to CSV/Markdown.
- Apply tagging for source type and theme to accelerate synthesis.
- Integrate with citation managers (Zotero, Zotero Connector, JabRef) for consistent formatting.
- Store raw artifacts (PDF, transcript, dataset) in an organized folder structure named `YYYY-MM-DD_source-title_slug`.

---

## Duplicate Suppression Protocol
1. Normalize titles by lowercasing, stripping punctuation, and removing stop words.
2. Normalize authors (Last, First) and publication years.
3. Create a deterministic ID: `sha1(normalized_title + normalized_author + year)`.
4. Check the ID before adding a new record; log duplicates with a reference to the existing entry.
5. When duplicates diverge (e.g., updated versions), keep the latest but link to prior versions in notes.

---

## Citation Capture Checklist
- [ ] Title, author(s), publication, publication date.
- [ ] URL or DOI + date accessed.
- [ ] Source type and evidence grade.
- [ ] Summary of relevance (1–2 sentences).
- [ ] Direct quotations with timestamps/page numbers if used.
- [ ] Stored local copy or archive link.

Consistent capture guarantees reproducibility and smooth transition from collection to analysis.
