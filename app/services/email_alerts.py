"""Email alert service for safety notifications using fastapi-mail"""

import asyncio
from typing import List, Optional
from datetime import datetime
from pathlib import Path

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors

from app.models.schemas import AnomalyAlert
from app.config import settings


class EmailAlertService:
    """Email notification system for safety alerts using fastapi-mail"""
    
    def __init__(self):
        self.enabled = bool(settings.smtp_username and settings.smtp_password)
        
        if self.enabled:
            # Configure fastapi-mail
            self.mail_config = ConnectionConfig(
                MAIL_USERNAME=settings.smtp_username,
                MAIL_PASSWORD=settings.smtp_password,
                MAIL_FROM=settings.mail_from or settings.smtp_username,
                MAIL_FROM_NAME=settings.mail_from_name,
                MAIL_PORT=settings.smtp_port,
                MAIL_SERVER=settings.smtp_server,
                MAIL_STARTTLS=settings.smtp_use_tls,
                MAIL_SSL_TLS=settings.smtp_use_ssl,
                USE_CREDENTIALS=True,
                VALIDATE_CERTS=True,
                TEMPLATE_FOLDER=Path(__file__).parent.parent.parent / "templates"
            )
            
            self.fast_mail = FastMail(self.mail_config)
            print(f"Email service configured with {settings.smtp_server}:{settings.smtp_port}")
        else:
            self.fast_mail = None
            print("Email alerts disabled - no SMTP credentials configured")
    
    async def send_alert(self, alert: AnomalyAlert, recipients: List[str] = None):
        """Send email alert for anomaly"""
        if not self.enabled:
            print(f"Email alert would be sent: {alert.description}")
            return
            
        recipients = recipients or settings.alert_recipients
        if not recipients:
            print("No email recipients configured")
            return
            
        try:
            subject = f"🚨 SMR Safety Alert - {alert.severity} - {alert.parameter}"
            body = self._create_alert_body(alert)
            
            message = MessageSchema(
                subject=subject,
                recipients=recipients,
                body=body,
                subtype=MessageType.plain
            )
            
            await self.fast_mail.send_message(message)
            print(f"Alert email sent for {alert.parameter} to {len(recipients)} recipients")
            
        except ConnectionErrors as e:
            print(f"Email connection error: {e}")
        except Exception as e:
            print(f"Failed to send email alert: {e}")
    
    def _create_alert_body(self, alert: AnomalyAlert) -> str:
        """Create email body for alert"""
        return f"""
SMR Safety Monitoring Alert

⚠️  ALERT DETAILS ⚠️
Timestamp: {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}
Parameter: {alert.parameter}
Value: {alert.value:.4f}
Severity: {alert.severity}
Anomaly Score: {alert.anomaly_score:.4f}

Description: {alert.description}

🔴 IMMEDIATE ACTION REQUIRED 🔴
Please investigate this anomaly immediately and take appropriate corrective measures.

This is an automated alert from the SMR Safety Monitoring System.
For technical support, contact the operations team.

---
SMR Monitoring System
Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
        """.strip()
    
    async def send_system_notification(self, subject: str, message: str, recipients: List[str] = None):
        """Send general system notification"""
        if not self.enabled:
            print(f"System notification: {subject} - {message}")
            return
            
        recipients = recipients or settings.alert_recipients
        if not recipients:
            print("No email recipients configured for system notifications")
            return
            
        try:
            full_subject = f"SMR System - {subject}"
            body = self._create_notification_body(message)
            
            message_schema = MessageSchema(
                subject=full_subject,
                recipients=recipients,
                body=body,
                subtype=MessageType.plain
            )
            
            await self.fast_mail.send_message(message_schema)
            print(f"System notification sent: {subject} to {len(recipients)} recipients")
            
        except ConnectionErrors as e:
            print(f"Email connection error for notification: {e}")
        except Exception as e:
            print(f"Failed to send system notification: {e}")
    
    def _create_notification_body(self, message: str) -> str:
        """Create notification email body"""
        return f"""
SMR Safety Monitoring System Notification

{message}

---
Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
SMR Monitoring System
        """.strip()
    
    async def send_html_alert(self, alert: AnomalyAlert, recipients: List[str] = None):
        """Send HTML formatted alert email"""
        if not self.enabled:
            print(f"HTML alert would be sent: {alert.description}")
            return
            
        recipients = recipients or settings.alert_recipients
        if not recipients:
            print("No email recipients configured")
            return
            
        try:
            subject = f"🚨 SMR Safety Alert - {alert.severity} - {alert.parameter}"
            html_body = self._create_html_alert_body(alert)
            
            message = MessageSchema(
                subject=subject,
                recipients=recipients,
                body=html_body,
                subtype=MessageType.html
            )
            
            await self.fast_mail.send_message(message)
            print(f"HTML alert email sent for {alert.parameter} to {len(recipients)} recipients")
            
        except ConnectionErrors as e:
            print(f"Email connection error: {e}")
        except Exception as e:
            print(f"Failed to send HTML email alert: {e}")
    
    def _create_html_alert_body(self, alert: AnomalyAlert) -> str:
        """Create HTML formatted email body for alert"""
        severity_color = {
            "CRITICAL": "#FF1744",
            "HIGH": "#FF5252", 
            "MEDIUM": "#FF9800",
            "LOW": "#FFC107"
        }.get(alert.severity, "#666666")
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>SMR Safety Alert</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
                .header {{ background-color: {severity_color}; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .alert-details {{ background-color: #f9f9f9; padding: 15px; border-radius: 4px; margin: 15px 0; }}
                .detail-row {{ margin: 8px 0; }}
                .label {{ font-weight: bold; color: #333; }}
                .value {{ color: #666; }}
                .footer {{ background-color: #f0f0f0; padding: 15px; text-align: center; font-size: 12px; color: #666; }}
                .severity-badge {{ background-color: {severity_color}; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚨 SMR Safety Alert</h1>
                    <p>Small Modular Reactor Safety Monitoring System</p>
                </div>
                
                <div class="content">
                    <h2>Alert Details</h2>
                    
                    <div class="alert-details">
                        <div class="detail-row">
                            <span class="label">Timestamp:</span> 
                            <span class="value">{alert.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}</span>
                        </div>
                        <div class="detail-row">
                            <span class="label">Parameter:</span> 
                            <span class="value">{alert.parameter}</span>
                        </div>
                        <div class="detail-row">
                            <span class="label">Value:</span> 
                            <span class="value">{alert.value:.4f}</span>
                        </div>
                        <div class="detail-row">
                            <span class="label">Severity:</span> 
                            <span class="severity-badge">{alert.severity}</span>
                        </div>
                        <div class="detail-row">
                            <span class="label">Anomaly Score:</span> 
                            <span class="value">{alert.anomaly_score:.4f}</span>
                        </div>
                    </div>
                    
                    <h3>Description</h3>
                    <p>{alert.description}</p>
                    
                    <div style="background-color: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 4px; margin: 20px 0;">
                        <h3 style="color: #856404; margin-top: 0;">🔴 IMMEDIATE ACTION REQUIRED</h3>
                        <p style="color: #856404; margin-bottom: 0;">Please investigate this anomaly immediately and take appropriate corrective measures.</p>
                    </div>
                    
                    <p><em>This is an automated alert from the SMR Safety Monitoring System.<br>
                    For technical support, contact the operations team.</em></p>
                </div>
                
                <div class="footer">
                    SMR Monitoring System<br>
                    Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
                </div>
            </div>
        </body>
        </html>
        """.strip()
    
    async def test_connection(self) -> bool:
        """Test email connection"""
        if not self.enabled:
            print("Email service disabled - cannot test connection")
            return False
            
        try:
            # Send a test message to verify connection
            test_message = MessageSchema(
                subject="SMR System - Connection Test",
                recipients=[settings.smtp_username],  # Send to self
                body="This is a test message to verify email configuration.",
                subtype=MessageType.plain
            )
            
            await self.fast_mail.send_message(test_message)
            print("Email connection test successful")
            return True
            
        except Exception as e:
            print(f"Email connection test failed: {e}")
            return False
