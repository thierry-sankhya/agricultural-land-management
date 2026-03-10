# IAML Carbon Accounting: Technical Blueprint & Package Design

## 1. Introduction
This document outlines the technical design for the `iaml_carbon` module, a specialized Python library for quantifying Greenhouse Gas (GHG) emission reductions and carbon removals from Improved Agricultural Land Management (IALM).

The focus is on Soil Organic Carbon (SOC) and compatibility with regenerative agriculture projects, providing a modular, audit-ready framework for carbon benefit quantification.

## 2. Scope & Applicability
The module supports projects implementing:
- Improved fertilizer management (N2O reductions)
- Improved water management / irrigation (CH4/CO2 reductions)
- Reduced tillage / improved residue management (SOC preservation/increase)
- Improved crop planting (cover crops, rotations, agroforestry)
- Improved grazing practices (SOC and CH4 management)

## 3. Carbon-Benefit Components & Quantification Options

| Component | What is Measured | Units | Type | Activity Data | Quantification Pathways |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **SOC Stock** | Soil Organic Carbon content | tCO2e/ha | Removal | Land use, tillage, residue, amendments | Sample+Resample, Sample+Model, Model+Calibration |
| **N2O (Fertilizer)** | Nitrogen application rate/type | tCO2e/yr | Reduction | Fertilizer type, amount, timing, placement | Activity data + Emission Factors (IPCC Tier 1/2) |
| **CH4 (Rice/Water)** | Flooding duration/regime | tCO2e/yr | Reduction | Irrigation logs, water levels, soil type | Model-based (DNDC/DayCent) or RS proxies |
| **CH4 (Grazing)** | Enteric fermentation / Manure | tCO2e/yr | Reduction | Herd size, diet, manure mgmt system | Tier 1/2 Emission Factors, Model-based diet analysis |
| **CO2 (Energy)** | Fuel/Electricity consumption | tCO2e/yr | Reduction | Fuel logs, utility bills, pump specs | Activity data + Fuel-specific Emission Factors |
| **Biomass (Agro)** | Tree/Shrub growth | tCO2e/ha | Removal | Species, DBH, height, planting density | Allometric equations, RS-based canopy height |

## 4. Baseline & Additionality Requirements

| Component | Baseline Requirement | Additionality Logic |
| :--- | :--- | :--- |
| **SOC** | Historical SOC levels or Modeled Counterfactual | Performance-based or Practice-based shift |
| **N2O** | Historical fertilizer application rates (3-5yr) | Reduction below historical or regional benchmark |
| **CH4** | Practice-as-usual (e.g., continuous flooding) | Adoption of AWD or improved drainage |
| **CO2** | Historical energy intensity per unit output | Technology upgrade or reduced pump hours |
| **Biomass** | Existing woody biomass stock (Pre-project) | Net increase in perennial woody cover |

## 5. Quantification Pathways
1.  **Sample + Resample SOC:** Physical soil cores at Year 0 and Year N. High accuracy, high cost.
2.  **Sample + Model SOC:** Initial samples to set baseline, followed by process-based modeling (e.g., RothC, DayCent).
3.  **Model + Periodic Calibration:** Continuous modeling with physical sampling every 5 years for "ground-truthing".
4.  **Activity Data + Emission Factors:** Standard IPCC or regional factors applied to management records (e.g., kg N applied).
5.  **Remote Sensing + Field Calibration:** RS-derived indices (NDVI, bare soil spectra) for tillage, cover crop, and residue monitoring.

## 6. Implementation Roadmap
- **Phase 1: Foundation.** Core data model (Project, Strata, PracticeChange) + Basic SOC and N2O/CO2 calculators.
- **Phase 2: Rigor.** Uncertainty quantification, baseline scenario generation, and additionality logic.
- **Phase 3: Integration.** Remote sensing interfaces, climate event tracking, and grazing/agroforestry extensions.
- **Phase 4: Issuance & Value.** Credit issuance logic and integration with Carbon Accumulation Fund valuation.

## 7. Testing Strategy
- **Unit Tests:** Individual calculation engines (e.g., N2O emission factor application).
- **Integration Tests:** End-to-end quantification from ManagementSchedule to AnnualNetGHG.
- **Data Validation Tests:** Schema checks for SoilSample and ManagementRecords.
- **Scenario Tests:** Comparison of project vs. counterfactual baseline results.
