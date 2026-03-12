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
    current_year = date.today().year
    
    for stratum in strata:
        # Determine Transition Period
        if stratum.transition_period_years:
            transition_period = stratum.transition_period_years
        elif stratum.soc_impact and stratum.soc_impact in config.transition_period_years_map:
            range_vals = config.transition_period_years_map[stratum.soc_impact]
            transition_period = sum(range_vals) / len(range_vals)
        else:
            transition_period = config.transition_period_years

        # Baseline Stock (Factor-based for this demo)
        baseline_factors = [f for f in factor_sets if f.climate_zone == stratum.climate_zone 
                            and f.soil_type == stratum.soil_type
                            and f.land_use_class == stratum.baseline_land_use
                            and f.management_regime == stratum.baseline_management]
        baseline_stock_tC_ha = calculate_ipcc_stock(baseline_factors[0]) if baseline_factors else 0.0

        # Eligibility Period
        start_year = stratum.eligibility_start_date.year if stratum.eligibility_start_date else current_year
        
        # Track history for resampling logic
        delta_history = []
        last_measured_stock = None
        
        for year in range(start_year, current_year + 1):
            n = year - start_year + 1
            
            # 1. Identify samples for this year
            year_samples = [s for s in samples 
                           if s.project_id == stratum.project_id 
                           and s.stratum_id == stratum.stratum_id
                           and s.sample_date.year == year]
            
            resampling_occurred = len(year_samples) > 0
            
            if resampling_occurred:
                last_measured_stock = aggregate_measured_to_stratum(year_samples, stratum.project_id, stratum.stratum_id, year)
                
            # 2. Determine S_curr
            if last_measured_stock is not None:
                s_curr = last_measured_stock
            else:
                # Use IPCC factor-based if never measured
                matching_factors = [f for f in factor_sets if f.climate_zone == stratum.climate_zone 
                                    and f.soil_type == stratum.soil_type
                                    and f.land_use_class == stratum.land_use_class
                                    and f.management_regime == stratum.management_regime]
                s_curr = calculate_ipcc_stock(matching_factors[0]) if matching_factors else baseline_stock_tC_ha

            # 3. Calculate Delta_n
            if n > transition_period:
                # Beyond transition period, assume no more incremental stock change from this practice change
                annual_change_tC_ha = 0.0
            elif not resampling_occurred and n == 1:
                # Initial year, default rule
                annual_change_tC_ha = (s_curr - baseline_stock_tC_ha) / transition_period
            elif resampling_occurred:
                # Resampling during transition period
                t_rem = transition_period - (n - 1)
                if t_rem > 0:
                    sum_prev_delta = sum(delta_history)
                    annual_change_tC_ha = (s_curr - baseline_stock_tC_ha - sum_prev_delta) / t_rem
                else:
                    # n exactly transition_period, t_rem=1 actually. 
                    # If n > transition_period handled above.
                    # Wait if n=transition_period, t_rem = transition_period - (transition_period - 1) = 1.
                    # So it's fine.
                    sum_prev_delta = sum(delta_history)
                    annual_change_tC_ha = (s_curr - baseline_stock_tC_ha - sum_prev_delta)
            else:
                # No resampling this year, but may have happened before.
                # If we use the same annual_change as last year (smooth allocation)
                if delta_history:
                    annual_change_tC_ha = delta_history[-1]
                else:
                    annual_change_tC_ha = (s_curr - baseline_stock_tC_ha) / transition_period

            delta_history.append(annual_change_tC_ha)
            
            # 4. Final Accounting for the year
            annual_change_tCO2e_ha = convert_tc_to_tco2e(annual_change_tC_ha)
            total_change_tCO2e = annual_change_tCO2e_ha * stratum.area_ha
            
            # Uncertainty & Conservatism
            uncertainty = config.default_uncertainty_pct
            deduction = config.default_conservative_deduction_pct
            
            # Apply conservative caps if needed (simplified: credit only if positive, or full deduction if negative)
            if total_change_tCO2e > 0:
                creditable = total_change_tCO2e * (1 - deduction)
            else:
                # Negative change is a deduction without "discount" (conservative)
                creditable = total_change_tCO2e 
            
            results.append(SOCResult(
                project_id=stratum.project_id,
                stratum_id=stratum.stratum_id,
                year=year,
                soc_stock_tC_ha=s_curr,
                soc_stock_tCO2e_ha=convert_tc_to_tco2e(s_curr),
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
