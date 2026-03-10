from dataclasses import dataclass

@dataclass
class SOCResult:
    project_id: str
    stratum_id: str
    year: int
    soc_stock_tC_ha: float
    soc_stock_tCO2e_ha: float
    soc_change_tC_ha_yr: float
    soc_change_tCO2e_ha_yr: float
    total_change_tCO2e_yr: float
    uncertainty_pct: float
    conservative_adjustment_pct: float
    creditable_change_tCO2e_yr: float
    area_ha: float = 0.0
