"""Test script to verify the SMR monitoring system setup"""

import sys
import importlib
import traceback
from pathlib import Path

def test_imports():
    """Test if all modules can be imported successfully"""
    print("🔍 Testing module imports...")
    
    modules_to_test = [
        "app.config",
        "app.models.schemas", 
        "app.models.database",
        "app.database.connection",
        "app.services.simulator",
        "app.services.anomaly_detection",
        "app.services.email_alerts",
        "app.services.websocket_manager",
        "app.services.monitoring",
        "app.api.routes",
        "app.main"
    ]
    
    failed_imports = []
    
    for module in modules_to_test:
        try:
            importlib.import_module(module)
            print(f"  ✅ {module}")
        except Exception as e:
            print(f"  ❌ {module}: {str(e)}")
            failed_imports.append((module, str(e)))
    
    if failed_imports:
        print(f"\n❌ {len(failed_imports)} import failures detected:")
        for module, error in failed_imports:
            print(f"  - {module}: {error}")
        return False
    else:
        print(f"\n✅ All {len(modules_to_test)} modules imported successfully!")
        return True

def test_config():
    """Test configuration loading"""
    print("\n🔍 Testing configuration...")
    
    try:
        from app.config import settings
        print(f"  ✅ Config loaded: {settings.app_name}")
        print(f"  ✅ Database URL: {settings.database_url}")
        print(f"  ✅ Host:Port: {settings.host}:{settings.port}")
        return True
    except Exception as e:
        print(f"  ❌ Config test failed: {str(e)}")
        return False

def test_data_models():
    """Test data model creation"""
    print("\n🔍 Testing data models...")
    
    try:
        from app.models.schemas import ReactorReading, AnomalyAlert
        from datetime import datetime
        
        # Test ReactorReading
        reading = ReactorReading(
            timestamp=datetime.now(),
            core_temp=290.0,
            coolant_temp=260.0,
            pressure=16.0,
            neutron_flux=3e13,
            control_rod_position=78.0,
            coolant_flow_rate=225.0,
            steam_pressure=7.0
        )
        print(f"  ✅ ReactorReading created: Core temp {reading.core_temp}°C")
        
        # Test AnomalyAlert
        alert = AnomalyAlert(
            timestamp=datetime.now(),
            parameter="core_temp",
            value=295.5,
            anomaly_score=-0.6,
            severity="HIGH",
            description="Test alert"
        )
        print(f"  ✅ AnomalyAlert created: {alert.severity} severity")
        
        return True
    except Exception as e:
        print(f"  ❌ Data model test failed: {str(e)}")
        return False

def test_services():
    """Test service initialization"""
    print("\n🔍 Testing services...")
    
    try:
        from app.services.simulator import SMRDataSimulator
        from app.services.anomaly_detection import AnomalyDetector
        
        # Test simulator
        simulator = SMRDataSimulator()
        reading = simulator.generate_reading()
        print(f"  ✅ Data simulator: Generated reading with core temp {reading.core_temp:.1f}°C")
        
        # Test anomaly detector
        detector = AnomalyDetector()
        print(f"  ✅ Anomaly detector: Initialized (trained: {detector.is_trained})")
        
        return True
    except Exception as e:
        print(f"  ❌ Service test failed: {str(e)}")
        traceback.print_exc()
        return False

def test_database_models():
    """Test database model definitions"""
    print("\n🔍 Testing database models...")
    
    try:
        from app.models.database import Base, ReactorReadingDB, AnomalyAlertDB
        
        # Check if models are properly defined
        tables = [table.name for table in Base.metadata.tables.values()]
        expected_tables = ['reactor_readings', 'anomaly_alerts', 'system_metrics']
        
        for table in expected_tables:
            if table in tables:
                print(f"  ✅ Database table defined: {table}")
            else:
                print(f"  ❌ Missing database table: {table}")
                return False
        
        return True
    except Exception as e:
        print(f"  ❌ Database model test failed: {str(e)}")
        return False

def test_dependencies():
    """Test required dependencies"""
    print("\n🔍 Testing dependencies...")
    
    required_packages = [
        'fastapi',
        'uvicorn',
        'sqlalchemy',
        'aiosqlite',
        'numpy',
        'pandas',
        'sklearn',
        'joblib',
        'pydantic',
        'pydantic_settings'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            # Handle packages with different import names
            import_name = package
            if package == 'sklearn':
                import_name = 'sklearn'
            elif package == 'pydantic_settings':
                import_name = 'pydantic_settings'
            
            importlib.import_module(import_name)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} - Not installed")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Install with: pip install -r requirements.txt")
        return False
    else:
        print(f"\n✅ All {len(required_packages)} required packages available!")
        return True

def test_file_structure():
    """Test if all required files exist"""
    print("\n🔍 Testing file structure...")
    
    base_path = Path(".")
    required_files = [
        "main.py",
        "requirements.txt",
        ".env.template",
        "app/__init__.py",
        "app/main.py",
        "app/config.py",
        "app/models/__init__.py",
        "app/models/schemas.py",
        "app/models/database.py",
        "app/database/__init__.py",
        "app/database/connection.py",
        "app/services/__init__.py",
        "app/services/simulator.py",
        "app/services/anomaly_detection.py",
        "app/services/email_alerts.py",
        "app/services/websocket_manager.py",
        "app/services/monitoring.py",
        "app/api/__init__.py",
        "app/api/routes.py"
    ]
    
    missing_files = []
    
    for file_path in required_files:
        full_path = base_path / file_path
        if full_path.exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ Missing: {file_path}")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n❌ Missing {len(missing_files)} required files")
        return False
    else:
        print(f"\n✅ All {len(required_files)} required files present!")
        return True

def main():
    """Run all tests"""
    print("🚀 SMR Safety Monitoring System - Setup Verification")
    print("=" * 60)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Dependencies", test_dependencies),
        ("Module Imports", test_imports),
        ("Configuration", test_config),
        ("Data Models", test_data_models),
        ("Database Models", test_database_models),
        ("Services", test_services)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ {test_name} test crashed: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} | {test_name}")
    
    print(f"\nResult: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your SMR monitoring system is ready to run.")
        print("Start the application with: python main.py")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please fix the issues above before running.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
