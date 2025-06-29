# SMR Safety Monitoring System

A comprehensive real-time monitoring system for Small Modular Reactors (SMR) with advanced anomaly detection, safety alerts, and dashboard visualization.

## 🏗️ Architecture

This system is built with a clean, modular architecture:

```
smr-monitor/
├── app/                          # Main application package
│   ├── __init__.py
│   ├── main.py                   # FastAPI application and dashboard
│   ├── config.py                 # Configuration management
│   ├── models/                   # Data models and schemas
│   │   ├── __init__.py
│   │   ├── schemas.py            # Pydantic models and dataclasses
│   │   └── database.py           # SQLAlchemy database models
│   ├── database/                 # Database operations
│   │   ├── __init__.py
│   │   └── connection.py         # Async database manager
│   ├── services/                 # Business logic services
│   │   ├── __init__.py
│   │   ├── simulator.py          # SMR data simulation
│   │   ├── anomaly_detection.py  # ML-based anomaly detection
│   │   ├── email_alerts.py       # Email notification system
│   │   ├── websocket_manager.py  # Real-time WebSocket management
│   │   └── monitoring.py         # Core monitoring orchestration
│   └── api/                      # API routes and endpoints
│       ├── __init__.py
│       └── routes.py             # FastAPI route definitions
├── models/                       # Saved ML models (auto-generated)
├── static/                       # Static web assets (optional)
├── templates/                    # HTML templates (optional)
├── main.py                       # Application entry point
├── requirements.txt              # Python dependencies
├── .env.template                 # Environment variables template
└── README.md                     # This file
```

## 🚀 Key Features

### Real-time Monitoring
- **Sub-second data collection** from simulated SMR sensors
- **WebSocket-based dashboard** with live updates
- **Persistent data storage** with async SQLite database

### Advanced Anomaly Detection
- **Machine Learning**: Isolation Forest algorithm for anomaly detection
- **Auto-retraining**: Periodic model updates with recent data
- **Multi-parameter analysis**: Monitors 7 critical reactor parameters
- **Severity classification**: Critical, High, Medium, Low alert levels

### Safety Alert System
- **Email notifications** for critical and high-severity anomalies
- **Real-time dashboard alerts** with color-coded severity
- **Alert history** with persistent storage and analysis

### Production-Ready Features
- **Async SQLite database** with connection pooling
- **Configurable settings** via environment variables
- **Graceful startup/shutdown** with proper resource cleanup
- **Error handling and logging** throughout the system
- **Health check endpoints** for monitoring

## 📊 Monitored Parameters

| Parameter | Range | Unit | Description |
|-----------|-------|------|-------------|
| Core Temperature | 285-295 | °C | Reactor core temperature |
| Coolant Temperature | 250-270 | °C | Primary coolant temperature |
| Pressure | 15.5-16.5 | MPa | System pressure |
| Neutron Flux | 1e13-5e13 | neutrons/cm²/s | Neutron flux density |
| Control Rod Position | 70-85 | % withdrawn | Control rod insertion |
| Coolant Flow Rate | 200-250 | kg/s | Primary coolant flow |
| Steam Pressure | 6.8-7.2 | MPa | Secondary steam pressure |

## 🛠️ Installation & Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Copy the environment template and configure your settings:
```bash
cp .env.template .env
# Edit .env with your configuration
```

### 3. Run the Application
```bash
python main.py
```

### 4. Access the Dashboard
- **Dashboard**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health

<!-- ## 🔧 Configuration

The system uses environment variables for configuration. Key settings include:

```env
# Application
DEBUG=false
HOST=0.0.0.0
PORT=8000

# Database  
DATABASE_URL=sqlite+aiosqlite:///./smr_monitoring.db

# Email Alerts (optional)
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
ALERT_RECIPIENTS=["operator@example.com"]

# Monitoring
DATA_COLLECTION_INTERVAL=1.0
ANOMALY_THRESHOLD=0.1
MODEL_RETRAIN_INTERVAL=3600
``` -->

## 📡 API Endpoints

### Core Monitoring
- `GET /api/status` - System status and metrics
- `GET /api/readings?limit=100` - Recent reactor readings
- `GET /api/alerts?limit=50` - Recent anomaly alerts
- `GET /api/health` - Health check

### Analytics
- `GET /api/alerts/summary?hours=24` - Alert summary by severity
- `GET /api/model/info` - ML model information
- `POST /api/system/retrain` - Trigger model retraining

### Real-time
- `WebSocket /api/ws` - Real-time data stream

## 🔒 Safety Features

### Anomaly Detection
- **Isolation Forest ML model** with 90% normal operation training
- **Multi-dimensional analysis** of all parameters simultaneously
- **Adaptive thresholds** based on recent operational data
- **False positive minimization** through statistical validation

### Alert Management
- **Severity-based prioritization** (Critical → High → Medium → Low)
- **Email notifications** for high-priority alerts
- **Alert history** for compliance and analysis
- **Real-time dashboard** updates for immediate awareness

### Data Integrity
- **Persistent storage** of all readings and alerts
- **Data validation** at ingestion
- **Automatic cleanup** of old data
- **Transaction safety** with async database operations

## 🔄 Background Services

The system runs several background services:

1. **Data Collection**: Continuous sensor data simulation and collection
2. **Anomaly Detection**: Real-time analysis of incoming data
3. **Alert Processing**: Email notifications and dashboard updates
4. **Model Retraining**: Periodic ML model updates
5. **Database Cleanup**: Automated old data removal

## 🎨 Dashboard Features

The web dashboard provides:

- **Real-time parameter displays** with live updates
- **Visual alerts** with color-coded severity indicators
- **System status monitoring** with uptime and metrics
- **Connection status** indicator for WebSocket connectivity
- **Responsive design** for desktop and mobile access

## 🔍 Development

### Project Structure
- **Clean Architecture**: Separation of concerns with distinct layers
- **Service Layer**: Business logic isolated in services
- **Data Layer**: Database operations abstracted
- **API Layer**: RESTful endpoints with proper HTTP semantics

<!-- ### Code Quality
- **Type Hints**: Full typing throughout the codebase
- **Error Handling**: Comprehensive exception management
- **Async/Await**: Non-blocking operations for performance
- **Configuration**: Environment-based settings management -->

## 📈 Performance

- **Sub-second response times** for all API endpoints
- **Real-time updates** via WebSocket connections
- **Efficient database queries** with async SQLAlchemy
- **Memory management** with configurable data retention
- **Scalable architecture** ready for production deployment

<!-- ## 🛡️ Security Considerations

- **Input validation** on all API endpoints
- **SQL injection protection** via ORM
- **HTTPS ready** for production deployment
- **Environment-based secrets** management
- **Rate limiting ready** for production

## 📞 Support

For technical support or questions about the SMR Safety Monitoring System, please contact the development team or refer to the API documentation at `/docs`. -->

---

**⚠️ Important**: This is a demonstration system for educational purposes. For actual nuclear facility monitoring, additional safety certifications, redundancy, and regulatory compliance measures would be required.
