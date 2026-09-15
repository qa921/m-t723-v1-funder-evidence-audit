# M-T723-V1 — Evidence inventory (audited 2026-09-15)

Scope: Dropbox `/M-T723-V1-funder-evidence-audit/` mirrored under `evidence/` in this repo
(identical byte sizes: corpus 3294 B, literal 3345 B, appendix 2860 B, source_index 347 B).
All counts below are computed from the actual rows — **not** from `evidence/source_index.json`,
which is a stale intake index and was not trusted.

## Real counts vs source index

| Metric | Real (audited) | Index claim | Delta | Notes |
|---|---|---|---|---|
| Corpus rows | 24 (C01–C24) | 23 | **+1** | One row per funder; paraphrase/secondary-summary level only |
| Literal rows | 24 (L01–L24) | 22 | **+2** | Each row carries a page citation (p1–p14) |
| Appendix rows | 25 (A01–A24, A24D) | 26 | **−1** | A24D is an exact duplicate of A24 |
| Citations | 24 | 61 | **−37** | Only literal rows carry `cite`; corpus/appendix rows have none |
| Distinct funders | 24 | 20 | **+4** | Identical 24-funder set across all three sources |
| Categories (from corpus) | 19 distinct | — | n/a | Index has no category count |

## Per-source inventory

### corpus/retrieved_corpus.jsonl (lowest authority)
- 24 rows, ids C01–C24, fields: id, f, cat, regions, text.
- Content is retrieved summaries/paraphrases ("paraphrase says…", "secondary snippet says…",
  "likely…", "possibly…", "unclear…"). Several embed exclusion-like claims that are
  **not** supported by higher-authority sources (C03, C08, C12, C13, C14 narrowed by L14).
- C16 (Prairie Wellness) is partly garbled.

### literal/literal_register.jsonl (highest authority)
- 24 rows, ids L01–L24, fields: id, f, quote, cite (p1–p14).
- Direct funder quotes. L16 (Prairie Wellness): `[scan unreadable after: eligible community
  mental health...]` — illegible, unusable for eligibility rules.

### appendix/appendix_extracts.jsonl (middle authority, only if legible and explicit)
- 25 rows, ids A01–A24 plus duplicate A24D, fields: id, f, text, legible.
- A16 (Prairie Wellness): `legible=false` — excluded from authority.
- A24D duplicates A24 verbatim. Both rows retained in the source (per instructions, duplicates
  were not discarded); the duplicate is collapsed only in generated outputs.
- Content is mostly conditions/priorities/process notes, not exclusions.

## Consequences
- Source-index totals are wrong on every claimed metric; nothing was taken from the index.
- Prairie Wellness has no legible authoritative source (L16 unreadable, A16 illegible,
  C16 garbled) → no eligibility-affecting rule generated; tracked as an open conflict.
- Duplicates preserved at source level; deduplication happens only in generated artifacts.
