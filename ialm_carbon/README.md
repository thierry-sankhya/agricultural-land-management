# CarbonIQ IAML Carbon Accounting Package (`ialm_carbon`)

## Overview
CarbonIQ `ialm_carbon` package is a modular Python library designed for quantifying GHG emission reductions and carbon removals from Improved Agricultural Land Management (IALM) projects. It is specifically designed to handle Soil Organic Carbon (SOC) and other agricultural GHG components (N2O, CH4, CO2) in a way that is production-ready and audit-friendly.

## Package Structure
- `domain/`: Core entities and data models. Includes `soc_entities.py` for SOC specific data structures (now with extended grazing, agroforestry, and soil property fields).
- `methods/`: Quantification engines.
    - `soc/`: Soil Organic Carbon stock change accounting (Measured, Factor-based, and Hybrid modes).
- `io/`: Robust data loaders supporting multiple encodings (BOM-aware) and date formats.
    - `n2o/`: Nitrous Oxide reductions from fertilizer management.
    - `ch4/`: Methane reductions from water and grazing management.
    - `co2_energy/`: CO2 reductions from energy/fuel efficiency.
    - `annual_accounting.py`: Aggregation engine for net-GHG benefits.
- `baselines/`: Logic for generating and maintaining baseline scenarios.
- `additionality/`: Checks for project additionality.
- `geospatial/`: Remote sensing and boundary verification support.
- `monitoring/`: Management of monitoring events and records.
- `uncertainty/`: Uncertainty quantification and deductions.
- `valuation/`: Integration with the Carbon Accumulation Fund valuation layer.
- `tests/`: Comprehensive unit and integration test suite.

## Getting Started
### Core Entities
The project uses dataclasses to represent core carbon accounting concepts. See `ialm_carbon/domain/soc_entities.py`.

### SOC Accounting Logic

#### 1. Transition Period (`transition_period_years`)
The `transition_period_years` (T) defines the duration over which the Soil Organic Carbon (SOC) stock change resulting from a practice change is expected to occur. It is sourced using the following hierarchy:
1.  **Stratum Level**: Value from `transition_period_years` column in `strata.csv`.
2.  **Impact-Based Fallback**: If missing, it is derived from the `soc_impact` field using the `transition_period_years_map` in `soc_model_config.yaml` (averaging the defined range).
    *   `high_impact`: [3, 5] (Avg: 4 years)
    *   `moderate_impact`: [5, 7] (Avg: 6 years)
    *   `low_impact`: [7, 12] (Avg: 9.5 years)
    *   `slow_impact`: [10, 15] (Avg: 12.5 years)
3.  **Global Default**: Fallback to the global `transition_period_years` in `soc_model_config.yaml` (default: 20 years).

#### 2. Annual Stock Change Calculation (`annual_change_tC_ha`)
The package implements a dynamic allocation algorithm to distribute the observed or modeled stock change over the transition period.

**Case A: Default Rule (No Resampling)**
If no new measurement occurs in a given year $n$, the annual change is calculated as:
$$\Delta_{n} = \frac{S_{\text{curr}} - S_{\text{base}}}{T}$$
Where $S_{\text{curr}}$ is the target stock (measured or factor-based) and $S_{\text{base}}$ is the baseline stock.

**Case B: Resampling During Transition Period**
If a new measurement ($S_{\text{new}}$) is taken during the transition period (year $n$), the remaining allocation is updated:
$$\Delta_{n}^{\text{updated}} = \frac{S_{\text{new}} - S_{\text{base}} - \sum_{i=1}^{n-1}\Delta_{i}}{T_{\text{rem}}}$$
Where $T_{\text{rem}} = T - (n-1)$ is the number of years remaining in the transition period. 
*   **Retrospective Adjustment**: If $\Delta_{n}^{\text{updated}}$ is lower than previously credited amounts, a deduction is applied to avoid over-crediting.
*   **Conservative Caps**: If higher, standard conservative deductions (e.g., 10%) are applied to the incremental gain.

### Accounting Example
```python
from ialm_carbon.methods.soc.soc_engine import SOCAccounting
from ialm_carbon.methods.annual_accounting import GHGAccountingEngine

# Initialize engines
soc_engine = SOCAccounting(baseline_samples)
ghg_engine = GHGAccountingEngine(project_id="my_project")

# Calculate SOC change
soc_change = soc_engine.calculate_stock_change(current_samples)

# Calculate N2O reductions
n2o_red = ghg_engine.calculate_annual_n2o_reductions(baseline_n, project_n)

# Aggregate to net benefit
net_benefit = ghg_engine.compute_net_annual_benefit(stratum_id, year, soc_change, n2o_red, co2_red)
```

## Planned Implementation Phases
1. **Phase 1: Foundation.** Core data model + Basic SOC and N2O/CO2 calculators. (COMPLETED)
2. **Phase 2: Rigor.** Uncertainty quantification, baseline scenario generation, and additionality logic.
3. **Phase 3: Integration.** Remote sensing interfaces, climate event tracking, and grazing/agroforestry extensions.
4. **Phase 4: Issuance & Value.** Credit issuance logic and integration with Carbon Accumulation Fund valuation.

## Demo Project Details
The `demo_soc_accounting.py` script processes two distinct projects using a hybrid (measured + factor-based) approach.

### Project 1: PRJ_001 (USA - Warm Temperate Dry)
*   **Stratum A**: Loam cropland transition from full-till to reduced-till with cover cropping. (125.4 ha)
*   **Stratum B**: Clay loam cropland under conventional tillage. (89.7 ha)
*   **Data Files**:
    *   `strata.csv`: Defines soil types (HAC_loam, HAC_clay_loam) and management regimes.
    *   `soc_samples.csv`: Contains 2026 monitoring data for both strata.
    *   `soc_reference_stocks.csv` & `soc_stock_change_factors.csv`: Provide IPCC-aligned reference values and multipliers.

### Project 2: PRJ_002 (Australia - Warm Temperate Moist)
*   **Stratum A**: Sandy grassland (Tenosol) transition from continuous grazing to rotational grazing (started 2024). (150 ha)
*   **Data Files**:
    *   `strata.csv`: Specifies `warm_temperate_moist` climate and `sandy_loam (Tenosol)` soil.
    *   `soc_samples.csv`: Includes baseline samples (2023) and new project-period samples (2026) for resampling logic demonstration.

## PDF Generation Instructions
To generate a high-quality PDF version of this documentation (`README.pdf`), follow these steps on a Windows environment with Pandoc and Microsoft Edge installed:

1.  **Convert Markdown to HTML**: Use Pandoc with `--standalone` and `--embed-resources` flags to ensure all content (including math if supported or required assets) is bundled.
    ```powershell
    pandoc -f markdown -t html ialm_carbon/README.md -o ialm_carbon/README.html --standalone --embed-resources --metadata title="CarbonIQ IAML Carbon Accounting Package"
    ```
2.  **Print HTML to PDF**: Use Microsoft Edge in headless mode for reliable rendering of the standalone HTML.
    ```powershell
    & "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --headless --print-to-pdf="C:\Full\Path\To\ialm_carbon\README.pdf" "file:///C:/Full/Path/To/ialm_carbon/README.html"
    ```
3.  **Cleanup**: Remove the temporary HTML file.
    ```powershell
    rm ialm_carbon/README.html
    ```
