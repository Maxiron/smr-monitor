"""Database connection and operations for SMR monitoring system"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select, desc, func
from typing import List, Optional
from datetime import datetime, timedelta

from app.config import settings
from app.models.database import Base, ReactorReadingDB, AnomalyAlertDB, SystemMetrics
from app.models.schemas import ReactorReading, AnomalyAlert


class DatabaseManager:
    """Manages database connections and operations"""
    
    def __init__(self):
        self.engine = create_async_engine(
            settings.database_url,
            echo=settings.debug
        )
        self.async_session = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    
    async def init_db(self):
        """Initialize database tables"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    async def close(self):
        """Close database connections"""
        await self.engine.dispose()
    
    async def save_reading(self, reading: ReactorReading) -> int:
        """Save a reactor reading to database"""
        async with self.async_session() as session:
            db_reading = ReactorReadingDB(
                timestamp=reading.timestamp,
                core_temp=reading.core_temp,
                coolant_temp=reading.coolant_temp,
                pressure=reading.pressure,
                neutron_flux=reading.neutron_flux,
                control_rod_position=reading.control_rod_position,
                coolant_flow_rate=reading.coolant_flow_rate,
                steam_pressure=reading.steam_pressure
            )
            session.add(db_reading)
            await session.commit()
            await session.refresh(db_reading)
            return db_reading.id
    
    async def save_alert(self, alert: AnomalyAlert) -> int:
        """Save an anomaly alert to database"""
        async with self.async_session() as session:
            db_alert = AnomalyAlertDB(
                timestamp=alert.timestamp,
                parameter=alert.parameter,
                value=alert.value,
                anomaly_score=alert.anomaly_score,
                severity=alert.severity,
                description=alert.description
            )
            session.add(db_alert)
            await session.commit()
            await session.refresh(db_alert)
            return db_alert.id
    
    async def get_recent_readings(self, limit: int = 100) -> List[ReactorReading]:
        """Get recent reactor readings"""
        async with self.async_session() as session:
            stmt = select(ReactorReadingDB).order_by(desc(ReactorReadingDB.timestamp)).limit(limit)
            result = await session.execute(stmt)
            db_readings = result.scalars().all()
            
            return [
                ReactorReading(
                    timestamp=r.timestamp,
                    core_temp=r.core_temp,
                    coolant_temp=r.coolant_temp,
                    pressure=r.pressure,
                    neutron_flux=r.neutron_flux,
                    control_rod_position=r.control_rod_position,
                    coolant_flow_rate=r.coolant_flow_rate,
                    steam_pressure=r.steam_pressure
                )
                for r in db_readings
            ]
    
    async def get_recent_alerts(self, limit: int = 50) -> List[AnomalyAlert]:
        """Get recent anomaly alerts"""
        async with self.async_session() as session:
            stmt = select(AnomalyAlertDB).order_by(desc(AnomalyAlertDB.timestamp)).limit(limit)
            result = await session.execute(stmt)
            db_alerts = result.scalars().all()
            
            return [
                AnomalyAlert(
                    timestamp=a.timestamp,
                    parameter=a.parameter,
                    value=a.value,
                    anomaly_score=a.anomaly_score,
                    severity=a.severity,
                    description=a.description
                )
                for a in db_alerts
            ]
    
    async def get_latest_reading(self) -> Optional[ReactorReading]:
        """Get the most recent reactor reading"""
        async with self.async_session() as session:
            stmt = select(ReactorReadingDB).order_by(desc(ReactorReadingDB.timestamp)).limit(1)
            result = await session.execute(stmt)
            db_reading = result.scalar_one_or_none()
            
            if db_reading:
                return ReactorReading(
                    timestamp=db_reading.timestamp,
                    core_temp=db_reading.core_temp,
                    coolant_temp=db_reading.coolant_temp,
                    pressure=db_reading.pressure,
                    neutron_flux=db_reading.neutron_flux,
                    control_rod_position=db_reading.control_rod_position,
                    coolant_flow_rate=db_reading.coolant_flow_rate,
                    steam_pressure=db_reading.steam_pressure
                )
            return None
    
    async def get_alert_count_by_severity(self, hours: int = 24) -> dict:
        """Get alert counts by severity for the last N hours"""
        async with self.async_session() as session:
            since = datetime.utcnow() - timedelta(hours=hours)
            stmt = select(
                AnomalyAlertDB.severity,
                func.count(AnomalyAlertDB.id)
            ).where(
                AnomalyAlertDB.timestamp >= since
            ).group_by(AnomalyAlertDB.severity)
            
            result = await session.execute(stmt)
            return dict(result.all())
    
    async def cleanup_old_data(self, days_to_keep: int = 30):
        """Clean up old data to manage database size"""
        async with self.async_session() as session:
            cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
            
            # Delete old readings
            await session.execute(
                ReactorReadingDB.__table__.delete().where(
                    ReactorReadingDB.timestamp < cutoff_date
                )
            )
            
            # Delete old alerts (keep longer for compliance)
            alert_cutoff = datetime.utcnow() - timedelta(days=days_to_keep * 2)
            await session.execute(
                AnomalyAlertDB.__table__.delete().where(
                    AnomalyAlertDB.timestamp < alert_cutoff
                )
            )
            
            await session.commit()


# Global database manager instance
db_manager = DatabaseManager()
