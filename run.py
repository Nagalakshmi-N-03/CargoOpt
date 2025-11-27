"""
CargoOpt Application Runner
Main entry point for the CargoOpt Backend Server
"""

import os
from backend.main import create_app
from backend.config.settings import DevelopmentConfig

# Create the Flask application instance
app = create_app(DevelopmentConfig)

if __name__ == '__main__':
    # Get configuration
    config = DevelopmentConfig()
    
    # Ensure required directories exist
    upload_folder = config.UPLOAD_FOLDER
    export_folder = config.EXPORT_FOLDER
    
    os.makedirs(upload_folder, exist_ok=True)
    os.makedirs(export_folder, exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    
    print("=" * 70)
    print("🚀 CargoOpt Backend Server Starting...")
    print("=" * 70)
    print(f"Environment:  {config.FLASK_ENV}")
    print(f"Debug Mode:   {config.DEBUG}")
    print(f"Host:         {config.HOST}")
    print(f"Port:         {config.PORT}")
    print(f"Database:     {config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}")
    print("=" * 70)
    print("\n📡 API Endpoints:")
    print(f"   Root:        http://{config.HOST}:{config.PORT}/")
    print(f"   API:         http://{config.HOST}:{config.PORT}/api/")
    print(f"   Health:      http://{config.HOST}:{config.PORT}/api/health")
    print(f"   API Info:    http://{config.HOST}:{config.PORT}/api/info")
    print("\n⏹️  Press CTRL+C to stop the server")
    print("=" * 70 + "\n")
    
    # Run the application
    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG
    )