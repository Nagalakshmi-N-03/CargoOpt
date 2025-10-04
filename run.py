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
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

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
    required_vars = []
    optional_vars = {
        'DATABASE_URL': 'sqlite:///./cargo_opt.db',
        'HOST': '0.0.0.0',
        'PORT': '5000',
        'RELOAD': 'false',
        'LOG_LEVEL': 'INFO',
        'MAX_WORKERS': '1'
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
        import pandas
        import numpy
        
        logger.info("✅ All core dependencies are available")
        
        # Log versions
        logger.info("Dependency Versions:")
        logger.info(f"  FastAPI: {fastapi.__version__}")
        logger.info(f"  SQLAlchemy: {sqlalchemy.__version__}")
        logger.info(f"  Pydantic: {pydantic.__version__}")
        logger.info(f"  Pandas: {pandas.__version__}")
        logger.info(f"  NumPy: {numpy.__version__}")
        
        return True
        
    except ImportError as e:
        logger.error(f"❌ Missing dependency: {e}")
        logger.error("Please install all required packages: pip install -r requirements.txt")
        return False

def initialize_application():
    """Initialize the FastAPI application"""
    try:
        from backend.main import app
        logger.info("✅ FastAPI application initialized successfully")
        return app
    except Exception as e:
        logger.error(f"❌ Failed to initialize application: {e}")
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

def main():
    """Main application entry point"""
    try:
        # Print banner
        print_banner()
        
        logger.info("Starting CargoOpt Application...")
        
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
            sys.exit(1)
        
        # Get configuration
        host = os.getenv("HOST", "0.0.0.0")
        port = int(os.getenv("PORT", "5000"))
        reload = os.getenv("RELOAD", "false").lower() == "true"
        log_level = os.getenv("LOG_LEVEL", "info")
        workers = int(os.getenv("MAX_WORKERS", "1"))
        
        # Log startup information
        logger.info(f"Server configuration:")
        logger.info(f"  Host: {host}")
        logger.info(f"  Port: {port}")
        logger.info(f"  Reload: {reload}")
        logger.info(f"  Log Level: {log_level}")
        logger.info(f"  Workers: {workers}")
        
        # Determine if we're in development mode
        is_development = reload or os.getenv("ENVIRONMENT", "development") == "development"
        
        if is_development:
            logger.info("🚀 Starting server in DEVELOPMENT mode...")
            logger.info("📚 API Documentation will be available at: http://localhost:5000/docs")
        else:
            logger.info("🚀 Starting server in PRODUCTION mode...")
        
        logger.info(f"🌐 Server will be available at: http://{host}:{port}")
        logger.info("⏳ Starting up... (Press CTRL+C to stop)")
        
        # Start the server
        uvicorn.run(
            "backend.main:app",
            host=host,
            port=port,
            reload=reload,
            log_level=log_level,
            workers=workers if not reload else 1,
            access_log=True,
            use_colors=True
        )
        
    except KeyboardInterrupt:
        logger.info("Received interrupt signal. Shutting down gracefully...")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)
    finally:
        logger.info("CargoOpt application has stopped.")

if __name__ == "__main__":
    main()