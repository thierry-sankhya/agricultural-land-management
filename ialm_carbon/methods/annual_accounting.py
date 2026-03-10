from typing import List, Dict, Any
from ialm_carbon.domain.entities import ManagementSchedule, QuantificationUnit

class GHGAccountingEngine:
    """
    Orchestrates annual net-GHG accounting across all components (SOC, N2O, CH4, CO2).
    """
    
    # Global Warming Potentials (IPCC AR5)
    GWP_N2O = 265
    GWP_CH4 = 28

    def __init__(self, project_id: str):
        self.project_id = project_id

    def calculate_annual_n2o_reductions(self, baseline_rate_kg_n_ha: float, 
                                          project_rate_kg_n_ha: float, 
                                          emission_factor: float = 0.01) -> float:
        """
        Calculates N2O emission reductions from fertilizer management.
        (Baseline N - Project N) * EF * GWP_N2O * (44/28 for N to N2O conversion)
        Returns: tCO2e / ha / yr
        """
        n_saved_kg_ha = max(0, baseline_rate_kg_n_ha - project_rate_kg_n_ha)
        n2o_saved_kg_ha = n_saved_kg_ha * emission_factor * (44 / 28)
        return (n2o_saved_kg_ha / 1000.0) * self.GWP_N2O

    def calculate_fuel_co2_reductions(self, baseline_fuel_l_ha: float, 
                                        project_fuel_l_ha: float, 
                                        fuel_ef: float = 2.68) -> float:
        """
        Calculates CO2 emission reductions from fuel use (e.g., reduced tillage).
        Returns: tCO2e / ha / yr
        """
        fuel_saved_l_ha = max(0, baseline_fuel_l_ha - project_fuel_l_ha)
        return (fuel_saved_l_ha * fuel_ef) / 1000.0

    def compute_net_annual_benefit(self, stratum_id: str, year: int,
                                    soc_removals: float,
                                    n2o_reductions: float,
                                    co2_reductions: float,
                                    leakage_factor: float = 0.0,
                                    uncertainty_buffer: float = 0.1) -> QuantificationUnit:
        """
        Aggregates components into a single QuantificationUnit for the year.
        """
        gross_removals = max(0, soc_removals)
        gross_reductions = max(0, n2o_reductions + co2_reductions)
        
        leakage_deduction = (gross_removals + gross_reductions) * leakage_factor
        uncertainty_deduction = (gross_removals + gross_reductions) * uncertainty_buffer
        
        net_benefit = gross_removals + gross_reductions - leakage_deduction - uncertainty_deduction
        
        return QuantificationUnit(
            unit_id=f"{stratum_id}_{year}",
            stratum_id=stratum_id,
            year=year,
            gross_removals_tco2e=gross_removals,
            gross_reductions_tco2e=gross_reductions,
            leakage_deduction_tco2e=leakage_deduction,
            uncertainty_deduction_tco2e=uncertainty_deduction,
            net_benefit_tco2e=net_benefit
        )
