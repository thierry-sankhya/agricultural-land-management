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
The project uses dataclasses to represent core carbon accounting concepts. See `ialm_carbon/domain/entities.py`.

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

## Implementation Phases
1. **Phase 1: Foundation.** Core data model + Basic SOC and N2O/CO2 calculators. (COMPLETED)
2. **Phase 2: Rigor.** Uncertainty quantification, baseline scenario generation, and additionality logic.
3. **Phase 3: Integration.** Remote sensing interfaces, climate event tracking, and grazing/agroforestry extensions.
4. **Phase 4: Issuance & Value.** Credit issuance logic and integration with Carbon Accumulation Fund valuation.
