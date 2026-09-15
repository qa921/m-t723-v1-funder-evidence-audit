#!/usr/bin/env python3
"""Regenerate M-T723-V1 canonical rules from raw evidence (deterministic).

Authority order (INSTRUCTIONS.md): literal > appendix (legible + explicit only)
> corpus. Corpus paraphrases may back category/scope but never create
exclusions. A condition, an ambiguity, or illegible text is not an exclusion.
Source files are never modified; deduplication happens only in generated
output. The stale registry is never read.

Usage:
    python src/generate_rules.py          # regenerate outputs
    python src/generate_rules.py --check  # verify committed outputs, no writes
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EVIDENCE = ROOT / "evidence"
CORPUS_PATH = EVIDENCE / "corpus" / "retrieved_corpus.jsonl"
LITERAL_PATH = EVIDENCE / "literal" / "literal_register.jsonl"
APPENDIX_PATH = EVIDENCE / "appendix" / "appendix_extracts.jsonl"
INDEX_PATH = EVIDENCE / "source_index.json"

RULES_OUT = ROOT / "rules" / "canonical_rules.jsonl"
REGISTRY_OUT = ROOT / "registry" / "reconciled_registry.jsonl"
TOTALS_OUT = ROOT / "docs" / "category_totals.json"
INVENTORY_OUT = ROOT / "docs" / "inventory_report.json"


def load_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def load_evidence():
    return load_jsonl(CORPUS_PATH), load_jsonl(LITERAL_PATH), load_jsonl(APPENDIX_PATH)


# Curated per-funder reconciliation decisions. Each rule cites the exact
# evidence rows it derives from; validate() re-checks every citation against
# the raw sources on each run. Exclusions require literal or legible-appendix
# authority. regions=[] means unrestricted (funder states worldwide/global,
# or a stated priority that is explicitly not a restriction).
DECISIONS = [
    {"funder": "Aster Health", "category": "health", "regions": ["US", "CA"], "eligible_types": ["charity"], "scope": "community clinics", "exclusions": [{"kind": "applicant_type", "value": "individual", "applies_to": "applicant", "source": ["A01"]}], "conditions": [], "priorities": [], "eligibility_authority": True, "provenance": {"literal": ["L01"], "appendix": ["A01"], "corpus": ["C01"]}, "rejected_paraphrases": [], "notes": "Registry regions corrected US -> US,CA per L01; corpus individual-exclusion paraphrase retained only because legible A01 states it."},
    {"funder": "Beacon Climate", "category": "climate", "regions": [], "eligible_types": ["nonprofit", "fiscal_sponsor"], "scope": "climate adaptation", "exclusions": [], "conditions": [], "priorities": [], "eligibility_authority": True, "provenance": {"literal": ["L02"], "appendix": ["A02"], "corpus": ["C02"]}, "rejected_paraphrases": [], "notes": "Category corrected environment -> climate per C02 (stale registry is not authority); A02: fiscal sponsor accepted for unincorporated groups; worldwide."},
    {"funder": "Cedar Arts", "category": "arts", "regions": ["US-NE"], "eligible_types": ["public_school", "charity"], "scope": "arts education / charitable arts organizations (New England)", "exclusions": [], "conditions": [{"key": "fiscal_agent_for_schools", "description": "School applications must name a charitable fiscal agent.", "source": ["A03"], "effect": "requires_review"}], "priorities": [], "eligibility_authority": True, "provenance": {"literal": ["L03"], "appendix": ["A03"], "corpus": ["C03"]}, "rejected_paraphrases": [{"source": "C03", "claim": "schools are ineligible", "reason": "Contradicted by L03 (eligible applicants include public schools); corpus paraphrase is not authority."}], "notes": "Registry region US -> US-NE per L03."},
    {"funder": "Delta Food", "category": "food", "regions": ["US"], "eligible_types": ["nonprofit"], "scope": "food security", "exclusions": [], "conditions": [{"key": "local_partner_multi_state", "description": "Local implementation partners are required only for multi-state work.", "source": ["L04", "A04"], "effect": "requires_review"}], "priorities": [], "eligibility_authority": True, "provenance": {"literal": ["L04"], "appendix": ["A04"], "corpus": ["C04"]}, "rejected_paraphrases": [], "notes": "C04 vague partner paraphrase narrowed to multi-state work by L04/A04."},
    {"funder": "Ember Justice", "category": "justice", "regions": [], "eligible_types": ["nonprofit"], "scope": "civil-rights litigation and legal advocacy", "exclusions": [], "conditions": [{"key": "advocacy_litigation_link", "description": "Advocacy is eligible when connected to litigation strategy.", "source": ["A05"], "effect": "requires_review"}], "priorities": [], "eligibility_authority": True, "provenance": {"literal": ["L05"], "appendix": ["A05"], "corpus": ["C05"]}, "rejected_paraphrases": [], "notes": "Stale registry 'litigation only' corrected: L05 includes legal advocacy; C05 ambiguity resolved."},
    {"funder": "Fjord Education", "category": "education", "regions": ["US-MW"], "eligible_types": ["school_district", "nonprofit"], "scope": "STEM teacher initiatives", "exclusions": [], "conditions": [], "priorities": [{"description": "Priority: rural districts.", "source": ["A06"]}], "eligibility_authority": True, "provenance": {"literal": ["L06"], "appendix": ["A06"], "corpus": ["C06"]}, "rejected_paraphrases": [], "notes": "A06 is a priority, not an exclusion; stale 'districts' only broadened per L06 (districts and nonprofits)."},
    {"funder": "Grove Housing", "category": "housing", "regions": ["US-W"], "eligible_types": ["nonprofit"], "scope": "affordable housing preservation", "exclusions": [{"kind": "project_type", "value": "new_construction", "applies_to": "project", "source": ["L07"]}], "conditions": [{"key": "emergency_repair_case_by_case", "description": "Emergency repair may be considered case by case.", "source": ["A07"], "effect": "requires_review"}], "priorities": [], "eligibility_authority": True, "provenance": {"literal": ["L07"], "appendix": ["A07"], "corpus": ["C07"]}, "rejected_paraphrases": [], "notes": "New-construction exclusion is literal (L07) and retained."},
    {"funder": "Harbor Oceans", "category": "environment", "regions": [], "eligible_types": ["nonprofit"], "scope": "marine conservation", "exclusions": [], "conditions": [{"key": "marine_impact_evidence", "description": "Inland watershed applicants may be considered with marine impact evidence.", "source": ["A08"], "effect": "requires_review"}], "priorities": [{"description": "Coastal communities are a priority, not a geographic restriction.", "source": ["L08"]}], "eligibility_authority": True, "provenance": {"literal": ["L08"], "appendix": ["A08"], "corpus": ["C08"]}, "rejected_paraphrases": [{"source": "C08", "claim": "coastal-only", "reason": "L08 states coastal is a priority, not a restriction."}], "notes": "Stale registry Coastal restriction removed per L08."},
    {"funder": "Indigo Youth", "category": "youth", "regions": ["US"], "eligible_types": ["nonprofit"], "scope": "youth development", "exclusions": [{"kind": "applicant_type", "value": "individual", "applies_to": "applicant", "source": ["L09"]}, {"kind": "award_type", "value": "scholarship", "applies_to": "project", "source": ["A09"]}], "conditions": [], "priorities": [], "eligibility_authority": True, "provenance": {"literal": ["L09"], "appendix": ["A09"], "corpus": ["C09"]}, "rejected_paraphrases": [], "notes": "C09 scholarship ambiguity resolved: no individual awards (L09), scholarships out of scope (A09); youth-led nonprofits eligible."},
    {"funder": "Juniper Rural", "category": "rural", "regions": ["US-S"], "eligible_types": ["charity", "nonprofit", "fiscal_sponsor"], "scope": "rural-serving organizations", "exclusions": [], "conditions": [], "priorities": [{"description": "501(c)(3) status is preferred, not required for fiscal-sponsor applicants.", "source": ["A10"]}], "eligibility_authority": True, "provenance": {"literal": ["L10"], "appendix": ["A10"], "corpus": ["C10"]}, "rejected_paraphrases": [{"source": "C10", "claim": "501(c)(3) required", "reason": "A10 states preferred, not required; corpus summary is not authority."}], "notes": "Stale registry 501c3 requirement corrected per A10."},
    {"funder": "Kestrel Science", "category": "science", "regions": [], "eligible_types": ["university", "nonprofit"], "scope": "open science infrastructure", "exclusions": [], "conditions": [{"key": "open_licensing_software", "description": "Open licensing is required for software outputs.", "source": ["A11"], "effect": "requires_review"}], "priorities": [], "eligibility_authority": True, "provenance": {"literal": ["L11"], "appendix": ["A11"], "corpus": ["C11"]}, "rejected_paraphrases": [], "notes": "C11 'universities possibly eligible' confirmed by L11."},
    {"funder": "Lumen Mobility", "category": "transport", "regions": ["EU"], "eligible_types": ["nonprofit"], "scope": "safe-mobility pilots, including policy implementation", "exclusions": [], "conditions": [{"key": "municipal_partner_participation", "description": "Municipal partners may participate; the applicant must be nonprofit.", "source": ["A12"], "effect": "requires_review"}], "priorities": [], "eligibility_authority": True, "provenance": {"literal": ["L12"], "appendix": ["A12"], "corpus": ["C12"]}, "rejected_paraphrases": [{"source": "C12", "claim": "excludes policy", "reason": "L12 explicitly includes policy implementation."}], "notes": ""},
    {"funder": "Mesa Water", "category": "water", "regions": ["US-SW"], "eligible_types": ["nonprofit", "fiscal_sponsor"], "scope": "watershed restoration", "exclusions": [], "conditions": [], "priorities": [], "eligibility_authority": True, "provenance": {"literal": ["L13"], "appendix": ["A13"], "corpus": ["C13"]}, "rejected_paraphrases": [{"source": "C13", "claim": "grants require a fiscal sponsor", "reason": "A13 states a fiscal sponsor MAY apply for community watershed groups; not a requirement."}], "notes": "Stale registry 'fiscal sponsor required' corrected per A13."},
    {"funder": "Northstar Equity", "category": "equity", "regions": ["US"], "eligible_types": ["nonprofit"], "scope": "economic mobility", "exclusions": [{"kind": "instrument", "value": "direct_startup_investment", "applies_to": "project", "source": ["L14"]}], "conditions": [], "priorities": [], "eligibility_authority": True, "provenance": {"literal": ["L14"], "appendix": ["A14"], "corpus": ["C14"]}, "rejected_paraphrases": [], "notes": "C14 broad startup-exclusion paraphrase narrowed to direct startup investments per L14; A14 (PRIs reviewed separately) recorded as non-eligibility note."},
    {"funder": "Orchid Culture", "category": "culture", "regions": [], "eligible_types": ["nonprofit"], "scope": "cultural heritage", "exclusions": [], "conditions": [], "priorities": [{"description": "Digital access / digitization is a review priority, not a requirement.", "source": ["L15", "A15"]}], "eligibility_authority": True, "provenance": {"literal": ["L15"], "appendix": ["A15"], "corpus": ["C15"]}, "rejected_paraphrases": [], "notes": "Stale registry digitization criterion corrected to priority per L15/A15."},
    {"funder": "Prairie Wellness", "category": "health", "regions": ["US-Plains"], "eligible_types": [], "scope": "", "exclusions": [], "conditions": [], "priorities": [], "eligibility_authority": False, "provenance": {"literal": ["L16"], "appendix": ["A16"], "corpus": ["C16"]}, "rejected_paraphrases": [], "notes": "UNRESOLVED: L16 illegible, A16 illegible, C16 partly garbled. Category/region are corpus-only and provisional; no eligibility-affecting rule generated."},
    {"funder": "Quarry Workforce", "category": "workforce", "regions": ["US"], "eligible_types": ["nonprofit"], "scope": "worker transition programs", "exclusions": [], "conditions": [], "priorities": [{"description": "Union partnership strengthens review but is not required.", "source": ["L17", "A17"]}], "eligibility_authority": True, "provenance": {"literal": ["L17"], "appendix": ["A17"], "corpus": ["C17"]}, "rejected_paraphrases": [], "notes": "Stale registry 'union partner required' corrected per L17/A17."},
    {"funder": "River Tech", "category": "technology", "regions": [], "eligible_types": ["nonprofit"], "scope": "public-interest technology", "exclusions": [], "conditions": [{"key": "open_source_release", "description": "Open-source release is encouraged; exceptions need approval.", "source": ["A18"], "effect": "requires_review"}], "priorities": [], "eligibility_authority": True, "provenance": {"literal": ["L18"], "appendix": ["A18"], "corpus": ["C18"]}, "rejected_paraphrases": [], "notes": "Stale registry 'open source required' corrected: A18 makes it conditional, not an exclusion."},
    {"funder": "Solace Refuge", "category": "humanitarian", "regions": ["MENA"], "eligible_types": ["nonprofit"], "scope": "displacement response", "exclusions": [], "conditions": [], "priorities": [{"description": "Declared-emergency response requests may be expedited (process note).", "source": ["A19"]}], "eligibility_authority": True, "provenance": {"literal": ["L19"], "appendix": ["A19"], "corpus": ["C19"]}, "rejected_paraphrases": [], "notes": ""},
    {"funder": "Tandem Trees", "category": "environment", "regions": ["US"], "eligible_types": ["nonprofit"], "scope": "urban forestry maintenance", "exclusions": [], "conditions": [], "priorities": [{"description": "Planting-only proposals are lower priority, not excluded.", "source": ["A20"]}], "eligibility_authority": True, "provenance": {"literal": ["L20"], "appendix": ["A20"], "corpus": ["C20"]}, "rejected_paraphrases": [], "notes": ""},
    {"funder": "Umber Heritage", "category": "culture", "regions": ["US-SE"], "eligible_types": ["charity", "nonprofit"], "scope": "historic preservation, including capital preservation and stabilization work", "exclusions": [], "conditions": [], "priorities": [], "eligibility_authority": True, "provenance": {"literal": ["L21"], "appendix": ["A21"], "corpus": ["C21"]}, "rejected_paraphrases": [], "notes": "CONTRADICTION resolved: stale registry 'capital excluded' vs L21 'including capital preservation work' -- literal wins; capital work eligible."},
    {"funder": "Verdant Agriculture", "category": "food", "regions": [], "eligible_types": ["nonprofit"], "scope": "regenerative agriculture", "exclusions": [], "conditions": [{"key": "nonprofit_lead_for_for_profit", "description": "For-profit pilots require a nonprofit lead applicant.", "source": ["A22"], "effect": "conditional"}], "priorities": [], "eligibility_authority": True, "provenance": {"literal": ["L22"], "appendix": ["A22"], "corpus": ["C22"]}, "rejected_paraphrases": [], "notes": "C22 for-profit ambiguity resolved by A22: allowed only with a nonprofit lead applicant."},
    {"funder": "Willow Disability", "category": "disability", "regions": ["US"], "eligible_types": ["nonprofit"], "scope": "disability justice and accessible design, including digital accessibility", "exclusions": [], "conditions": [], "priorities": [], "eligibility_authority": True, "provenance": {"literal": ["L23"], "appendix": ["A23"], "corpus": ["C23"]}, "rejected_paraphrases": [], "notes": ""},
    {"funder": "Zephyr Disaster", "category": "humanitarian", "regions": ["APAC"], "eligible_types": ["nonprofit"], "scope": "disaster preparedness; response funding", "exclusions": [], "conditions": [{"key": "declared_emergency", "description": "Response funding activates only after a declared emergency.", "source": ["A24", "A24D"], "effect": "limits_scope"}], "priorities": [], "eligibility_authority": True, "provenance": {"literal": ["L24"], "appendix": ["A24", "A24D"], "corpus": ["C24"]}, "rejected_paraphrases": [], "notes": "A24D is an exact duplicate of A24; both retained in source, collapsed into one condition in generated output."},
]


def inventory(corpus, literal, appendix):
    """Real counts from raw rows; never trusts source_index.json."""
    claimed = json.loads(INDEX_PATH.read_text(encoding="utf-8"))["claimed_counts"]
    texts = [a["text"] for a in appendix]
    funders = {r["f"] for r in corpus} | {r["f"] for r in literal} | {r["f"] for r in appendix}
    return {
        "corpus_rows": len(corpus),
        "literal_rows": len(literal),
        "appendix_rows": len(appendix),
        "appendix_duplicate_texts": sorted({t for t in texts if texts.count(t) > 1}),
        "illegible_literal": [r["id"] for r in literal if "unreadable" in r.get("quote", "")],
        "illegible_appendix": [r["id"] for r in appendix if not r.get("legible", False)],
        "citations": sum(1 for r in literal if r.get("cite")),
        "distinct_funders": len(funders),
        "categories_from_corpus": sorted({r["cat"] for r in corpus}),
        "index_claimed": claimed,
        "deltas": {
            "corpus_rows": len(corpus) - claimed["corpus_rows"],
            "literal_rows": len(literal) - claimed["literal_rows"],
            "appendix_rows": len(appendix) - claimed["appendix_rows"],
            "citations": sum(1 for r in literal if r.get("cite")) - claimed["citations"],
            "funders": len(funders) - claimed["funders"],
        },
    }


def validate(decisions, corpus, literal, appendix):
    """Re-check every decision against raw evidence before generating."""
    errors = []
    corpus_ids = {r["id"] for r in corpus}
    literal_ids = {r["id"] for r in literal}
    appendix_by_id = {}
    for row in appendix:  # duplicates collapse here only; source untouched
        appendix_by_id.setdefault(row["id"], row)
    for rule in decisions:
        funder = rule["funder"]
        prov = rule["provenance"]
        for lid in prov.get("literal", []):
            if lid not in literal_ids:
                errors.append("%s: literal row %s not found" % (funder, lid))
        for aid in prov.get("appendix", []):
            row = appendix_by_id.get(aid)
            if row is None:
                errors.append("%s: appendix row %s not found" % (funder, aid))
            elif rule["eligibility_authority"] and not row.get("legible"):
                errors.append("%s: illegible appendix row %s used as authority" % (funder, aid))
        for cid in prov.get("corpus", []):
            if cid not in corpus_ids:
                errors.append("%s: corpus row %s not found" % (funder, cid))
        for rej in rule.get("rejected_paraphrases", []):
            if rej["source"] not in corpus_ids:
                errors.append("%s: rejected paraphrase %s not found" % (funder, rej["source"]))
        for ex in rule.get("exclusions", []):
            sources = ex.get("source", [])
            if any(s.startswith("C") for s in sources):
                errors.append("%s: corpus-sourced exclusion" % funder)
            if not any(s.startswith("L") or s.startswith("A") for s in sources):
                errors.append("%s: exclusion lacks literal/appendix authority" % funder)
        if rule["eligibility_authority"] and not prov.get("literal"):
            errors.append("%s: eligibility-affecting rule without literal authority" % funder)
    return errors


def _registry_row(rule):
    return {
        "f": rule["funder"],
        "cat": rule["category"],
        "regions": rule["regions"] or ["Global"],
        "eligible": ", ".join(rule["eligible_types"]) if rule["eligible_types"] else "undetermined",
        "status": "reconciled" if rule["eligibility_authority"] else "unresolved",
        "provenance": rule["provenance"]["literal"] + rule["provenance"]["appendix"] + rule["provenance"]["corpus"],
    }


def build_outputs(decisions, inv):
    categories = {}
    for rule in decisions:
        categories[rule["category"]] = categories.get(rule["category"], 0) + 1
    totals = {
        "computed_from": "rules/canonical_rules.jsonl",
        "total_rules": len(decisions),
        "total_funders": len({r["funder"] for r in decisions}),
        "eligibility_authority_true": sum(1 for r in decisions if r["eligibility_authority"]),
        "eligibility_authority_false": sum(1 for r in decisions if not r["eligibility_authority"]),
        "categories": dict(sorted(categories.items())),
    }
    return {
        RULES_OUT: "".join(json.dumps(r, sort_keys=True) + "\n" for r in decisions),
        REGISTRY_OUT: "".join(json.dumps(_registry_row(r), sort_keys=True) + "\n" for r in decisions),
        TOTALS_OUT: json.dumps(totals, indent=2, sort_keys=True) + "\n",
        INVENTORY_OUT: json.dumps(inv, indent=2, sort_keys=True) + "\n",
    }


def run(check=False):
    corpus, literal, appendix = load_evidence()
    errors = validate(DECISIONS, corpus, literal, appendix)
    if errors:
        raise SystemExit("validation failed:\n" + "\n".join(errors))
    outputs = build_outputs(DECISIONS, inventory(corpus, literal, appendix))
    drift = []
    for path, text in sorted(outputs.items(), key=lambda kv: str(kv[0])):
        if not path.exists() or path.read_text(encoding="utf-8") != text:
            drift.append(str(path.relative_to(ROOT)))
        if not check:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
    return drift


def main():
    check = "--check" in sys.argv
    drift = run(check=check)
    if check:
        if drift:
            print("STALE generated outputs:", ", ".join(drift))
            sys.exit(1)
        print("OK: committed outputs match regeneration")
    else:
        print("Regenerated %d canonical rules from evidence." % len(DECISIONS))


if __name__ == "__main__":
    main()
