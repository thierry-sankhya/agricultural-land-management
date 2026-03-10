from dataclasses import dataclass

@dataclass
class SOCFactorSet:
    climate_zone: str
    soil_type: str
    land_use_class: str
    management_regime: str
    input_regime: str
    water_regime: str
    soc_ref_tC_ha: float
    flu: float
    fmg: float
    fi: float
    depth_basis_cm: float = 30.0
    