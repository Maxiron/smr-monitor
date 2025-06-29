"""Data models for SMR monitoring system"""

from datetime import datetime
from typing import Optional
from dataclasses import dataclass
from pydantic import BaseModel


@dataclass
class ReactorReading:
    """Reactor sensor reading data"""
    timestamp: datetime
    core_temp: float          # °C
    coolant_temp: float       # °C
    pressure: float           # MPa
    neutron_flux: float       # neutrons/cm²/s
    control_rod_position: float  # % withdrawn
    coolant_flow_rate: float  # kg/s
    steam_pressure: float     # MPa


@dataclass  
class AnomalyAlert:
    """Anomaly alert data"""
    timestamp: datetime
    parameter: str
    value: float
    anomaly_score: float
    severity: str
    description: str


# Pydantic models for API responses
class ReactorReadingResponse(BaseModel):
    """API response model for reactor readings"""
    timestamp: str
    core_temp: float
    coolant_temp: float
    pressure: float
    neutron_flux: float
    control_rod_position: float
    coolant_flow_rate: float
    steam_pressure: float


class AnomalyAlertResponse(BaseModel):
    """API response model for anomaly alerts"""
    timestamp: str
    parameter: str
    value: float
    anomaly_score: float
    severity: str
    description: str


class SystemStatusResponse(BaseModel):
    """API response model for system status"""
    status: str
    active_alerts: int
    last_reading: Optional[ReactorReadingResponse] = None
    uptime_seconds: float
    total_readings: int
