from typing import List
from ialm_carbon.methods.soc.factor_sets import SOCFactorSet

def calculate_ipcc_stock(factor_set: SOCFactorSet) -> float:
    """
    SOC = SOCREF * FLU * FMG * FI
    """
    return factor_set.soc_ref_tC_ha * factor_set.flu * factor_set.fmg * factor_set.fi

def calculate_annual_stock_change(initial_stock: float, final_stock: float, transition_years: int = 20) -> float:
    """
    soc_change_tC_ha_yr = (final_stock - initial_stock) / transition_years
    """
    if transition_years <= 0:
        return 0.0
    return (final_stock - initial_stock) / transition_years
