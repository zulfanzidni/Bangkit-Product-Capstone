import sys
from pathlib import Path

# Add project root to sys.path
root = Path(__file__).resolve().parent.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

print("Testing imports...")
from streamlit_app import utils
from streamlit_app import calculator
from streamlit_app import lifestyle
from streamlit_app import catalog
from streamlit_app import global_trends
from streamlit_app import app

print("Testing inference...")
rate, total = utils.predict_emissions_tflite("Car", 1500, 4, "Small (Up to 1500 cc)", 20.0)
print(f"Prediction success: {rate} g/km, {total} g total")

print("Testing datasets...")
df_v = utils.load_vehicle_catalog()
print(f"Vehicles: {df_v.shape}")
df_f = utils.load_footprint_dataset()
print(f"Footprint: {df_f.shape}")
df_g = utils.load_global_energy_dataset()
print(f"Global Energy: {df_g.shape}")

print("ALL VERIFICATIONS PASSED SUCCESSFULLY!")
