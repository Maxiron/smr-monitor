"""API routes for SMR monitoring system"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import JSONResponse
from typing import List, Optional
from datetime import datetime

from app.services import monitoring_service
from app.database import db_manager
from app.models.schemas import (
    ReactorReadingResponse, 
    AnomalyAlertResponse, 
    SystemStatusResponse
)


router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await monitoring_service.websocket_manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and handle any client messages
            data = await websocket.receive_text()
            # Echo back or handle commands if needed
            
    except WebSocketDisconnect:
        monitoring_service.websocket_manager.disconnect(websocket)


@router.get("/status", response_model=SystemStatusResponse)
async def get_system_status():
    """Get current system status and metrics"""
    try:
        status = monitoring_service.get_system_status()
        
        # Get latest reading for status
        latest_reading = await db_manager.get_latest_reading()
        latest_reading_response = None
        
        if latest_reading:
            latest_reading_response = ReactorReadingResponse(
                timestamp=latest_reading.timestamp.isoformat(),
                core_temp=latest_reading.core_temp,
                coolant_temp=latest_reading.coolant_temp,
                pressure=latest_reading.pressure,
                neutron_flux=latest_reading.neutron_flux,
                control_rod_position=latest_reading.control_rod_position,
                coolant_flow_rate=latest_reading.coolant_flow_rate,
                steam_pressure=latest_reading.steam_pressure
            )
        
        return SystemStatusResponse(
            status=status["status"],
            active_alerts=status["total_alerts"],
            last_reading=latest_reading_response,
            uptime_seconds=status["uptime_seconds"],
            total_readings=status["total_readings"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting system status: {str(e)}")


@router.get("/readings", response_model=List[ReactorReadingResponse])
async def get_recent_readings(limit: int = 100):
    """Get recent reactor readings"""
    try:
        if limit > 1000:  # Prevent excessive data requests
            limit = 1000
            
        readings = await db_manager.get_recent_readings(limit=limit)
        
        return [
            ReactorReadingResponse(
                timestamp=reading.timestamp.isoformat(),
                core_temp=reading.core_temp,
                coolant_temp=reading.coolant_temp,
                pressure=reading.pressure,
                neutron_flux=reading.neutron_flux,
                control_rod_position=reading.control_rod_position,
                coolant_flow_rate=reading.coolant_flow_rate,
                steam_pressure=reading.steam_pressure
            )
            for reading in readings
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting readings: {str(e)}")


@router.get("/alerts", response_model=List[AnomalyAlertResponse])
async def get_recent_alerts(limit: int = 50):
    """Get recent anomaly alerts"""
    try:
        if limit > 500:  # Prevent excessive data requests
            limit = 500
            
        alerts = await db_manager.get_recent_alerts(limit=limit)
        
        return [
            AnomalyAlertResponse(
                timestamp=alert.timestamp.isoformat(),
                parameter=alert.parameter,
                value=alert.value,
                anomaly_score=alert.anomaly_score,
                severity=alert.severity,
                description=alert.description
            )
            for alert in alerts
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting alerts: {str(e)}")


@router.get("/alerts/summary")
async def get_alerts_summary(hours: int = 24):
    """Get summary of alerts by severity for the last N hours"""
    try:
        if hours > 168:  # Limit to 1 week
            hours = 168
            
        alert_counts = await db_manager.get_alert_count_by_severity(hours=hours)
        
        return {
            "time_period_hours": hours,
            "alert_counts": alert_counts,
            "total_alerts": sum(alert_counts.values())
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting alert summary: {str(e)}")


@router.get("/model/info")
async def get_model_info():
    """Get information about the anomaly detection model"""
    try:
        model_info = monitoring_service.anomaly_detector.get_model_info()
        system_status = monitoring_service.get_system_status()
        
        return {
            **model_info,
            "last_training": system_status.get("last_training"),
            "total_readings_processed": system_status.get("total_readings", 0)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting model info: {str(e)}")


@router.post("/system/retrain")
async def trigger_model_retrain():
    """Manually trigger model retraining"""
    try:
        await monitoring_service._retrain_model()
        return {"message": "Model retraining initiated"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error triggering retrain: {str(e)}")


@router.post("/system/test-email")
async def test_email_configuration():
    """Test email configuration by sending a test message"""
    try:
        success = await monitoring_service.email_service.test_connection()
        if success:
            return {"message": "Email test successful", "status": "ok"}
        else:
            return {"message": "Email test failed", "status": "error"}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error testing email: {str(e)}")


@router.get("/websocket/info")
async def get_websocket_info():
    """Get information about WebSocket connections"""
    try:
        return monitoring_service.websocket_manager.get_connection_info()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting WebSocket info: {str(e)}")


# Health check endpoint
@router.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "SMR Safety Monitoring System"
    }
