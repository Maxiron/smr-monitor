"""Core monitoring service that orchestrates data collection and analysis"""

import asyncio
from datetime import datetime, timedelta
from typing import List
from dataclasses import asdict

from app.config import settings
from app.services.simulator import SMRDataSimulator
from app.services.anomaly_detection import AnomalyDetector
from app.services.email_alerts import EmailAlertService
from app.services.websocket_manager import ConnectionManager
from app.database import db_manager
from app.models.schemas import ReactorReading, AnomalyAlert


class MonitoringService:
    """Core service that coordinates all monitoring activities"""
    
    def __init__(self):
        self.simulator = SMRDataSimulator()
        self.anomaly_detector = AnomalyDetector()
        self.email_service = EmailAlertService()
        self.websocket_manager = ConnectionManager()
        
        # Runtime state
        self.is_running = False
        self.start_time = None
        self.total_readings = 0
        self.total_alerts = 0
        self.last_training_time = None
        
        # Background tasks
        self.monitoring_task = None
        self.cleanup_task = None
    
    async def initialize(self):
        """Initialize the monitoring service"""
        print("Initializing SMR Monitoring Service...")
        
        # Initialize database
        await db_manager.init_db()
        
        # Check if we need to train the model
        if not self.anomaly_detector.is_trained:
            await self._initial_training()
        
        self.start_time = datetime.now()
        print("SMR Monitoring Service initialized successfully!")
    
    async def start_monitoring(self):
        """Start the monitoring process"""
        if self.is_running:
            return
            
        self.is_running = True
        print("Starting continuous monitoring...")
        
        # Start background tasks
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        self.cleanup_task = asyncio.create_task(self._cleanup_loop())
        
        # Send startup notification
        await self.email_service.send_system_notification(
            "System Started",
            "SMR Safety Monitoring System has started successfully."
        )
    
    async def stop_monitoring(self):
        """Stop the monitoring process"""
        if not self.is_running:
            return
            
        self.is_running = False
        print("Stopping monitoring...")
        
        # Cancel background tasks
        if self.monitoring_task:
            self.monitoring_task.cancel()
        if self.cleanup_task:
            self.cleanup_task.cancel()
        
        # Send shutdown notification
        await self.email_service.send_system_notification(
            "System Shutdown",
            "SMR Safety Monitoring System is shutting down."
        )
    
    async def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.is_running:
            try:
                # Generate new reading
                reading = self.simulator.generate_reading(inject_anomaly=True)
                
                # Save to database
                await db_manager.save_reading(reading)
                self.total_readings += 1
                
                # Check for anomalies
                alert = self.anomaly_detector.detect_anomaly(reading)
                if alert:
                    await self._handle_anomaly(alert)
                
                # Broadcast reading to dashboard
                await self._broadcast_reading(reading)
                
                # Periodic model retraining
                await self._check_retraining()
                
                # Wait for next interval
                await asyncio.sleep(settings.data_collection_interval)
                
            except Exception as e:
                print(f"Error in monitoring loop: {e}")
                await asyncio.sleep(5)  # Back off on error
    
    async def _handle_anomaly(self, alert: AnomalyAlert):
        """Handle detected anomaly"""
        # Save alert to database
        await db_manager.save_alert(alert)
        self.total_alerts += 1
        
        print(f"🚨 ANOMALY DETECTED: {alert.description}")
        
        # Send email alert for high/critical severity
        if alert.severity in ["HIGH", "CRITICAL"]:
            # Use HTML email for critical alerts, plain text for high
            if alert.severity == "CRITICAL":
                await self.email_service.send_html_alert(alert)
            else:
                await self.email_service.send_alert(alert)
        
        # Broadcast alert to dashboard
        await self._broadcast_alert(alert)
    
    async def _broadcast_reading(self, reading: ReactorReading):
        """Broadcast reading to WebSocket clients"""
        reading_dict = asdict(reading)
        reading_dict['timestamp'] = reading.timestamp.isoformat()
        
        await self.websocket_manager.broadcast_reading(reading_dict)
    
    async def _broadcast_alert(self, alert: AnomalyAlert):
        """Broadcast alert to WebSocket clients"""
        alert_dict = asdict(alert)
        alert_dict['timestamp'] = alert.timestamp.isoformat()
        
        await self.websocket_manager.broadcast_alert(alert_dict)
    
    async def _initial_training(self):
        """Perform initial model training"""
        print("Training anomaly detection model...")
        
        # Generate training data
        training_data = self.simulator.generate_batch_readings(
            settings.training_data_size, 
            inject_anomalies=False
        )
        
        # Train the model
        self.anomaly_detector.train(training_data)
        self.last_training_time = datetime.now()
    
    async def _check_retraining(self):
        """Check if model needs retraining"""
        if not self.last_training_time:
            return
            
        time_since_training = datetime.now() - self.last_training_time
        if time_since_training.total_seconds() >= settings.model_retrain_interval:
            await self._retrain_model()
    
    async def _retrain_model(self):
        """Retrain the anomaly detection model with recent data"""
        print("Retraining anomaly detection model...")
        
        try:
            # Get recent readings from database
            recent_readings = await db_manager.get_recent_readings(
                limit=settings.training_data_size
            )
            
            if len(recent_readings) >= 100:  # Minimum for retraining
                self.anomaly_detector.train(recent_readings)
                self.last_training_time = datetime.now()
                print("Model retrained successfully")
            else:
                print("Insufficient data for retraining")
                
        except Exception as e:
            print(f"Error during model retraining: {e}")
    
    async def _cleanup_loop(self):
        """Periodic cleanup of old data"""
        while self.is_running:
            try:
                # Run cleanup daily
                await asyncio.sleep(24 * 3600)  # 24 hours
                await db_manager.cleanup_old_data()
                print("Database cleanup completed")
                
            except Exception as e:
                print(f"Error during cleanup: {e}")
    
    def get_system_status(self) -> dict:
        """Get current system status"""
        uptime = 0
        if self.start_time:
            uptime = (datetime.now() - self.start_time).total_seconds()
        
        return {
            "status": "operational" if self.is_running else "stopped",
            "uptime_seconds": uptime,
            "total_readings": self.total_readings,
            "total_alerts": self.total_alerts,
            "model_trained": self.anomaly_detector.is_trained,
            "last_training": self.last_training_time.isoformat() if self.last_training_time else None,
            "websocket_connections": len(self.websocket_manager.active_connections)
        }


# Global monitoring service instance
monitoring_service = MonitoringService()
