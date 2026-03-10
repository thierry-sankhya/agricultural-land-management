from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional, Dict, Any
from enum import Enum

class PracticeType(Enum):
    TILLAGE = "tillage"
    FERTILIZER = "fertilizer"
    WATER_MGMT = "water_management"
    COVER_CROP = "cover_crop"
    CROP_ROTATION = "crop_rotation"
    GRAZING = "grazing"
    AGROFORESTRY = "agroforestry"

@dataclass
class Project:
    project_id: str
    name: str
    methodology: str
    crediting_period_start: date
    crediting_period_end: date
    total_area_ha: float

@dataclass
class Stratum:
    stratum_id: str
    name: str
    soil_type: str
    climate_zone: str
    area_ha: float

@dataclass
class ProjectArea:
    area_id: str
    geometry: Any  # GeoJSON or similar
    strata: List[Stratum]
    total_area_ha: float

@dataclass
class PracticeChange:
    practice_type: PracticeType
    description: str
    start_date: date
    is_additionality_verified: bool

@dataclass
class ManagementSchedule:
    year: int
    stratum_id: str
    practices: List[PracticeChange]
    nitrogen_rate_kg_ha: float = 0.0
    irrigation_m3_ha: float = 0.0
    residue_retained_pct: float = 0.0

@dataclass
class SoilSample:
    sample_id: str
    stratum_id: str
    date: date
    depth_cm: float
    soc_stock_t_ha: float
    bulk_density_g_cm3: float
    uncertainty_pct: float

@dataclass
class MonitoringEvent:
    event_id: str
    date: date
    event_type: str  # e.g., "Remote Sensing", "Field Visit"
    findings: Dict[str, Any]

@dataclass
class ClimateEvent:
    event_id: str
    date: date
    type: str  # "Drought", "Flood", "Fire"
    impact_severity: float  # 0 to 1
    affected_area_ha: float

@dataclass
class ConservativeAdjustment:
    component: str
    deduction_pct: float
    reason: str

@dataclass
class QuantificationUnit:
    unit_id: str
    stratum_id: str
    year: int
    gross_removals_tco2e: float = 0.0
    gross_reductions_tco2e: float = 0.0
    leakage_deduction_tco2e: float = 0.0
    uncertainty_deduction_tco2e: float = 0.0
    net_benefit_tco2e: float = 0.0

@dataclass
class ValuationScenario:
    scenario_name: str
    carbon_price_usd: float
    discount_rate: float
    issuance_probability: float
