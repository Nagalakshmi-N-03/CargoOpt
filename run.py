#!/usr/bin/env python3
"""
Cargo Space Optimization - Main Entry Point
Version: 3.0.0
Description: Advanced cargo space optimization system with multiple algorithms
"""

import os
import sys
import logging
import uvicorn
from dotenv import load_dotenv

# Add the backend directory to Python path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('cargo_opt.log', mode='a', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)

def check_environment():
    """Check if all required environment variables are set"""
    required_vars = []  # No required vars for basic operation
    optional_vars = {
        'DATABASE_URL': 'sqlite:///./cargoopt.db',
        'HOST': '0.0.0.0',
        'PORT': '8000',
        'DEBUG': 'true',
        'LOG_LEVEL': 'INFO'
    }
    
    missing_required = [var for var in required_vars if not os.getenv(var)]
    if missing_required:
        logger.error(f"Missing required environment variables: {missing_required}")
        return False
    
    # Log configuration
    logger.info("Environment Configuration:")
    for var, default in optional_vars.items():
        value = os.getenv(var, default)
        logger.info(f"  {var}: {value}")
    
    return True

def check_dependencies():
    """Check if all required dependencies are available"""
    try:
        # Test core dependencies
        import fastapi
        import uvicorn
        import sqlalchemy
        import pydantic
        
        logger.info("✅ All core dependencies are available")
        
        # Log versions
        logger.info("Dependency Versions:")
        logger.info(f"  FastAPI: {fastapi.__version__}")
        logger.info(f"  SQLAlchemy: {sqlalchemy.__version__}")
        logger.info(f"  Pydantic: {pydantic.__version__}")
        
        # Optional dependencies
        try:
            import pulp
            logger.info(f"  PuLP: {pulp.__version__}")
        except ImportError:
            logger.warning("  ⚠️ PuLP not installed (required for optimization algorithms)")
        
        try:
            import pandas
            import numpy
            logger.info(f"  Pandas: {pandas.__version__}")
            logger.info(f"  NumPy: {numpy.__version__}")
        except ImportError:
            logger.warning("  Optional dependencies (pandas, numpy) not installed")
        
        return True
        
    except ImportError as e:
        logger.error(f"❌ Missing core dependency: {e}")
        logger.error("Please install all required packages: pip install -r requirements.txt")
        return False

def initialize_application():
    """Initialize the FastAPI application"""
    try:
        # Import here to avoid circular imports
        from backend.main import app
        logger.info("✅ FastAPI application initialized successfully")
        return app
    except ImportError as e:
        logger.error(f"❌ Failed to import backend modules: {e}")
        logger.error("Make sure you're in the correct directory and backend structure exists")
        return None
    except Exception as e:
        logger.error(f"❌ Failed to initialize application: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None

def print_banner():
    """Print application banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║    🚚 Cargo Space Optimization System v3.0.0 🚚            ║
    ║                                                              ║
    ║    Advanced container packing optimization with AI          ║
    ║                                                              ║
    ║    Features:                                                 ║
    ║    • Multiple optimization algorithms                        ║
    ║    • 3D container packing                                    ║
    ║    • Genetic algorithm optimization                         ║
    ║    • Multi-container stowage                                ║
    ║    • Batch processing                                        ║
    ║    • Real-time validation                                   ║
    ║    • Comprehensive reporting                                 ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def create_default_env():
    """Create default .env file if it doesn't exist"""
    env_file = ".env"
    if not os.path.exists(env_file):
        logger.info("Creating default .env file...")
        with open(env_file, 'w') as f:
            f.write("""# Database Configuration
DATABASE_URL=sqlite:///./cargoopt.db

# Application Settings
DEBUG=true
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO

# Security
SECRET_KEY=your-secret-key-change-in-production

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://127.0.0.1:3000","http://localhost:5173"]
""")
        logger.info("✅ Default .env file created")

def main():
    """Main application entry point"""
    try:
        # Print banner
        print_banner()
        
        logger.info("Starting CargoOpt Application...")
        
        # Create default .env if missing
        create_default_env()
        
        # Check environment
        if not check_environment():
            logger.error("Environment check failed. Please check your configuration.")
            sys.exit(1)
        
        # Check dependencies
        if not check_dependencies():
            logger.error("Dependency check failed. Please install required packages.")
            sys.exit(1)
        
        # Initialize application
        app = initialize_application()
        if not app:
            logger.error("Failed to initialize application. Check backend structure.")
            sys.exit(1)
        
        # Get configuration
        host = os.getenv("HOST", "0.0.0.0")
        port = int(os.getenv("PORT", "8000"))
        reload = os.getenv("DEBUG", "true").lower() == "true"
        log_level = os.getenv("LOG_LEVEL", "info").lower()
        
        # Log startup information
        logger.info(f"Server configuration:")
        logger.info(f"  Host: {host}")
        logger.info(f"  Port: {port}")
        logger.info(f"  Reload: {reload}")
        logger.info(f"  Log Level: {log_level}")
        
        # Determine if we're in development mode
        is_development = reload or os.getenv("ENVIRONMENT", "development") == "development"
        
        if is_development:
            logger.info("🚀 Starting server in DEVELOPMENT mode...")
            logger.info("📚 API Documentation: http://localhost:8000/docs")
            logger.info("🔗 OpenAPI JSON: http://localhost:8000/openapi.json")
        else:
            logger.info("🚀 Starting server in PRODUCTION mode...")
        
        logger.info(f"🌐 Application will be available at: http://{host}:{port}")
        logger.info("⏳ Starting up... (Press CTRL+C to stop)")
        
        # Start the server
        uvicorn.run(
            "backend.main:app",
            host=host,
            port=port,
            reload=reload,
            log_level=log_level,
            access_log=True,
            use_colors=True
        )
        
    except KeyboardInterrupt:
        logger.info("Received interrupt signal. Shutting down gracefully...")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        logger.info("CargoOpt application has stopped.")

if __name__ == "__main__":
    main()