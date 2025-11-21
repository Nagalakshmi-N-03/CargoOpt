"""
Main entry point for the Real Estate Management System
"""
import os
from app import create_app

# Create the Flask application instance
app = create_app()

if __name__ == '__main__':
    # Ensure upload directory exists
    upload_folder = app.config.get('UPLOAD_FOLDER', 'static/uploads')
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    
    # Run the application
    # Debug mode should be False in production
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )