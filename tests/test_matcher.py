"""Tests for the M-T723-V1 canonical matcher, generated rules and generator.

Covers: source provenance, contradiction resolution, conditional terms and
regions, per INSTRUCTIONS.md. Stdlib only: python -m unittest discover tests
(or pytest).
"""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import generate_rules  # noqa: E402
import matcher  # noqa: E402

RULES = matcher.load_rules()
BY_FUNDER = {r["funder"]: r for r in RULES}
EXAMPLES = json.loads(
    (ROOT / "examples" / "synthetic_applicants.json").read_text(encoding="utf-8"))
EXAMPLES_BY_NAME = {a["name"]: a for a in EXAMPLES}


def result_for(applicant, funder):
    for result in matcher.match(applicant, RULES):
        if result["funder"] == funder:
            return result
    raise AssertionError("no result for %s vs %s" % (applicant.get("name"), funder))


class TestProvenance(unittest.TestCase):
    def test_every_rule_has_literal_provenance(self):
        for rule in RULES:
            self.assertTrue(rule["provenance"]["literal"], rule["funder"])

    def test_exclusions_have_literal_or_appendix_authority(self):
        for rule in RULES:
            for exclusion in rule["exclusions"]:
                sources = exclusion["source"]
                self.assertTrue(
                    any(s.startswith("L") for s in sources)
                    or any(s.startswith("A") for s in sources),
                    "%s: exclusion without high authority" % rule["funder"])

    def test_no_exclusion_is_corpus_sourced(self):
        for rule in RULES:
            for exclusion in rule["exclusions"]:
                self.assertFalse(
                    any(s.startswith("C") for s in exclusion["source"]),
                    "%s: corpus-sourced exclusion" % rule["funder"])

    def test_appendix_provenance_is_legible(self):
        appendix = {}
        path = ROOT / "evidence" / "appendix" / "appendix_extracts.jsonl"
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                row = json.loads(line)
                appendix.setdefault(row["id"], row)
        for rule in RULES:
            if not rule["eligibility_authority"]:
                continue
            for aid in rule["provenance"]["appendix"]:
                self.assertTrue(appendix[aid]["legible"],
                                "%s: illegible %s used as authority" % (rule["funder"], aid))

    def test_generator_reproduces_committed_rules(self):
        corpus, literal, appendix = generate_rules.load_evidence()
        self.assertEqual(
            generate_rules.validate(generate_rules.DECISIONS, corpus, literal, appendix), [])
        regenerated = json.loads(json.dumps(generate_rules.DECISIONS))
        committed = [
            json.loads(line)
            for line in (ROOT / "rules" / "canonical_rules.jsonl")
            .read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        self.assertEqual(regenerated, committed)


class TestAuthorityGate(unittest.TestCase):
    def test_prairie_wellness_is_undetermined(self):
        self.assertFalse(BY_FUNDER["Prairie Wellness"]["eligibility_authority"])
        result = result_for(
            {"name": "probe", "type": "nonprofit", "region": "US-Plains",
             "category": "health"},
            "Prairie Wellness")
        self.assertEqual(result["status"], matcher.UNDETERMINED)


class TestContradictions(unittest.TestCase):
    def test_cedar_arts_schools_not_excluded(self):
        rule = BY_FUNDER["Cedar Arts"]
        self.assertIn("public_school", rule["eligible_types"])
        self.assertFalse(rule["exclusions"])

    def test_umber_heritage_capital_not_excluded(self):
        rule = BY_FUNDER["Umber Heritage"]
        self.assertFalse(rule["exclusions"])
        self.assertIn("capital", rule["scope"])

    def test_mesa_water_fiscal_sponsor_not_required(self):
        rule = BY_FUNDER["Mesa Water"]
        self.assertIn("nonprofit", rule["eligible_types"])
        self.assertFalse(rule["conditions"])

    def test_quarry_workforce_union_not_required(self):
        rule = BY_FUNDER["Quarry Workforce"]
        self.assertFalse(rule["conditions"])
        self.assertFalse(rule["exclusions"])

    def test_lumen_mobility_policy_not_excluded(self):
        rule = BY_FUNDER["Lumen Mobility"]
        self.assertIn("policy", rule["scope"])
        self.assertFalse(rule["exclusions"])

    def test_ember_justice_advocacy_eligible(self):
        rule = BY_FUNDER["Ember Justice"]
        self.assertIn("advocacy", rule["scope"])
        self.assertFalse(rule["exclusions"])


class TestConditions(unittest.TestCase):
    def test_zephyr_response_requires_declared_emergency(self):
        base = {"name": "probe", "type": "nonprofit", "region": "APAC",
                "category": "humanitarian"}
        without = result_for(dict(base, declared_emergency=False), "Zephyr Disaster")
        self.assertEqual(without["status"], matcher.ELIGIBLE)
        self.assertIn("response", without["blocked_tracks"])
        with_em = result_for(dict(base, declared_emergency=True), "Zephyr Disaster")
        self.assertEqual(with_em["status"], matcher.ELIGIBLE)
        self.assertEqual(with_em["blocked_tracks"], [])

    def test_verdant_for_profit_is_conditional_not_excluded(self):
        result = result_for(
            {"name": "probe", "type": "for_profit", "region": "Global",
             "category": "food"},
            "Verdant Agriculture")
        self.assertEqual(result["status"], matcher.CONDITIONAL)

    def test_delta_multi_state_partner_is_condition_not_exclusion(self):
        rule = BY_FUNDER["Delta Food"]
        self.assertFalse(rule["exclusions"])
        self.assertEqual(rule["conditions"][0]["key"], "local_partner_multi_state")


class TestRegions(unittest.TestCase):
    def test_aster_accepts_canada(self):
        result = result_for(
            {"name": "probe", "type": "charity", "region": "CA", "category": "health"},
            "Aster Health")
        self.assertEqual(result["status"], matcher.ELIGIBLE)

    def test_aster_rejects_eu(self):
        result = result_for(
            {"name": "probe", "type": "charity", "region": "EU", "category": "health"},
            "Aster Health")
        self.assertEqual(result["status"], matcher.INELIGIBLE)

    def test_solace_is_mena_only(self):
        result = result_for(
            {"name": "probe", "type": "nonprofit", "region": "US",
             "category": "humanitarian"},
            "Solace Refuge")
        self.assertEqual(result["status"], matcher.INELIGIBLE)

    def test_harbor_inland_not_excluded(self):
        result = result_for(
            {"name": "probe", "type": "nonprofit", "region": "US-MW",
             "category": "environment"},
            "Harbor Oceans")
        self.assertNotEqual(result["status"], matcher.INELIGIBLE)


class TestSyntheticExamples(unittest.TestCase):
    def test_authorized_examples(self):
        r = result_for(EXAMPLES_BY_NAME["Canadian clinic"], "Aster Health")
        self.assertEqual(r["status"], matcher.ELIGIBLE)
        r = result_for(EXAMPLES_BY_NAME["NE public school"], "Cedar Arts")
        self.assertEqual(r["status"], matcher.ELIGIBLE_WITH_CONDITIONS)
        r = result_for(EXAMPLES_BY_NAME["Inland watershed group"], "Harbor Oceans")
        self.assertEqual(r["status"], matcher.ELIGIBLE_WITH_CONDITIONS)
        r = result_for(EXAMPLES_BY_NAME["Inland watershed group"], "Tandem Trees")
        self.assertEqual(r["status"], matcher.ELIGIBLE)
        r = result_for(EXAMPLES_BY_NAME["APAC emergency NGO"], "Zephyr Disaster")
        self.assertEqual(r["status"], matcher.ELIGIBLE)
        self.assertEqual(r["blocked_tracks"], [])
        r = result_for(EXAMPLES_BY_NAME["APAC preparedness NGO"], "Zephyr Disaster")
        self.assertEqual(r["status"], matcher.ELIGIBLE)
        self.assertIn("response", r["blocked_tracks"])
        r = result_for(EXAMPLES_BY_NAME["Startup farm pilot"], "Verdant Agriculture")
        self.assertEqual(r["status"], matcher.CONDITIONAL)
        r = result_for(EXAMPLES_BY_NAME["Startup farm pilot"], "Delta Food")
        self.assertEqual(r["status"], matcher.INELIGIBLE)
        r = result_for(EXAMPLES_BY_NAME["Fiscal-sponsor rural group"], "Juniper Rural")
        self.assertEqual(r["status"], matcher.ELIGIBLE)
        r = result_for(EXAMPLES_BY_NAME["Unionless workforce nonprofit"], "Quarry Workforce")
        self.assertEqual(r["status"], matcher.ELIGIBLE)


if __name__ == "__main__":
    unittest.main()
