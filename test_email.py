"""Test script for fastapi-mail email functionality"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from app.config import settings
from app.services.email_alerts import EmailAlertService
from app.models.schemas import AnomalyAlert


async def test_email_service():
    """Test the new fastapi-mail email service"""
    print("🧪 Testing FastAPI-Mail Email Service")
    print("=" * 50)
    
    # Initialize email service
    email_service = EmailAlertService()
    
    if not email_service.enabled:
        print("❌ Email service is disabled (no credentials configured)")
        return
    
    print(f"✅ Email service initialized")
    print(f"   Server: {settings.smtp_server}:{settings.smtp_port}")
    print(f"   Username: {settings.smtp_username}")
    print(f"   Use TLS: {settings.smtp_use_tls}")
    print(f"   Use SSL: {settings.smtp_use_ssl}")
    print(f"   Recipients: {settings.alert_recipients}")
    
    # Test connection
    print("\n🔌 Testing email connection...")
    connection_success = await email_service.test_connection()
    
    if not connection_success:
        print("❌ Email connection test failed")
        return
    
    print("✅ Email connection test successful")
    
    # Test plain text alert
    print("\n📧 Testing plain text alert...")
    test_alert = AnomalyAlert(
        timestamp=datetime.now(),
        parameter="core_temp",
        value=298.5,
        anomaly_score=-0.4,
        severity="HIGH",
        description="Test anomaly: Core temperature exceeds normal range"
    )
    
    try:
        await email_service.send_alert(test_alert)
        print("✅ Plain text alert sent successfully")
    except Exception as e:
        print(f"❌ Plain text alert failed: {e}")
    
    # Test HTML alert
    print("\n🎨 Testing HTML alert...")
    critical_alert = AnomalyAlert(
        timestamp=datetime.now(),
        parameter="neutron_flux",
        value=6e13,
        anomaly_score=-0.8,
        severity="CRITICAL",
        description="CRITICAL: Neutron flux spike detected - immediate shutdown recommended"
    )
    
    try:
        await email_service.send_html_alert(critical_alert)
        print("✅ HTML alert sent successfully")
    except Exception as e:
        print(f"❌ HTML alert failed: {e}")
    
    # Test system notification
    print("\n📢 Testing system notification...")
    try:
        await email_service.send_system_notification(
            "Test Notification",
            "This is a test system notification from the SMR monitoring system."
        )
        print("✅ System notification sent successfully")
    except Exception as e:
        print(f"❌ System notification failed: {e}")
    
    print("\n🎉 Email service testing completed!")
    print("Check your email inbox for the test messages.")


if __name__ == "__main__":
    asyncio.run(test_email_service())
