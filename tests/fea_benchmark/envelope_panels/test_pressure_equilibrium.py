"""Pure-Python S8R pressure assembly tests; actual CCX RF checked by workflow."""
from __future__ import annotations

import math
import tempfile
import unittest
from pathlib import Path

from generate import build
from check_pressure_equilibrium import integrate_loads, parse_deck, reconcile, shape


class EquilibriumTests(unittest.TestCase):
    def test_serendipity_partition_of_unity(self):
        for xi, eta in ((0, 0), (-0.6, 0.4), (1, 1), (-1, 0), (0.9, -0.8)):
            self.assertAlmostEqual(sum(shape(xi, eta)), 1, places=12)

    def test_independent_boundary_nodal_load(self):
        with tempfile.TemporaryDirectory() as td:
            for material in ("glass", "aluminum"):
                for n in (4, 8, 16):
                    folder = Path(td) / f"{material}_{n}"
                    build(material, n, "small", folder)
                    nodes, elements, edge, q = parse_deck(folder / "panel.inp")
                    loads, total = integrate_loads(nodes, elements, q)
                    expected_fraction = (2 * n + 1) / (3 * n * n)
                    self.assertAlmostEqual(total, 1.0, places=10)
                    self.assertAlmostEqual(sum(loads[k] for k in edge), expected_fraction, places=10)
                    self.assertEqual(len(edge), 8 * n)
                    self.assertEqual(len(elements), n * n)

    def test_rf_is_not_support_reaction_and_reconciliation(self):
        with tempfile.TemporaryDirectory() as td:
            folder = Path(td) / "glass"
            build("glass", 4, "small", folder)
            nodes, elements, edge, q = parse_deck(folder / "panel.inp")
            loads, total = integrate_loads(nodes, elements, q)
            dat = folder / "panel.dat"
            def fake_rf(extra=0.0, drop=None):
                rows = [" forces (fx,fy,fz) for set EDGE and time  0.1000000E+01", ""]
                for nid in sorted(edge):
                    if nid == drop:
                        continue
                    z = loads[nid] - total / len(edge) + extra / len(edge)
                    rows.append(f"{nid} 0.0 0.0 {z:.12E}")
                dat.write_text("\n".join(rows) + "\n\n")
            fake_rf()
            _, edge_load, raw, support, residual = reconcile(folder / "panel.inp", dat)
            self.assertAlmostEqual(raw[2], -0.8125, places=10)
            self.assertAlmostEqual(edge_load, 0.1875, places=10)
            self.assertAlmostEqual(support, -1, places=10)
            self.assertLess(residual, 1e-10)
            fake_rf(extra=0.04)
            with self.assertRaisesRegex(ValueError, "SMALL_LOAD_BALANCE_FAIL"):
                reconcile(folder / "panel.inp", dat)
            fake_rf(drop=min(edge))
            with self.assertRaisesRegex(ValueError, "INCOMPLETE_EDGE_RF"):
                reconcile(folder / "panel.inp", dat)

    def test_reject_distorted_element(self):
        with tempfile.TemporaryDirectory() as td:
            folder = Path(td) / "aluminum"
            build("aluminum", 4, "small", folder)
            nodes, elements, edge, q = parse_deck(folder / "panel.inp")
            nid = elements[0][4]
            x, y, z = nodes[nid]
            nodes[nid] = (x + 0.25, y, z)
            with self.assertRaisesRegex(ValueError, "NONRECTANGULAR_OR_DISTORTED_S8R"):
                integrate_loads(nodes, elements, q)


if __name__ == "__main__":
    unittest.main()
