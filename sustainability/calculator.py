# SPDX-FileCopyrightText: Copyright (c) 2026. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import json
import os
from pathlib import Path
from dataclasses import dataclass
from typing import Any, Dict, Optional

@dataclass
class HardwareProfile:
    name: str
    flops_per_watt: float # Efficiency (GFLOPS/Watt)

class CarbonCalculator:
    # Standard Grid Intensities (gCO2e / kWh)
    GRID_INTENSITY = {
        "GLOBAL_AVG": 475.0, # IEA Global Average
        "US_AVG": 380.0,
        "EU_AVG": 255.0,
        "SWEDEN": 45.0,      # Hydro/Nuclear heavy (Green)
        "COAL_HEAVY": 820.0  # Regions relying on coal
    }

    # Hardware Efficiency Profiles (Real-world FP16 inference estimates)
    # Using the provided values, adjusted for consistency
    HARDWARE = {
        "NVIDIA_A100": HardwareProfile("NVIDIA A100", 150.0e9), # 150 GFLOPS/Watt
        "NVIDIA_H100": HardwareProfile("NVIDIA H100", 250.0e9), # ~250 GFLOPS/Watt
        "CONSUMER_GPU": HardwareProfile("RTX 4090", 50.0e9),    # Less efficient per watt
    }

    def __init__(self, hardware: str = "NVIDIA_A100", region: str = "GLOBAL_AVG", reference_data_path: Optional[str] = None):
        self.hardware = self.HARDWARE.get(hardware, self.HARDWARE["NVIDIA_A100"])
        self.grid_intensity = self.GRID_INTENSITY.get(region, 475.0)
        
        if reference_data_path is None:
            reference_data_path = str(Path(__file__).parent / "reference_data.json")
        
        self.reference_data = self._load_reference_data(reference_data_path)

    def _load_reference_data(self, path: str) -> list:
        if not os.path.exists(path):
            return []
        try:
            with open(path, "r") as f:
                return json.load(f)
        except Exception:
            return []

    def get_model_energy_factor(self, model_name: str) -> Optional[float]:
        """Returns energy_factor_wh_per_1k if found in reference_data."""
        for provider in self.reference_data:
            for variant in provider.get("variants", []):
                if variant["model_name"].lower() == model_name.lower():
                    return variant.get("energy_factor_wh_per_1k")
        return None

    def calculate_emissions(self, total_tokens: int, param_count_billions: Optional[float] = None, model_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Returns a dictionary of impact metrics.
        total_tokens: Input + Output tokens
        param_count_billions: e.g., 70 for Llama-3-70B (Optional if model_name is provided)
        model_name: Optional, used to look up energy factors in reference_data.json
        """
        
        energy_kwh = 0.0
        method = "unknown"

        # Priority 1: Use model-specific energy factor from reference_data.json
        if model_name:
            factor = self.get_model_energy_factor(model_name)
            if factor is not None:
                # factor is Watt-hours per 1k tokens
                energy_wh = (total_tokens / 1000.0) * factor
                energy_kwh = energy_wh / 1000.0
                method = f"model_reference ({model_name})"

        # Priority 2: Use FLOPs-based calculation if param_count is known and model lookup failed
        if energy_kwh == 0.0 and param_count_billions is not None:
            # 1. Calculate Compute Load (FLOPs)
            # Formula: 2 * Parameters * Tokens
            N = param_count_billions * 1e9
            total_flops = 2 * N * total_tokens
            
            # 2. Calculate Energy (Joules & kWh)
            energy_joules = total_flops / self.hardware.flops_per_watt
            energy_kwh = energy_joules / 3_600_000 # 3.6M Joules in 1 kWh
            method = f"hardware_flops ({self.hardware.name})"
        
        # 3. Calculate Carbon (Grams)
        carbon_grams = energy_kwh * self.grid_intensity
        
        # 4. Contextualize (Smartphone Charges)
        # Standard phone battery ~ 15 Wh = 0.015 kWh
        phone_charges = energy_kwh / 0.015

        return {
            "model_info": model_name or (f"{param_count_billions}B" if param_count_billions else "Unknown"),
            "total_tokens": total_tokens,
            "energy_kwh": round(energy_kwh, 8),
            "carbon_g": round(carbon_grams, 6),
            "phone_charges": round(phone_charges, 4),
            "calculation_method": method
        }

# Global instance for easy access
sustainability_calculator = CarbonCalculator()
