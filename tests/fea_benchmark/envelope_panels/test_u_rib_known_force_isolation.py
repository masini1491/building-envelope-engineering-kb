"""Fail-closed controls for the known-load isolated open-U shell experiment."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from check_u_rib_known_force_isolation import CASES, MESHES, deck, generate, load_nodes, observe, noncontact_known_force_residual


class KnownForceIsolationTests(unittest.TestCase):
    def test_loaded_nodes_are_unconstrained_and_symmetrical(self):
        for n in MESHES:
            topo, nodes = load_nodes(n)
            self.assertEqual(len(nodes), 2)
            self.assertTrue(set(nodes).isdisjoint(topo["clamped_rib_end"]))

    def test_force_sign_and_no_contact_or_studs(self):
        for n in MESHES:
            topo, nodes = load_nodes(n)
            for case in CASES:
                with self.subTest(n=n, case=case):
                    content = deck(n, case)
                    self.assertEqual(content.count("*CLOAD"), 1)
                    self.assertEqual(content.count("*CONTACT PAIR"), 0)
                    self.assertNotIn("SPRING2", content)
                    sign = 0.5 if case == "up" else -0.5
                    for node in nodes:
                        self.assertIn(f"{node},3,{sign:.8f}", content)
                    self.assertIn("*NODE PRINT,NSET=RIB_END_RF", content)

    def test_scope_rejection(self):
        for n in (4, 0, True, 8.0):
            with self.assertRaises(ValueError):
                deck(n, "up")
        with self.assertRaises(ValueError):
            deck(8, "wrong")

    def test_known_force_balance_requires_finite_and_correct_sign(self):
        self.assertAlmostEqual(noncontact_known_force_residual(-1.0000028, 1.0), -0.0000028)
        self.assertAlmostEqual(noncontact_known_force_residual(0.9999986, -1.0), -0.0000014)
        for reaction, load in ((-0.98, 1.0), (1.0, 1.0), (float("nan"), 1.0),
                               (0.0, float("inf")), (-1.0, 0.5)):
            with self.subTest(reaction=reaction, load=load):
                with self.assertRaises(ValueError):
                    noncontact_known_force_residual(reaction, load)

    def test_generation_and_missing_evidence(self):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "case"
            generate(target, 8, "up")
            self.assertEqual((target / "panel.inp").read_text(), deck(8, "up"))
            with self.assertRaises(ValueError):
                generate(target, 8, "up")
            with self.assertRaises(ValueError):
                observe(td)


if __name__ == "__main__":
    unittest.main()
