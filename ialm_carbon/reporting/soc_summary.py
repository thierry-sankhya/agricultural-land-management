import csv
from typing import List
from ialm_carbon.methods.soc.results import SOCResult

def export_soc_summary(results: List[SOCResult], filepath: str):
    if not results:
        return
    
    headers = [
        'project_id', 'stratum_id', 'year', 'soc_stock_tC_ha', 'soc_stock_tCO2e_ha',
        'soc_change_tC_ha_yr', 'soc_change_tCO2e_ha_yr', 'total_change_tCO2e_yr',
        'uncertainty_pct', 'conservative_adjustment_pct', 'creditable_change_tCO2e_yr'
    ]
    
    with open(filepath, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for res in results:
            writer.writerow({
                'project_id': res.project_id,
                'stratum_id': res.stratum_id,
                'year': res.year,
                'soc_stock_tC_ha': round(res.soc_stock_tC_ha, 4),
                'soc_stock_tCO2e_ha': round(res.soc_stock_tCO2e_ha, 4),
                'soc_change_tC_ha_yr': round(res.soc_change_tC_ha_yr, 4),
                'soc_change_tCO2e_ha_yr': round(res.soc_change_tCO2e_ha_yr, 4),
                'total_change_tCO2e_yr': round(res.total_change_tCO2e_yr, 4),
                'uncertainty_pct': res.uncertainty_pct,
                'conservative_adjustment_pct': res.conservative_adjustment_pct,
                'creditable_change_tCO2e_yr': round(res.creditable_change_tCO2e_yr, 4)
            })
