from pathlib import Path
import numpy as np
import pandas as pd

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_MOBILE_PATH = BASE_DIR / "MD - ecometer" / "app" / "src" / "main" / "ml" / "model2.tflite"
MODEL_ML_PATH = BASE_DIR / "ML - model" / "model.tflite"
DATASET_VEHICLES_PATH = (
    BASE_DIR / "Dataset" / "Data Emisi" / "Data Penggunaan Transportasi" / "CO2 Emission by Vehicles" / "CO2 Emissions_Canada.csv"
)
DATASET_FOOTPRINT_PATH = (
    BASE_DIR / "Dataset" / "Data Emisi" / "Individual Carbon Footprint Calculation.csv"
)
DATASET_GLOBAL_ENERGY_PATH = (
    BASE_DIR / "Dataset" / "Data Emisi" / "Global Data on Sustainable Energy (2000-2020).csv"
)

# Interpreter Cache
_interpreter_cache = {}

def get_interpreter(model_path: Path):
    """Load and cache TFLite interpreter using ai-edge-litert."""
    path_str = str(model_path)
    if path_str not in _interpreter_cache:
        try:
            import ai_edge_litert.interpreter as tflite
            interpreter = tflite.Interpreter(model_path=path_str)
            interpreter.allocate_tensors()
            _interpreter_cache[path_str] = interpreter
        except Exception as e:
            print(f"Failed to load model {model_path}: {e}")
            return None
    return _interpreter_cache.get(path_str)


def predict_emissions_tflite(
    vehicle_type: str,
    engine_capacity_cc: float,
    cylinder_count: int,
    fuel_class: str,
    distance_km: float
) -> tuple[float, float]:
    """
    Calculates CO2 emission using the EcoMeter TFLite model.
    Returns: (rate_g_per_km, total_g_co2)
    """
    model_path = MODEL_MOBILE_PATH if MODEL_MOBILE_PATH.exists() else MODEL_ML_PATH
    interpreter = get_interpreter(model_path)

    # Convert fuel class to numerical score following mobile app logic
    if vehicle_type == "Car":
        fuel_map = {
            "Small (Up to 1500 cc)": 7.0,
            "Medium (Up to 3000 cc)": 10.0,
            "Large (Over 3000 cc)": 15.0
        }
        fuel_val = fuel_map.get(fuel_class, 7.0)
    else:
        fuel_map = {
            "125 cc or less": 2.0,
            "250 cc": 3.5,
            "500 cc or more": 5.0
        }
        fuel_val = fuel_map.get(fuel_class, 2.0)

    engine_liters = engine_capacity_cc / 1000.0

    if interpreter is not None:
        try:
            min_v = min(engine_liters, float(cylinder_count), fuel_val)
            max_v = max(engine_liters, float(cylinder_count), fuel_val)
            diff = max_v - min_v if max_v != min_v else 1.0

            norm_eng = (engine_liters - min_v) / diff
            norm_cyl = (float(cylinder_count) - min_v) / diff
            norm_fuel = (fuel_val - min_v) / diff

            input_data = np.array([[norm_eng, norm_cyl, norm_fuel]], dtype=np.float32)

            in_idx = interpreter.get_input_details()[0]["index"]
            out_idx = interpreter.get_output_details()[0]["index"]

            interpreter.set_tensor(in_idx, input_data)
            interpreter.invoke()
            g_per_km = float(interpreter.get_tensor(out_idx)[0][0])
            # Keep within physically grounded bounds
            g_per_km = max(40.0, min(g_per_km, 600.0))
        except Exception:
            # Fallback empirical standard if inference fails
            g_per_km = (engine_liters * 45.0) + (cylinder_count * 15.0) + (fuel_val * 8.0)
    else:
        # Fallback empirical calculation
        g_per_km = (engine_liters * 45.0) + (cylinder_count * 15.0) + (fuel_val * 8.0)

    total_g = g_per_km * distance_km
    return round(g_per_km, 2), round(total_g, 2)


def get_emission_equivalents(total_g_co2: float) -> dict:
    """Calculates practical environmental equivalents for a given CO2 amount."""
    kg_co2 = total_g_co2 / 1000.0
    # An average mature tree absorbs ~22 kg of CO2 per year (~60 g per day)
    trees_needed_yearly = kg_co2 / 22.0
    # Average gasoline combustion emits ~2,310 grams CO2 per liter
    liters_gasoline = total_g_co2 / 2310.0
    # Average smartphone full charge is ~8.22 grams CO2
    smartphone_charges = total_g_co2 / 8.22

    return {
        "kg_co2": round(kg_co2, 3),
        "trees_yearly": round(trees_needed_yearly, 3),
        "liters_gasoline": round(liters_gasoline, 2),
        "smartphone_charges": int(smartphone_charges)
    }


def get_travel_mode_comparison(distance_km: float, current_total_g: float) -> list[dict]:
    """Compares the current trip against other common transit options."""
    # Average emission factors (g CO2 / passenger-km)
    modes = [
        {"Mode": "Electric Train / Metro", "Factor": 28.0},
        {"Mode": "City Bus (Transit)", "Factor": 82.0},
        {"Mode": "Motorcycle (125cc)", "Factor": 72.0},
        {"Mode": "Average Petrol Car", "Factor": 192.0},
        {"Mode": "Bicycle / Walking", "Factor": 0.0},
    ]

    results = []
    for m in modes:
        emissions_g = m["Factor"] * distance_km
        diff_g = emissions_g - current_total_g
        results.append({
            "Mode": m["Mode"],
            "Trip CO2 (g)": round(emissions_g, 1),
            "Trip CO2 (kg)": round(emissions_g / 1000.0, 2),
            "Difference vs Current (g)": round(diff_g, 1)
        })
    return results


def load_vehicle_catalog() -> pd.DataFrame:
    """Loads Canada Vehicle Emissions dataset."""
    if DATASET_VEHICLES_PATH.exists():
        df = pd.read_csv(DATASET_VEHICLES_PATH)
        return df
    return pd.DataFrame()


def load_footprint_dataset() -> pd.DataFrame:
    """Loads Individual Carbon Footprint dataset."""
    if DATASET_FOOTPRINT_PATH.exists():
        df = pd.read_csv(DATASET_FOOTPRINT_PATH)
        return df
    return pd.DataFrame()


def load_global_energy_dataset() -> pd.DataFrame:
    """Loads Global Sustainable Energy dataset."""
    if DATASET_GLOBAL_ENERGY_PATH.exists():
        df = pd.read_csv(DATASET_GLOBAL_ENERGY_PATH)
        return df
    return pd.DataFrame()
