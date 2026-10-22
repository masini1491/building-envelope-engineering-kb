"""合成資料測試；不含 ADM 材料容量、係數或表格。"""
import dataclasses
import unittest

from scripts.engineering_calc.aluminum_member_capacity_evidence import (
    AluminumCapacityEvidenceError,
    inspect_aluminum_member_capacity_evidence as inspect,
)

CTX = dict(member_role="mullion", alloy_temper="6063-T5",
           product_form="extrusion", weld_condition="unwelded",
           adm_edition="2020", design_method="ASD")


def source(**overrides):
    return {**{key: CTX[key] for key in ("alloy_temper", "product_form",
                                        "weld_condition", "adm_edition", "design_method")},
            "reference_locator": "synthetic engineer-supplied capacity reference",
            **overrides}


def entry(mode="flexure", *, demand=25.0, capacity=50.0, unit="N-mm"):
    return dict(limit_state_id=mode, status="EXTERNAL_CAPACITY_SUPPLIED",
                unit=unit, demand=demand, design_capacity=capacity,
                capacity_source=source())


def invoke(**changes):
    args=dict(member_context=CTX,
              required_limit_states=["flexure", "shear"],
              limit_state_entries=[entry(), entry("shear", demand=60, capacity=40, unit="N")],
              combined_action_review=dict(status="EXTERNALLY_REVIEWED",
                                          reference_locator="synthetic interaction reference"))
    args.update(changes)
    return inspect(**args)


class CapacityEvidenceGateTests(unittest.TestCase):
    def test_numeric_only_never_admits_design(self):
        res=invoke()
        self.assertEqual(res.calculation_status, "NUMERIC_RECONCILIATION_ONLY")
        self.assertEqual([c.ratio for c in res.comparisons], [0.5, 1.5])
        self.assertEqual([c.exceeds_supplied_capacity for c in res.comparisons], [False, True])
        self.assertEqual(res.standard_capacity_kernel, "NOT_IMPLEMENTED")
        self.assertEqual(res.engineering_acceptance, "NOT_ADMITTED")
        self.assertEqual(res.source_authenticity, "NOT_INDEPENDENTLY_VERIFIED")
        self.assertEqual(res.unresolved_limit_states, ())
        self.assertEqual(dataclasses.asdict(res)["scope_status"], "USER_DECLARED_LIMIT_STATE_SET_ONLY")

    def test_no_overall_pass_even_if_all_ratios_below_one(self):
        result=invoke(limit_state_entries=[entry(), entry("shear", demand=1, capacity=2, unit="N")])
        self.assertEqual(result.calculation_status, "NUMERIC_RECONCILIATION_ONLY")
        self.assertFalse(any(v.exceeds_supplied_capacity for v in result.comparisons))
        self.assertEqual(result.engineering_acceptance, "NOT_ADMITTED")

    def test_missing_mode_is_incomplete(self):
        result=invoke(limit_state_entries=[entry()])
        self.assertEqual(result.calculation_status, "INCOMPLETE_INPUT")
        self.assertEqual(result.unresolved_limit_states, ("shear",))

    def test_unresolved_interaction_is_incomplete(self):
        result=invoke(combined_action_review=dict(status="UNRESOLVED", reason="no independent interaction review"))
        self.assertEqual(result.calculation_status, "INCOMPLETE_INPUT")
        self.assertEqual(result.declared_interaction_status, "UNRESOLVED")

    def test_unresolved_mode_preserved(self):
        result=invoke(limit_state_entries=[
            entry(), dict(limit_state_id="shear", status="UNRESOLVED", reason="capacity unavailable")])
        self.assertEqual(result.unresolved_limit_states, ("shear",))
        self.assertEqual(len(result.comparisons), 1)

    def test_identity_guard_and_invalid_data(self):
        bad=[
            {"member_context": {**CTX, "design_method": "UNKNOWN"}},
            {"member_context": {**CTX, "alloy_temper": ""}},
            {"required_limit_states": []},
            {"required_limit_states": ["flexure", "flexure"]},
            {"limit_state_entries": [entry()] * 2},
            {"limit_state_entries": [entry("unknown")]},
            {"limit_state_entries": [entry(demand=float("nan"))]},
            {"limit_state_entries": [entry(demand=True)]},
            {"limit_state_entries": [entry(capacity=0)]},
            {"limit_state_entries": [entry(capacity=-1)]},
            {"limit_state_entries": [entry(unit="kN")]},
            {"limit_state_entries": [{**entry(), "capacity_source": source(design_method="LRFD")}]},
            {"limit_state_entries": [{**entry(), "capacity_source": source(weld_condition="welded")}]},
            {"limit_state_entries": [{**entry(), "capacity_source": source(reference_locator="")}]},
            {"combined_action_review": {"status": "EXTERNALLY_REVIEWED"}},
            {"combined_action_review": {"status": "UNRESOLVED", "reason": ""}},
        ]
        for item in bad:
            with self.subTest(item=item), self.assertRaises(AluminumCapacityEvidenceError):
                invoke(**item)


if __name__ == "__main__":
    unittest.main()
