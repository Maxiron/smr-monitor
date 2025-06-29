"""Main FastAPI application for SMR Safety Monitoring System"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
import os

from app.config import settings
from app.api import router
from app.services import monitoring_service
from app.database import db_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    print("Starting SMR Safety Monitoring System...")
    await monitoring_service.initialize()
    await monitoring_service.start_monitoring()
    
    yield
    
    # Shutdown
    print("Shutting down SMR Safety Monitoring System...")
    await monitoring_service.stop_monitoring()
    await db_manager.close()


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="Real-time safety monitoring system for Small Modular Reactors",
    version="1.0.0",
    lifespan=lifespan
)

# Include API routes
app.include_router(router, prefix="/api", tags=["SMR Monitoring"])

# Mount static files
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def get_dashboard():
    """Serve the main dashboard"""
    dashboard_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SMR Safety Monitoring Dashboard</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                color: white;
                min-height: 100vh;
                padding: 20px;
            }
            
            .container {
                max-width: 1400px;
                margin: 0 auto;
            }
            
            .header {
                text-align: center;
                margin-bottom: 30px;
                padding: 20px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 15px;
                backdrop-filter: blur(10px);
            }
            
            .status-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            
            .status-card {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 15px;
                padding: 20px;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            
            .status-value {
                font-size: 2em;
                font-weight: bold;
                margin: 10px 0;
            }
            
            .charts-container {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
                margin-bottom: 30px;
            }
            
            .chart-container {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 15px;
                padding: 20px;
                backdrop-filter: blur(10px);
                height: 400px;
            }
            
            .alerts-container {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 15px;
                padding: 20px;
                backdrop-filter: blur(10px);
            }
            
            .alert-item {
                background: rgba(255, 82, 82, 0.2);
                border-left: 4px solid #ff5252;
                padding: 15px;
                margin: 10px 0;
                border-radius: 5px;
            }
            
            .alert-critical { border-left-color: #ff1744; background: rgba(255, 23, 68, 0.3); }
            .alert-high { border-left-color: #ff5252; background: rgba(255, 82, 82, 0.2); }
            .alert-medium { border-left-color: #ff9800; background: rgba(255, 152, 0, 0.2); }
            .alert-low { border-left-color: #ffc107; background: rgba(255, 193, 7, 0.2); }
            
            .connection-status {
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 10px 20px;
                border-radius: 25px;
                font-weight: bold;
            }
            
            .connected { background: #4caf50; }
            .disconnected { background: #f44336; }
            
            @keyframes pulse {
                0% { opacity: 1; }
                50% { opacity: 0.7; }
                100% { opacity: 1; }
            }
            
            .updating {
                animation: pulse 1s infinite;
            }
        </style>
    </head>
    <body>
        <div class="connection-status disconnected" id="connectionStatus">
            Connecting...
        </div>
        
        <div class="container">
            <div class="header">
                <h1>🔬 SMR Safety Monitoring Dashboard</h1>
                <p>Real-time monitoring of Small Modular Reactor safety parameters</p>
            </div>
            
            <div class="status-grid">
                <div class="status-card">
                    <h3>System Status</h3>
                    <div class="status-value" id="systemStatus">Initializing...</div>
                    <p>Current operational state</p>
                </div>
                
                <div class="status-card">
                    <h3>Active Alerts</h3>
                    <div class="status-value" id="activeAlerts">0</div>
                    <p>Current safety alerts</p>
                </div>
                
                <div class="status-card">
                    <h3>Core Temperature</h3>
                    <div class="status-value" id="coreTemp">---°C</div>
                    <p>Reactor core temperature</p>
                </div>
                
                <div class="status-card">
                    <h3>Neutron Flux</h3>
                    <div class="status-value" id="neutronFlux">---</div>
                    <p>neutrons/cm²/s</p>
                </div>
            </div>
            
            <div class="charts-container">
                <div class="chart-container">
                    <h3>Temperature Trends</h3>
                    <div id="tempChart">
                        <p style="text-align: center; margin-top: 150px;">
                            📊 Real-time temperature chart<br>
                            <small>Core and coolant temperature monitoring</small>
                        </p>
                    </div>
                </div>
                
                <div class="chart-container">
                    <h3>Pressure & Flow</h3>
                    <div id="pressureChart">
                        <p style="text-align: center; margin-top: 150px;">
                            📈 Pressure and flow monitoring<br>
                            <small>System pressure and coolant flow</small>
                        </p>
                    </div>
                </div>
            </div>
            
            <div class="alerts-container">
                <h3>Recent Safety Alerts</h3>
                <div id="alertsList">
                    <p style="text-align: center; padding: 40px;">
                        ✅ No recent alerts<br>
                        <small>All systems operating normally</small>
                    </p>
                </div>
            </div>
        </div>
        
        <script>
            class SMRDashboard {
                constructor() {
                    this.ws = null;
                    this.reconnectAttempts = 0;
                    this.maxReconnectAttempts = 10;
                    this.recentReadings = [];
                    this.recentAlerts = [];
                    
                    this.initWebSocket();
                    this.loadInitialData();
                }
                
                initWebSocket() {
                    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                    const wsUrl = `${protocol}//${window.location.host}/api/ws`;
                    
                    this.ws = new WebSocket(wsUrl);
                    
                    this.ws.onopen = () => {
                        console.log('WebSocket connected');
                        this.reconnectAttempts = 0;
                        this.updateConnectionStatus(true);
                    };
                    
                    this.ws.onmessage = (event) => {
                        const message = JSON.parse(event.data);
                        this.handleMessage(message);
                    };
                    
                    this.ws.onclose = () => {
                        console.log('WebSocket disconnected');
                        this.updateConnectionStatus(false);
                        this.attemptReconnect();
                    };
                    
                    this.ws.onerror = (error) => {
                        console.error('WebSocket error:', error);
                    };
                }
                
                handleMessage(message) {
                    switch (message.type) {
                        case 'reading':
                            this.handleReading(message.data);
                            break;
                        case 'alert':
                            this.handleAlert(message.data);
                            break;
                        case 'status':
                            this.handleStatus(message.data);
                            break;
                    }
                }
                
                handleReading(reading) {
                    this.recentReadings.push(reading);
                    if (this.recentReadings.length > 100) {
                        this.recentReadings.shift();
                    }
                    
                    // Update real-time displays
                    document.getElementById('coreTemp').textContent = `${reading.core_temp.toFixed(1)}°C`;
                    document.getElementById('neutronFlux').textContent = reading.neutron_flux.toExponential(2);
                    
                    // Add visual feedback for updates
                    document.getElementById('coreTemp').classList.add('updating');
                    setTimeout(() => {
                        document.getElementById('coreTemp').classList.remove('updating');
                    }, 1000);
                }
                
                handleAlert(alert) {
                    this.recentAlerts.unshift(alert);
                    if (this.recentAlerts.length > 20) {
                        this.recentAlerts.pop();
                    }
                    
                    this.updateAlertsDisplay();
                    this.updateActiveAlertsCount();
                }
                
                updateAlertsDisplay() {
                    const alertsList = document.getElementById('alertsList');
                    
                    if (this.recentAlerts.length === 0) {
                        alertsList.innerHTML = `
                            <p style="text-align: center; padding: 40px;">
                                ✅ No recent alerts<br>
                                <small>All systems operating normally</small>
                            </p>
                        `;
                        return;
                    }
                    
                    alertsList.innerHTML = this.recentAlerts.map(alert => `
                        <div class="alert-item alert-${alert.severity.toLowerCase()}">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <strong>${alert.parameter}</strong>
                                <span>${alert.severity}</span>
                            </div>
                            <div>${alert.description}</div>
                            <small>${new Date(alert.timestamp).toLocaleString()}</small>
                        </div>
                    `).join('');
                }
                
                async loadInitialData() {
                    try {
                        // Load system status
                        const statusResponse = await fetch('/api/status');
                        const status = await statusResponse.json();
                        
                        document.getElementById('systemStatus').textContent = status.status.toUpperCase();
                        this.updateActiveAlertsCount();
                        
                        if (status.last_reading) {
                            this.handleReading(status.last_reading);
                        }
                        
                        // Load recent alerts
                        const alertsResponse = await fetch('/api/alerts?limit=10');
                        const alerts = await alertsResponse.json();
                        this.recentAlerts = alerts;
                        this.updateAlertsDisplay();
                        
                    } catch (error) {
                        console.error('Error loading initial data:', error);
                    }
                }
                
                updateActiveAlertsCount() {
                    // Count alerts from last 24 hours
                    const oneDayAgo = new Date(Date.now() - 24 * 60 * 60 * 1000);
                    const recentAlertCount = this.recentAlerts.filter(
                        alert => new Date(alert.timestamp) > oneDayAgo
                    ).length;
                    
                    document.getElementById('activeAlerts').textContent = recentAlertCount;
                }
                
                updateConnectionStatus(connected) {
                    const status = document.getElementById('connectionStatus');
                    if (connected) {
                        status.textContent = '🟢 Connected';
                        status.className = 'connection-status connected';
                    } else {
                        status.textContent = '🔴 Disconnected';
                        status.className = 'connection-status disconnected';
                    }
                }
                
                attemptReconnect() {
                    if (this.reconnectAttempts < this.maxReconnectAttempts) {
                        this.reconnectAttempts++;
                        const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000);
                        
                        setTimeout(() => {
                            console.log(`Reconnection attempt ${this.reconnectAttempts}`);
                            this.initWebSocket();
                        }, delay);
                    }
                }
            }
            
            // Initialize dashboard when page loads
            document.addEventListener('DOMContentLoaded', () => {
                new SMRDashboard();
            });
        </script>
    </body>
    </html>
    """
    return dashboard_html
