import pandas as pd
import numpy as np
from typing import List, Optional
from ialm_carbon.domain.entities import SoilSample, Stratum

class SOCAccounting:
    """
    Handles Soil Organic Carbon (SOC) accounting using sample-based and basic model-based logic.
    """
    
    # Constants
    C_TO_CO2_CONVERSION = 44 / 12  # Ratio of CO2e weight to Carbon weight

    def __init__(self, baseline_samples: List[SoilSample]):
        self.baseline_samples = baseline_samples
        self.baseline_stock = self._calculate_weighted_avg_stock(baseline_samples)

    def _calculate_weighted_avg_stock(self, samples: List[SoilSample]) -> float:
        """Calculate average SOC stock (t C / ha) across a set of raw."""
        if not samples:
            return 0.0
        return np.mean([s.soc_stock_t_ha for s in samples])

    def calculate_stock_change(self, current_samples: List[SoilSample]) -> float:
        """
        Calculate net SOC stock change in tCO2e / ha relative to baseline.
        Negative value indicates carbon loss.
        """
        current_stock = self._calculate_weighted_avg_stock(current_samples)
        stock_diff_t_c_ha = current_stock - self.baseline_stock
        return stock_diff_t_c_ha * self.C_TO_CO2_CONVERSION

    def estimate_rothc_rate(self, clay_content_pct: float, residue_input_t_ha: float, 
                           precip_mm: float, temp_c: float) -> float:
        """
        A placeholder for a process-based model integration (e.g., RothC).
        Returns estimated annual sequestration rate in tCO2e/ha/yr.
        """
        # Simplified empirical estimation for blueprint purposes
        # In production, this would call a RothC or DayCent wrapper.
        base_rate = 0.5 # tC/ha/yr base for cover crops
        climate_factor = max(0.2, min(1.5, temp_c / 20.0 * precip_mm / 800.0))
        return base_rate * climate_factor * self.C_TO_CO2_CONVERSION

    def apply_depth_standardization(self, stock: float, original_depth: float, 
                                     standard_depth: float = 30.0) -> float:
        """Adjusts SOC stock to a standard depth (usually 30cm or 100cm)."""
        # Linear approximation (simple default for blueprint)
        return stock * (standard_depth / original_depth)
