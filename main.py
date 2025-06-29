"""Entry point for SMR Safety Monitoring System"""

import uvicorn
from app.main import app
from app.config import settings

if __name__ == "__main__":
    print(f"Starting {settings.app_name}")
    print(f"Dashboard will be available at: http://{settings.host}:{settings.port}")
    print(f"API documentation at: http://{settings.host}:{settings.port}/docs")
    
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )