import csv
import yaml
from datetime import datetime, date
from typing import List, Dict, Any
from ialm_carbon.domain.soc_entities import SOCSample, SOCStratum
from ialm_carbon.methods.soc.model_spec import SOCModelSpec
from ialm_carbon.methods.soc.factor_sets import SOCFactorSet

def parse_date(date_str: str) -> date:
    if not date_str:
        return None
    for fmt in ('%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y'):
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Unknown date format: {date_str}")

def load_soc_samples(filepath: str) -> List[SOCSample]:
    samples = []
    encodings = ['utf-8-sig', 'utf-8', 'latin-1', 'cp1252']
    
    def open_with_encodings(path):
        for enc in encodings:
            try:
                with open(path, mode='r', encoding=enc) as f:
                    content = f.read()
                return content, enc
            except UnicodeDecodeError:
                continue
        raise ValueError(f"Could not decode {path}")

    content, enc = open_with_encodings(filepath)
    import io
    reader = csv.DictReader(io.StringIO(content))
    for row in reader:
        samples.append(SOCSample(
            sample_id=row['sample_id'],
            project_id=row['project_id'],
            stratum_id=row['stratum_id'],
            plot_id=row['plot_id'],
            sample_event_id=row['sample_event_id'],
            sample_date=parse_date(row['sample_date']),
            depth_top_cm=float(row['depth_top_cm']),
            depth_bottom_cm=float(row['depth_bottom_cm']),
            soc_percent=float(row['soc_percent']),
            bulk_density_g_cm3=float(row['bulk_density_g_cm3']),
            coarse_fragment_vol_frac=float(row['coarse_fragment_vol_frac']),
            texture_class=row['texture_class'],
            lab_method=row['lab_method'],
            latitude=float(row['latitude']),
            longitude=float(row['longitude']),
            qa_status=row['qa_status'],
            soil_moisture_pct=float(row['soil_moisture_pct']) if row.get('soil_moisture_pct') else None,
            ph=float(row['ph']) if row.get('ph') else None,
            notes=row.get('notes')
        ))
    return samples

def load_strata(filepath: str) -> List[SOCStratum]:
    strata = []
    # Try multiple encodings
    encodings = ['utf-8-sig', 'utf-8', 'latin-1', 'cp1252']
    for encoding in encodings:
        try:
            with open(filepath, mode='r', encoding=encoding) as f:
                reader = csv.DictReader(f)
                for row in reader:
                    strata.append(SOCStratum(
                        stratum_id=row['stratum_id'],
                        project_id=row['project_id'],
                        area_ha=float(row['area_ha']),
                        climate_zone=row['climate_zone'],
                        soil_type=row['soil_type'],
                        land_use_class=row['land_use_class'],
                        management_regime=row['management_regime'],
                        input_regime=row['input_regime'],
                        water_regime=row['water_regime'],
                        baseline_land_use=row['baseline_land_use'],
                        baseline_management=row['baseline_management'],
                        stratum_name=row.get('stratum_name'),
                        grazing_regime=row.get('grazing_regime'),
                        agroforestry_system=row.get('agroforestry_system'),
                        eligibility_start_date=parse_date(row.get('eligibility_start_date')),
                        notes=row.get('notes')
                    ))
                return strata
        except UnicodeDecodeError:
            strata = []
            continue
    raise ValueError(f"Could not decode {filepath} with any of the encodings {encodings}")

def load_model_config(filepath: str) -> SOCModelSpec:
    with open(filepath, mode='r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
        return SOCModelSpec(
            project_id=config['project_id'],
            accounting_mode=config['accounting_mode'],
            transition_period_years=config.get('transition_period_years', 20),
            default_uncertainty_pct=config.get('default_uncertainty_pct', 0.15),
            default_conservative_deduction_pct=config.get('default_conservative_deduction_pct', 0.10),
            depth_standard_cm=config.get('depth_standard_cm', 30.0)
        )

def load_factor_sets(filepath: str, ref_stocks_filepath: str) -> List[SOCFactorSet]:
    ref_stocks = {}
    encodings = ['utf-8-sig', 'utf-8', 'latin-1', 'cp1252']
    
    def open_with_encodings(path):
        for enc in encodings:
            try:
                # Read all lines to check for decoding errors
                with open(path, mode='r', encoding=enc) as f:
                    content = f.read()
                return content, enc
            except UnicodeDecodeError:
                continue
        raise ValueError(f"Could not decode {path}")

    ref_content, ref_enc = open_with_encodings(ref_stocks_filepath)
    import io
    reader = csv.DictReader(io.StringIO(ref_content))
    for row in reader:
        ref_stocks[(row['climate_zone'], row['soil_type'])] = float(row['soc_ref_tC_ha'])
    
    factor_content, factor_enc = open_with_encodings(filepath)
    factor_sets = []
    reader = csv.DictReader(io.StringIO(factor_content))
    for row in reader:
        climate = row['climate_zone'] if 'climate_zone' in row else None
        
        for (cz, st), ref_val in ref_stocks.items():
            if climate is None or cz == climate:
                factor_sets.append(SOCFactorSet(
                    climate_zone=cz,
                    soil_type=st,
                    land_use_class=row['land_use_class'],
                    management_regime=row['management_regime'],
                    input_regime=row['input_regime'],
                    water_regime=row['water_regime'],
                    soc_ref_tC_ha=ref_val,
                    flu=float(row['flu']),
                    fmg=float(row['fmg']),
                    fi=float(row['fi']),
                    depth_basis_cm=30.0
                ))
    return factor_sets
