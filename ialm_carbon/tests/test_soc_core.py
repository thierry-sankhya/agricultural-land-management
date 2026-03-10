import unittest
from datetime import date
from ialm_carbon.domain.soc_entities import SOCSample
from ialm_carbon.methods.soc.measured_stock import calculate_layer_stock, convert_tc_to_tco2e
from ialm_carbon.methods.soc.factor_based_stock_change import calculate_ipcc_stock, calculate_annual_stock_change
from ialm_carbon.methods.soc.factor_sets import SOCFactorSet
from ialm_carbon.methods.soc.aggregation import aggregate_measured_to_stratum

class TestSOCCalculations(unittest.TestCase):
    def test_measured_stock(self):
        sample = SOCSample(
            sample_id="s1", project_id="p1", stratum_id="st1", plot_id="pl1",
            sample_event_id="e1", sample_date=date(2024, 1, 1),
            depth_top_cm=0, depth_bottom_cm=30, soc_percent=2.0,
            bulk_density_g_cm3=1.2, coarse_fragment_vol_frac=0.1,
            texture_class="loam", lab_method="dry_combustion",
            latitude=0, longitude=0, qa_status="passed"
        )
        # SOC_stock_tC_ha = 2.0 * 1.2 * 30 * (1 - 0.1) * 0.1 = 6.48
        stock = calculate_layer_stock(sample)
        self.assertAlmostEqual(stock, 6.48)
        
        # tCO2e = 6.48 * 44/12 = 23.76
        self.assertAlmostEqual(convert_tc_to_tco2e(stock), 23.76)

    def test_factor_based_stock(self):
        fs = SOCFactorSet(
            climate_zone="warm_temperate_moist", soil_type="hac",
            land_use_class="cropland", management_regime="reduced_tillage",
            input_regime="medium", water_regime="rainfed",
            soc_ref_tC_ha=60.0, flu=0.69, fmg=1.02, fi=1.0
        )
        # 60 * 0.69 * 1.02 * 1.0 = 42.228
        stock = calculate_ipcc_stock(fs)
        self.assertAlmostEqual(stock, 42.228)
        
        # Change: (42.228 - 30) / 20 = 0.6114
        change = calculate_annual_stock_change(30.0, 42.228, 20)
        self.assertAlmostEqual(change, 0.6114)

    def test_aggregation(self):
        samples = [
            SOCSample("s1", "p1", "st1", "pl1", "e1", date(2024, 1, 1), 0, 15, 2.0, 1.0, 0, "loam", "lab", 0, 0, "p"),
            SOCSample("s2", "p1", "st1", "pl1", "e1", date(2024, 1, 1), 15, 30, 1.0, 1.0, 0, "loam", "lab", 0, 0, "p"),
            SOCSample("s3", "p1", "st1", "pl2", "e1", date(2024, 1, 1), 0, 30, 1.5, 1.0, 0, "loam", "lab", 0, 0, "p"),
        ]
        # pl1: (2.0*1.0*15*0.1) + (1.0*1.0*15*0.1) = 3.0 + 1.5 = 4.5
        # pl2: (1.5*1.0*30*0.1) = 4.5
        # st1 avg: (4.5 + 4.5) / 2 = 4.5
        avg_stock = aggregate_measured_to_stratum(samples, "p1", "st1", 2024)
        self.assertAlmostEqual(avg_stock, 4.5)

if __name__ == "__main__":
    unittest.main()
