from dataclasses import dataclass
from typing import Optional

@dataclass
class SOCModelSpec:
    project_id: str
    accounting_mode: str  # measured_stock, factor_based, hybrid
    transition_period_years: int = 20
    default_uncertainty_pct: float = 0.15
    default_conservative_deduction_pct: float = 0.10
    depth_standard_cm: float = 30.0

@dataclass
class SOCStratumContext:
    stratum_id: str
    area_ha: float
    climate_zone: str
    soil_type: str
    land_use_class: str
    management_regime: str
    input_regime: str
    water_regime: str
    baseline_land_use: str
    baseline_management: str
    baseline_input_regime: Optional[str] = None
    baseline_water_regime: Optional[str] = None
