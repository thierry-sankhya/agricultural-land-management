from dataclasses import dataclass
from datetime import date
from typing import Optional

@dataclass
class SOCSample:
    sample_id: str
    project_id: str
    stratum_id: str
    plot_id: str
    sample_event_id: str
    sample_date: date
    depth_top_cm: float
    depth_bottom_cm: float
    soc_percent: float
    bulk_density_g_cm3: float
    coarse_fragment_vol_frac: float
    texture_class: str
    lab_method: str
    latitude: float
    longitude: float
    qa_status: str
    soil_moisture_pct: Optional[float] = None
    ph: Optional[float] = None
    notes: Optional[str] = None

@dataclass
class SOCStratum:
    stratum_id: str
    project_id: str
    area_ha: float
    climate_zone: str
    soil_type: str
    land_use_class: str
    management_regime: str
    input_regime: str
    water_regime: str
    baseline_land_use: str
    baseline_management: str
    stratum_name: Optional[str] = None
    grazing_regime: Optional[str] = None
    agroforestry_system: Optional[str] = None
    eligibility_start_date: Optional[date] = None
    notes: Optional[str] = None
