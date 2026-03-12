from ialm_carbon.domain.soc_entities import SOCSample

C_TO_CO2E = 44 / 12

def calculate_layer_stock(sample: SOCSample) -> float:
    """
    SOC_stock_tC_ha = soc_percent * bulk_density_g_cm3 * depth_cm * (1 - coarse_fragment_vol_frac) * 0.1 [WRONG]

    Corrected value without the 0.1 factor!
    SOC_stock_tC_ha = soc_percent * bulk_density_g_cm3 * depth_cm * (1 - coarse_fragment_vol_frac)
    """
    depth_cm = sample.depth_bottom_cm - sample.depth_top_cm
    if depth_cm <= 0:
        return 0.0
    
    stock_tC_ha = (sample.soc_percent * 
                   sample.bulk_density_g_cm3 * 
                   depth_cm * 
                   (1 - sample.coarse_fragment_vol_frac) )
    return stock_tC_ha

def convert_tc_to_tco2e(stock_tc: float) -> float:
    return stock_tc * C_TO_CO2E
