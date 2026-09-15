# M-T723-V1 — Reconciliation handoff

Branch: `audit/m-t723-v1-approved` (approved isolated branch; no merge, no release performed).
Authority order applied: **literal > appendix (legible + explicit only) > corpus**.
Corpus paraphrases were allowed to back category/scope but never to create exclusions.
A condition of application, ambiguity, or illegible text was never converted into an exclusion.
`registry/stale_registry.jsonl` was kept untouched for lineage and never used as authority.

## Final category totals (computed from generated rules)

24 canonical rules / 24 funders / 19 categories — 23 rules with eligibility authority,
1 undetermined (Prairie Wellness).

| Category | Rules | Funders |
|---|---|---|
| health | 2 | Aster Health, Prairie Wellness* |
| climate | 1 | Beacon Climate |
| arts | 1 | Cedar Arts |
| food | 2 | Delta Food, Verdant Agriculture |
| justice | 1 | Ember Justice |
| education | 1 | Fjord Education |
| housing | 1 | Grove Housing |
| environment | 2 | Harbor Oceans, Tandem Trees |
| youth | 1 | Indigo Youth |
| rural | 1 | Juniper Rural |
| science | 1 | Kestrel Science |
| transport | 1 | Lumen Mobility |
| water | 1 | Mesa Water |
| equity | 1 | Northstar Equity |
| culture | 2 | Orchid Culture, Umber Heritage |
| workforce | 1 | Quarry Workforce |
| technology | 1 | River Tech |
| humanitarian | 2 | Solace Refuge, Zephyr Disaster |
| disability | 1 | Willow Disability |

*Prairie Wellness: category is corpus-only and provisional; no eligibility authority.

## Per-funder decisions

| Funder | Decision | Exclusions kept | Conditions / priorities | Rejected / corrected | Provenance |
|---|---|---|---|---|---|
| Aster Health | Registered charities running community clinics, US+CA | Individuals (A01) | — | Registry region US→US,CA; corpus exclusion kept only because A01 states it | L01, A01, C01 |
| Beacon Climate | Nonprofit-led climate adaptation, worldwide; fiscal sponsor accepted | — | — | Category environment→climate (C02; stale registry not authority) | L02, A02, C02 |
| Cedar Arts | Public schools + charitable arts orgs, US-NE | — | Schools must name charitable fiscal agent (A03) | C03 "schools ineligible" rejected (contradicts L03); region US→US-NE | L03, A03, C03 |
| Delta Food | US nonprofit food security | — | Local partners required only for multi-state work (L04, A04) | C04 vague "may require" narrowed | L04, A04, C04 |
| Ember Justice | Nonprofit civil-rights litigation AND legal advocacy, global | — | Advocacy eligible when tied to litigation strategy (A05) | Stale "litigation only" corrected; C05 ambiguity resolved | L05, A05, C05 |
| Fjord Education | US-MW school districts + nonprofits, STEM teacher initiatives | — | Priority: rural districts (A06) | Priority kept as priority, not exclusion | L06, A06, C06 |
| Grove Housing | US-W nonprofit preservation | New construction (L07, literal) | Emergency repair case-by-case (A07) | — | L07, A07, C07 |
| Harbor Oceans | Marine-conservation nonprofits, no geographic restriction | — | Inland watershed applicants considered with marine-impact evidence (A08); coastal = priority | C08 "coastal-only" rejected; stale Coastal restriction removed (L08) | L08, A08, C08 |
| Indigo Youth | US nonprofit youth development | Individual awards (L09); scholarships out of scope (A09) | — | C09 ambiguity resolved by L09/A09 | L09, A09, C09 |
| Juniper Rural | Rural-serving US charitable orgs; fiscal sponsors welcome | — | 501(c)(3) preferred, not required (A10) | Stale "501c3 required" + C10 paraphrase rejected | L10, A10, C10 |
| Kestrel Science | Universities + nonprofit operators, global, open science infrastructure | — | Open licensing required for software outputs (A11) | C11 "possibly eligible" confirmed by L11 | L11, A11, C11 |
| Lumen Mobility | EU nonprofit safe-mobility pilots incl. policy implementation | — | Municipal partners may participate; applicant nonprofit (A12) | C12 "excludes policy" rejected (L12 includes it) | L12, A12, C12 |
| Mesa Water | US-SW watershed-restoration nonprofits; fiscal sponsor may apply | — | — | C13 "fiscal sponsor required" rejected (A13 = may apply); stale field corrected | L13, A13, C13 |
| Northstar Equity | US nonprofits advancing economic mobility | Direct startup investments only (L14, narrow) | — | C14 broad "startup exclusion" narrowed; A14 PRI note = not eligibility guidance | L14, A14, C14 |
| Orchid Culture | Cultural-heritage nonprofits, worldwide | — | Digitization = review priority, not requirement (L15, A15) | Stale "digitization" criterion corrected | L15, A15, C15 |
| Prairie Wellness | **Undetermined** — no eligibility rule | — | — | L16 illegible, A16 illegible, C16 garbled → open conflict | L16, A16, C16 |
| Quarry Workforce | US nonprofit worker-transition programs | — | Union partnership welcome, not required (L17, A17) | Stale "union partner required" corrected | L17, A17, C17 |
| River Tech | Global public-interest tech by nonprofits | — | Open-source release encouraged; exceptions need approval (A18) | Stale "open source required" corrected to condition | L18, A18, C18 |
| Solace Refuge | MENA nonprofit displacement response | — | Declared-emergency requests expedited (A19, process note) | — | L19, A19, C19 |
| Tandem Trees | US nonprofit urban-forestry maintenance | — | Planting-only = lower priority, not excluded (A20) | — | L20, A20, C20 |
| Umber Heritage | US-SE charitable historic preservation **including capital/stabilization** | — | — | **Contradiction resolved**: stale "capital excluded" vs L21 "including capital preservation work" — literal wins | L21, A21, C21 |
| Verdant Agriculture | Regenerative-agriculture nonprofits, worldwide | — | For-profit pilots require nonprofit lead applicant (A22) | C22 ambiguity resolved | L22, A22, C22 |
| Willow Disability | US nonprofit disability justice + accessible design (incl. digital, A23) | — | — | — | L23, A23, C23 |
| Zephyr Disaster | APAC nonprofit disaster preparedness; response funding | — | Response activates only after declared emergency (A24; duplicate A24D collapsed) | — | L24, A24/A24D, C24 |

## Synthetic examples (examples/synthetic_applicants.json, hand-traced + encoded as tests)

| Applicant | Result |
|---|---|
| Canadian clinic (charity, CA, health) | Aster Health: **eligible** (registry-region correction validated) |
| NE public school (public_school, US-NE, arts) | Cedar Arts: **eligible_with_conditions** (charitable fiscal agent per A03) |
| Inland watershed group (nonprofit, US-MW, environment) | Harbor Oceans: **eligible_with_conditions** (marine-impact evidence); Tandem Trees: eligible |
| APAC emergency NGO (declared_emergency=true) | Zephyr Disaster: **eligible**, response track open; Solace Refuge: ineligible (MENA) |
| APAC preparedness NGO (declared_emergency=false) | Zephyr Disaster: **eligible** (preparedness), response track blocked |
| Startup farm pilot (for_profit, Global, food) | Verdant Agriculture: **conditional** (needs nonprofit lead); Delta Food: ineligible (US-only) |
| Fiscal-sponsor rural group (fiscal_sponsor, US-S, rural) | Juniper Rural: **eligible** (501(c)(3) not required) |
| Unionless workforce nonprofit (nonprofit, US, workforce) | Quarry Workforce: **eligible** (union not required) |

## Validation

- `src/generate_rules.py` validates before generating: every provenance row ID exists in the
  raw evidence; appendix provenance must be `legible=true` for eligibility-affecting rules;
  no exclusion may be corpus-sourced; eligibility-affecting rules must have literal provenance;
  rejected paraphrases must reference real corpus rows. `--check` mode verifies committed
  outputs match regeneration (determinism).
- `tests/test_matcher.py` covers: provenance completeness, no corpus-sourced exclusions,
  appendix legibility, generator reproducibility, the authority gate (Prairie Wellness),
  all six resolved contradictions, the three condition types, and region behaviour
  (CA acceptance, EU rejection, MENA restriction, inland-not-excluded, US-* hierarchy).
- Tests were written and hand-traced against the matcher logic in this environment; run with
  `python -m pytest tests/` or `python -m unittest discover tests` (stdlib only).

## Open conflicts / caveats

1. **Prairie Wellness** — no legible authoritative evidence; eligibility undetermined.
2. **Category provenance** — `cat` exists only in corpus rows; categories are the lowest-
   authority field everywhere (used for grouping, never for exclusions).
3. **Region hierarchy** — matcher treats `US-MW` as inside `US`; `CA` is not inside `US`
   (Aster lists CA explicitly). Documented convention.
4. **Type aliases** — `charity`/`charitable` normalized; `charity` is not auto-equated with
   `nonprofit` (kept distinct per literal wording).
5. **A14 (Northstar)** — program-related investments are review-process notes, recorded as
   such, not eligibility rules.

## Branch / release state

- All work committed on `audit/m-t723-v1-approved` only. `main` untouched.
- No PR opened, no merge, no tag/release — per INSTRUCTIONS.md.
- `registry/stale_registry.jsonl` preserved verbatim for lineage; corrections live in
  `registry/reconciled_registry.jsonl`.
