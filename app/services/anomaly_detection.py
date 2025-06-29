"""Anomaly detection service using machine learning"""

import numpy as np
import pandas as pd
from datetime import datetime
from typing import List, Optional
from dataclasses import asdict
import joblib
import os

from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from app.models.schemas import ReactorReading, AnomalyAlert
from app.config import settings


class AnomalyDetector:
    """ML-based anomaly detection for reactor parameters"""
    
    def __init__(self):
        self.model = IsolationForest(
            contamination=settings.anomaly_threshold,
            random_state=42,
            n_estimators=100
        )
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_columns = [
            'core_temp', 'coolant_temp', 'pressure', 'neutron_flux',
            'control_rod_position', 'coolant_flow_rate', 'steam_pressure'
        ]
        
        # Normal operating ranges for deviation calculation
        self.normal_ranges = {
            'core_temp': (285, 295),
            'coolant_temp': (250, 270),
            'pressure': (15.5, 16.5),
            'neutron_flux': (1e13, 5e13),
            'control_rod_position': (70, 85),
            'coolant_flow_rate': (200, 250),
            'steam_pressure': (6.8, 7.2)
        }
        
        # Try to load existing model
        self._load_model()
        
    def prepare_features(self, readings: List[ReactorReading]) -> np.ndarray:
        """Convert readings to feature matrix"""
        df = pd.DataFrame([asdict(reading) for reading in readings])
        return df[self.feature_columns].values
        
    def train(self, historical_readings: List[ReactorReading]):
        """Train the anomaly detection model"""
        if len(historical_readings) < 100:
            print(f"Warning: Training with only {len(historical_readings)} samples")
            
        features = self.prepare_features(historical_readings)
        features_scaled = self.scaler.fit_transform(features)
        self.model.fit(features_scaled)
        self.is_trained = True
        
        # Save model
        self._save_model()
        print(f"Anomaly detection model trained with {len(historical_readings)} samples")
        
    def detect_anomaly(self, reading: ReactorReading) -> Optional[AnomalyAlert]:
        """Detect if a reading is anomalous"""
        if not self.is_trained:
            return None
            
        features = self.prepare_features([reading])
        features_scaled = self.scaler.transform(features)
        
        # Get anomaly score
        anomaly_score = self.model.decision_function(features_scaled)[0]
        is_anomaly = self.model.predict(features_scaled)[0] == -1
        
        if is_anomaly:
            # Determine which parameter is most anomalous
            reading_dict = asdict(reading)
            severity = self._determine_severity(anomaly_score)
            anomalous_param = self._find_most_anomalous_parameter(reading_dict)
            
            return AnomalyAlert(
                timestamp=reading.timestamp,
                parameter=anomalous_param,
                value=reading_dict.get(anomalous_param, 0),
                anomaly_score=anomaly_score,
                severity=severity,
                description=f"Anomalous {anomalous_param} detected: {reading_dict.get(anomalous_param, 0):.2f}"
            )
        
        return None
    
    def _determine_severity(self, anomaly_score: float) -> str:
        """Determine alert severity based on anomaly score"""
        if anomaly_score < -0.7:
            return "CRITICAL"
        elif anomaly_score < -0.5:
            return "HIGH"
        elif anomaly_score < -0.3:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _find_most_anomalous_parameter(self, reading_dict: dict) -> str:
        """Find the parameter that deviates most from normal range"""
        max_deviation = 0
        anomalous_param = "unknown"
        
        for param, (min_val, max_val) in self.normal_ranges.items():
            if param in reading_dict:
                value = reading_dict[param]
                if value < min_val:
                    deviation = (min_val - value) / (max_val - min_val)
                elif value > max_val:
                    deviation = (value - max_val) / (max_val - min_val)
                else:
                    deviation = 0
                    
                if deviation > max_deviation:
                    max_deviation = deviation
                    anomalous_param = param
        
        return anomalous_param
    
    def _save_model(self):
        """Save the trained model and scaler"""
        try:
            os.makedirs("models", exist_ok=True)
            joblib.dump(self.model, "models/anomaly_model.pkl")
            joblib.dump(self.scaler, "models/scaler.pkl")
        except Exception as e:
            print(f"Failed to save model: {e}")
    
    def _load_model(self):
        """Load existing model and scaler"""
        try:
            if os.path.exists("models/anomaly_model.pkl") and os.path.exists("models/scaler.pkl"):
                self.model = joblib.load("models/anomaly_model.pkl")
                self.scaler = joblib.load("models/scaler.pkl")
                self.is_trained = True
                print("Loaded existing anomaly detection model")
        except Exception as e:
            print(f"Failed to load existing model: {e}")
    
    def get_model_info(self) -> dict:
        """Get information about the current model"""
        return {
            "is_trained": self.is_trained,
            "contamination": settings.anomaly_threshold,
            "n_estimators": self.model.n_estimators if hasattr(self.model, 'n_estimators') else 100,
            "feature_columns": self.feature_columns
        }
