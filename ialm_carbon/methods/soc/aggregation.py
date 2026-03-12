from typing import List, Dict
from collections import defaultdict
from ialm_carbon.domain.soc_entities import SOCSample
from ialm_carbon.methods.soc.measured_stock import calculate_layer_stock, convert_tc_to_tco2e
from ialm_carbon.methods.soc.results import SOCResult

def aggregate_measured_to_stratum(samples: List[SOCSample], project_id: str, stratum_id: str, year: int) -> float:
    """
    layer -> plot -> stratum
    """
    # 1. Group layers by plot
    plot_stocks = defaultdict(float)
    for sample in samples:
        if sample.project_id == project_id and sample.stratum_id == stratum_id:
            plot_stocks[sample.plot_id] += calculate_layer_stock(sample)
    
    # 2. Average plot stocks for stratum
    if not plot_stocks:
        return 0.0
    
    avg_stratum_stock_tC_ha = sum(plot_stocks.values()) / len(plot_stocks)
    return avg_stratum_stock_tC_ha

def compute_project_totals(stratum_results: List[SOCResult]) -> float:
    """
    stratum -> project total tCO2e_yr
    """
    total_creditable = sum(res.creditable_change_tCO2e_yr for res in stratum_results)
    return total_creditable
