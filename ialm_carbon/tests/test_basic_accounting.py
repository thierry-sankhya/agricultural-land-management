import unittest
from datetime import date
from ialm_carbon.domain.entities import SoilSample
from ialm_carbon.methods.soc.soc_engine import SOCAccounting
from ialm_carbon.methods.annual_accounting import GHGAccountingEngine

class TestIALMAccounting(unittest.TestCase):
    def setUp(self):
        self.baseline_samples = [
            SoilSample("s1", "stratum_a", date(2020, 1, 1), 30, 45.0, 1.3, 0.05),
            SoilSample("s2", "stratum_a", date(2020, 1, 1), 30, 47.0, 1.3, 0.05)
        ]
        self.soc_engine = SOCAccounting(self.baseline_samples)
        self.ghg_engine = GHGAccountingEngine("test_project")

    def test_soc_stock_change(self):
        current_samples = [
            SoilSample("s3", "stratum_a", date(2025, 1, 1), 30, 50.0, 1.3, 0.05),
            SoilSample("s4", "stratum_a", date(2025, 1, 1), 30, 52.0, 1.3, 0.05)
        ]
        # Avg baseline = 46.0, Avg current = 51.0 -> diff = 5.0 tC/ha
        # tCO2e = 5.0 * (44/12) = 18.333
        change = self.soc_engine.calculate_stock_change(current_samples)
        self.assertAlmostEqual(change, 18.333333333, places=5)

    def test_n2o_reductions(self):
        # Baseline 150 kgN/ha, Project 100 kgN/ha -> 50 kgN saved
        # 50 * 0.01 (EF) * (44/28) * 265 (GWP) / 1000 = 0.208
        reductions = self.ghg_engine.calculate_annual_n2o_reductions(150, 100)
        self.assertAlmostEqual(reductions, 0.2082142857, places=5)

    def test_net_benefit_calculation(self):
        unit = self.ghg_engine.compute_net_annual_benefit(
            stratum_id="stratum_a",
            year=2025,
            soc_removals=1.5,
            n2o_reductions=0.2,
            co2_reductions=0.1,
            leakage_factor=0.05,
            uncertainty_buffer=0.1
        )
        # Gross = 1.5 + 0.2 + 0.1 = 1.8
        # Leakage = 1.8 * 0.05 = 0.09
        # Uncertainty = 1.8 * 0.1 = 0.18
        # Net = 1.8 - 0.09 - 0.18 = 1.53
        self.assertEqual(unit.net_benefit_tco2e, 1.53)

if __name__ == '__main__':
    unittest.main()
