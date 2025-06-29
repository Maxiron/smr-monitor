"""SMR data simulation service"""

import numpy as np
from datetime import datetime
from typing import List
from app.models.schemas import ReactorReading


class SMRDataSimulator:
    """Generates realistic SMR operational data"""
    
    def __init__(self):
        # Normal operating ranges for SMR
        self.normal_ranges = {
            'core_temp': (285, 295),      # °C
            'coolant_temp': (250, 270),   # °C  
            'pressure': (15.5, 16.5),     # MPa
            'neutron_flux': (1e13, 5e13), # neutrons/cm²/s
            'control_rod_position': (70, 85), # % withdrawn
            'coolant_flow_rate': (200, 250),  # kg/s
            'steam_pressure': (6.8, 7.2)      # MPa
        }
        
        # Current state for smooth transitions
        self.current_state = {
            'core_temp': 290,
            'coolant_temp': 260,
            'pressure': 16.0,
            'neutron_flux': 3e13,
            'control_rod_position': 78,
            'coolant_flow_rate': 225,
            'steam_pressure': 7.0
        }
        
    def generate_reading(self, inject_anomaly: bool = False) -> ReactorReading:
        """Generate a single reactor reading"""
        
        for param, (min_val, max_val) in self.normal_ranges.items():
            if inject_anomaly and np.random.random() < 0.1:  # 10% chance of anomaly
                # Inject anomaly - values outside normal range
                if np.random.random() < 0.5:
                    self.current_state[param] = min_val - (max_val - min_val) * 0.3
                else:
                    self.current_state[param] = max_val + (max_val - min_val) * 0.3
            else:
                # Normal operation with small random walk
                target = np.random.uniform(min_val, max_val)
                # Smooth transition to target
                self.current_state[param] += (target - self.current_state[param]) * 0.1
                # Add small noise
                self.current_state[param] += np.random.normal(0, (max_val - min_val) * 0.02)
        
        return ReactorReading(
            timestamp=datetime.now(),
            **self.current_state
        )
    
    def generate_batch_readings(self, count: int, inject_anomalies: bool = False) -> List[ReactorReading]:
        """Generate multiple readings for training purposes"""
        return [
            self.generate_reading(inject_anomaly=inject_anomalies)
            for _ in range(count)
        ]
