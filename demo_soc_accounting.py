import os
import sys
from datetime import date

# Add project root to path
sys.path.append(os.path.join(os.getcwd(), '..', 'agricultural-land-management'))

from ialm_carbon.io.loaders import load_soc_samples, load_strata, load_model_config, load_factor_sets
from ialm_carbon.methods.soc.measured_stock import convert_tc_to_tco2e
from ialm_carbon.methods.soc.factor_based_stock_change import calculate_ipcc_stock, calculate_annual_stock_change
from ialm_carbon.methods.soc.aggregation import aggregate_measured_to_stratum
from ialm_carbon.methods.soc.results import SOCResult
from ialm_carbon.reporting.soc_summary import export_soc_summary

def main():
    data_dir = os.path.join('..', 'agricultural-land-management', 'data', 'my_project')
    raw_dir = os.path.join(data_dir, 'raw')
    param_dir = os.path.join(data_dir, 'parameters')
    output_dir = os.path.join(data_dir, 'outputs')
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 1. Load data
    samples = load_soc_samples(os.path.join(raw_dir, 'soc_samples.csv'))
    strata = load_strata(os.path.join(raw_dir, 'strata.csv'))
    config = load_model_config(os.path.join(param_dir, 'soc_model_config.yaml'))
    
    # Updated: Load factor sets from the new files in the raw directory
    factor_sets = load_factor_sets(os.path.join(raw_dir, 'soc_stock_change_factors.csv'),
                                   os.path.join(raw_dir, 'soc_reference_stocks.csv'))

    results = []
    
    # 2. Process each stratum
    for stratum in strata:
        # For demo, we'll use factor-based if no samples, otherwise measured
        stratum_samples = [s for s in samples if s.stratum_id == stratum.stratum_id]
        
        # Calculate Current Stock
        if stratum_samples:
            current_stock_tC_ha = aggregate_measured_to_stratum(stratum_samples, stratum.project_id, stratum.stratum_id, 2024)
        else:
            # Use IPCC factor-based for current
            matching_factors = [f for f in factor_sets if f.climate_zone == stratum.climate_zone 
                                and f.soil_type == stratum.soil_type
                                and f.land_use_class == stratum.land_use_class
                                and f.management_regime == stratum.management_regime]
            current_stock_tC_ha = calculate_ipcc_stock(matching_factors[0]) if matching_factors else 0.0
            
        # Calculate Baseline Stock (Factor-based for this demo)
        baseline_factors = [f for f in factor_sets if f.climate_zone == stratum.climate_zone 
                            and f.soil_type == stratum.soil_type
                            and f.land_use_class == stratum.baseline_land_use
                            and f.management_regime == stratum.baseline_management]
        baseline_stock_tC_ha = calculate_ipcc_stock(baseline_factors[0]) if baseline_factors else current_stock_tC_ha

        # Stock Change
        annual_change_tC_ha = calculate_annual_stock_change(baseline_stock_tC_ha, current_stock_tC_ha, config.transition_period_years)
        annual_change_tCO2e_ha = convert_tc_to_tco2e(annual_change_tC_ha)
        total_change_tCO2e = annual_change_tCO2e_ha * stratum.area_ha
        
        # Uncertainty & Conservatism
        uncertainty = config.default_uncertainty_pct
        deduction = config.default_conservative_deduction_pct
        creditable = total_change_tCO2e * (1 - deduction) if total_change_tCO2e > 0 else 0.0
        
        results.append(SOCResult(
            project_id=stratum.project_id,
            stratum_id=stratum.stratum_id,
            year=2024,
            soc_stock_tC_ha=current_stock_tC_ha,
            soc_stock_tCO2e_ha=convert_tc_to_tco2e(current_stock_tC_ha),
            soc_change_tC_ha_yr=annual_change_tC_ha,
            soc_change_tCO2e_ha_yr=annual_change_tCO2e_ha,
            total_change_tCO2e_yr=total_change_tCO2e,
            uncertainty_pct=uncertainty,
            conservative_adjustment_pct=deduction,
            creditable_change_tCO2e_yr=creditable,
            area_ha=stratum.area_ha
        ))

    # 3. Export results
    output_path = os.path.join(output_dir, 'soc_summary_demo.csv')
    export_soc_summary(results, output_path)
    print(f"Demo completed. Results exported to {output_path}")

if __name__ == "__main__":
    main()
