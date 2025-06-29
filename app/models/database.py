"""Database models for SMR monitoring system"""

from sqlalchemy import Column, Integer, Float, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class ReactorReadingDB(Base):
    """Database model for reactor readings"""
    __tablename__ = "reactor_readings"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    core_temp = Column(Float, nullable=False)
    coolant_temp = Column(Float, nullable=False)
    pressure = Column(Float, nullable=False)
    neutron_flux = Column(Float, nullable=False)
    control_rod_position = Column(Float, nullable=False)
    coolant_flow_rate = Column(Float, nullable=False)
    steam_pressure = Column(Float, nullable=False)


class AnomalyAlertDB(Base):
    """Database model for anomaly alerts"""
    __tablename__ = "anomaly_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    parameter = Column(String(50), nullable=False)
    value = Column(Float, nullable=False)
    anomaly_score = Column(Float, nullable=False)
    severity = Column(String(20), nullable=False)
    description = Column(Text, nullable=False)


class SystemMetrics(Base):
    """Database model for system metrics"""
    __tablename__ = "system_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    total_readings = Column(Integer, default=0)
    total_alerts = Column(Integer, default=0)
    uptime_seconds = Column(Float, default=0.0)
    last_anomaly_detection = Column(DateTime, nullable=True)
