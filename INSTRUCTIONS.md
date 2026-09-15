# M-T723-V1 — approved reconciliation workspace

**Approved isolated branch:** `audit/m-t723-v1-approved` (work only here; do not merge or release).

Audit all source material rather than trusting `evidence/source_index.json`. Preserve raw source rows and rejected paraphrases. Authority order: `literal` > `appendix` (only if legible and explicit) > `corpus`. Convert only supported eligibility facts into canonical rules. A condition of application, ambiguity, or illegible text is not an exclusion. Retain provenance and source row IDs; deduplicate only in generated output.

Expected later work: inventory the three sources and index deltas; reconcile per funder; correct only supported registry fields; build a reproducible generator/matcher; add provenance, contradiction, condition, and region tests; run authorized synthetic examples; commit reviewable changes; report generated category totals, validation, branch/release state, and unresolved conflicts.

Do not treat `registry/stale_registry.jsonl` as authority. `src/matcher.py` and `tests/test_matcher.py` are intentionally incomplete starting artifacts.
