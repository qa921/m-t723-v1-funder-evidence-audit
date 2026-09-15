"""Canonical grant matcher for M-T723-V1, rebuilt from generated rules.

Reads rules/canonical_rules.jsonl (produced by src/generate_rules.py). The
stale registry and corpus paraphrases are never consulted here, and only
rules with eligibility_authority=True may affect eligibility.

Conventions (documented in docs/RECONCILIATION.md):
- Region codes are hierarchical: applicant "US-MW" is inside funder region
  "US", but "CA" is not inside "US". regions=[] (or "Global") is unrestricted.
- Applicant types are normalized but "charity" is not auto-equated with
  "nonprofit"; rules list exactly what the literal/appendix text supports.
- Project-level exclusions (e.g. new construction, scholarships) are carried
  on the rule as metadata; the matcher only enforces applicant-level facts.
"""
import json
from pathlib import Path

RULES_PATH = Path(__file__).resolve().parent.parent / "rules" / "canonical_rules.jsonl"

ELIGIBLE = "eligible"
ELIGIBLE_WITH_CONDITIONS = "eligible_with_conditions"
CONDITIONAL = "conditional"
INELIGIBLE = "ineligible"
UNDETERMINED = "undetermined"

TYPE_ALIASES = {"charitable": "charity", "non-profit": "nonprofit"}


def load_rules(path=None):
    path = Path(path) if path else RULES_PATH
    with path.open(encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def _canon_type(value):
    value = (value or "").lower()
    return TYPE_ALIASES.get(value, value)


def _region_matches(applicant_region, rule_regions):
    if not rule_regions:
        return True
    for region in rule_regions:
        if region == "Global" or applicant_region == region:
            return True
        if applicant_region.startswith(region + "-"):  # US-MW inside US
            return True
    return False


def match_rule(applicant, rule):
    """Evaluate one applicant against one canonical rule (same category)."""
    result = {
        "funder": rule["funder"],
        "category": rule["category"],
        "status": ELIGIBLE,
        "reasons": [],
        "conditions": [],
        "blocked_tracks": [],
        "provenance": rule.get("provenance", {}),
    }
    if not rule.get("eligibility_authority", False):
        result["status"] = UNDETERMINED
        result["reasons"].append(
            "insufficient authoritative evidence (literal/appendix illegible or missing)")
        return result
    if not _region_matches(applicant.get("region", ""), rule.get("regions", [])):
        result["status"] = INELIGIBLE
        result["reasons"].append(
            "region %r outside %r" % (applicant.get("region"), rule.get("regions")))
        return result
    atype = _canon_type(applicant.get("type"))
    for exclusion in rule.get("exclusions", []):
        if exclusion.get("applies_to") == "applicant" and exclusion.get("value") == atype:
            result["status"] = INELIGIBLE
            result["reasons"].append("excluded applicant type %r (%s)" % (
                atype, ",".join(exclusion.get("source", []))))
            return result
    eligible_types = {_canon_type(t) for t in rule.get("eligible_types", [])}
    if atype not in eligible_types:
        conditional = [c for c in rule.get("conditions", []) if c.get("effect") == "conditional"]
        if conditional:
            result["status"] = CONDITIONAL
            result["conditions"].extend(c["description"] for c in conditional)
            result["reasons"].append(
                "applicant type %r not directly eligible; conditional path exists" % atype)
        else:
            result["status"] = INELIGIBLE
            result["reasons"].append(
                "applicant type %r not in eligible types %r" % (atype, sorted(eligible_types)))
        return result
    review = False
    for cond in rule.get("conditions", []):
        if cond.get("key") == "declared_emergency":
            if applicant.get("declared_emergency") is False:
                result["blocked_tracks"].append("response")
                result["conditions"].append(cond["description"])
            continue
        if cond.get("effect") in ("requires_review", "conditional"):
            result["conditions"].append(cond["description"])
            review = True
    if review:
        result["status"] = ELIGIBLE_WITH_CONDITIONS
    return result


def match(applicant, rules=None):
    """Match one applicant against all same-category canonical rules.

    Returns one result per same-category funder (including ineligible and
    undetermined outcomes, so audits can see why a funder did not match).
    """
    rules = rules if rules is not None else load_rules()
    results = [match_rule(applicant, rule) for rule in rules
               if rule.get("category") == applicant.get("category")]
    results.sort(key=lambda r: (r["status"] == INELIGIBLE, r["funder"]))
    return results
