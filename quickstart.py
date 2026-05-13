"""
Quick Start Script for Vessel Rating System
Run this to set up and start the application
"""

import os
import sys
import subprocess
import platform


def check_python_version():
    """Check if Python version is 3.9+"""
    if sys.version_info < (3, 9):
        print(f"❌ Python 3.9+ required, but found {sys.version_info.major}.{sys.version_info.minor}")
        sys.exit(1)
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor}")


def check_requirements():
    """Check if requirements are installed"""
    print("\nChecking dependencies...")
    
    try:
        import streamlit
        import sqlalchemy
        import requests
        import pandas
        print("✓ All dependencies installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        return False


def install_requirements():
    """Install required packages"""
    print("\n📦 Installing dependencies from requirements.txt...")
    
    if not os.path.exists("requirements.txt"):
        print("❌ requirements.txt not found")
        return False
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Installation failed: {e}")
        return False


def init_database():
    """Initialize the database"""
    print("\n💾 Initializing database...")
    
    try:
        from db.models import init_db
        init_db()
        print("✓ Database initialized")
        return True
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False


def create_directories():
    """Create required directories"""
    print("\n📁 Creating directories...")
    
    dirs = ["db", "data", "logs"]
    for dir_name in dirs:
        os.makedirs(dir_name, exist_ok=True)
        print(f"  ✓ {dir_name}/")
    
    return True


def print_startup_banner():
    """Print startup banner"""
    print("\n" + "="*70)
    print("  🚢 VESSEL RATING SYSTEM")
    print("  Automated Maritime Risk Assessment Platform")
    print("="*70)
    print("\n📊 System Features:")
    print("  • 2-Input Interface (Vessel Name + IMO)")
    print("  • 6-Module Risk Analysis")
    print("  • Real-time Data Aggregation")
    print("  • Band Rating (0-9)")
    print("  • Critical Alert System")
    print("  • Historical Tracking & Export")
    print("\n📋 Available Modules:")
    print("  1. General Information (10% weight)")
    print("  2. Ownership Information (20% weight)")
    print("  3. AIS Information (15% weight)")
    print("  4. Risk & Compliance (30% weight)")
    print("  5. Environmental & Voyage (15% weight)")
    print("  6. Legal & Documentation (10% weight)")


def start_streamlit():
    """Start Streamlit app"""
    print("\n🚀 Starting Streamlit application...\n")
    
    cmd = [sys.executable, "-m", "streamlit", "run", "app/main.py"]
    
    try:
        subprocess.call(cmd)
    except KeyboardInterrupt:
        print("\n\n👋 Application stopped")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Failed to start application: {e}")
        sys.exit(1)


def start_api():
    """Start FastAPI REST server"""
    print("\n🚀 Starting REST API server...\n")
    
    cmd = [sys.executable, "api_server.py"]
    
    try:
        subprocess.call(cmd)
    except KeyboardInterrupt:
        print("\n\n👋 API server stopped")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Failed to start API server: {e}")
        sys.exit(1)


def show_help():
    """Show help information"""
    print("""
VESSEL RATING SYSTEM - Quick Start Guide

Usage:
  python quickstart.py [option]

Options:
  (none)        Full setup and start Streamlit app
  --api         Start REST API server (port 8000)
  --check       Check dependencies only
  --init        Initialize database only
  --examples    Run example analysis scripts
  --help        Show this help message

After starting the Streamlit application:
  1. Open http://localhost:8501 in your browser
  2. Enter vessel name and IMO number
  3. Click "Analyze Vessel"
  4. Review detailed risk assessment report

Starting the API Server:
  1. Run: python quickstart.py --api
  2. API available at: http://localhost:8000
  3. Interactive docs at: http://localhost:8000/docs
  4. API examples: python api_examples.py

Examples:
  python quickstart.py                    # Full setup (Streamlit)
  python quickstart.py --api              # Start REST API
  python quickstart.py --check            # Check deps
  python quickstart.py --init             # Init database
  python api_examples.py                  # Run API examples
  python examples.py                      # Run UI examples

For more information, see:
  - README.md for system overview
  - API_DOCUMENTATION.md for REST API details
  - DEPLOYMENT.md for deployment options

Issues? Check:
  - config.py for settings
  - logs/ directory for error logs
  - API_DOCUMENTATION.md for REST API troubleshooting
""")


def main():
    """Main entry point"""
    
    # Handle command line arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        
        if arg in ["--help", "-h"]:
            show_help()
            return
        
        elif arg == "--api":
            print_startup_banner()
            check_python_version()
            
            if not check_requirements():
                print("\n🔧 Installing dependencies...")
                if not install_requirements():
                    print("❌ Failed to install dependencies")
                    sys.exit(1)
            
            create_directories()
            
            if not init_database():
                print("⚠️  Database initialization failed, but continuing...")
            
            print("\n" + "="*70)
            print("✅ SYSTEM READY - REST API")
            print("="*70)
            print("\nAccessing the API:")
            print("  API Endpoint:  http://localhost:8000/api/v1")
            print("  Interactive Docs: http://localhost:8000/docs")
            print("  ReDoc: http://localhost:8000/redoc")
            print("  OpenAPI Schema: http://localhost:8000/openapi.json")
            print("\nExample API calls:")
            print("  curl http://localhost:8000/api/v1/health")
            print("  python api_examples.py")
            print("\nPress Ctrl+C to stop the server")
            print("="*70)
            
            start_api()
            return
        
        elif arg == "--check":
            print("\n🔍 Checking system configuration...")
            check_python_version()
            check_requirements()
            print("\n✓ Check complete")
            return
        
        elif arg == "--init":
            print("\n⚙️  Initializing system...")
            create_directories()
            init_database()
            print("\n✓ Initialization complete")
            return
        
        elif arg == "--examples":
            print("\n📚 Running example analyses...")
            try:
                import examples
                examples.run_all_examples()
            except Exception as e:
                print(f"❌ Error: {e}")
            return
        
        else:
            print(f"Unknown argument: {arg}")
            show_help()
            return
    
    # Full setup and start Streamlit
    print_startup_banner()
    
    # Check Python version
    check_python_version()
    
    # Check if dependencies are installed
    if not check_requirements():
        print("\n🔧 Installing dependencies...")
        if not install_requirements():
            print("❌ Failed to install dependencies")
            sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Initialize database
    if not init_database():
        print("⚠️  Database initialization failed, but continuing...")
    
    # Print final info
    print("\n" + "="*70)
    print("✅ SYSTEM READY")
    print("="*70)
    print("\nAccessing the application:")
    print("  Local:     http://localhost:8501")
    print("  Network:   http://YOUR_IP:8501")
    print("\nAlternative: Start REST API server")
    print("  python quickstart.py --api")
    print("\nPress Ctrl+C to stop the server")
    print("="*70)
    
    # Start application
    start_streamlit()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
