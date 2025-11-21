"""
CargoOpt Main Application Factory
Creates and configures the Flask application instance.
"""

import os
import logging
from datetime import datetime
from flask import Flask, jsonify, request, g
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

from backend.config.settings import Config
from backend.config.database import DatabaseManager, db_manager
from backend.utils.logger import get_logger

logger = get_logger(__name__)


def create_app(config_class=Config):
    """
    Application factory for creating Flask app instances.
    
    Args:
        config_class: Configuration class to use
        
    Returns:
        Flask application instance
    """
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    _init_extensions(app)
    
    # Register blueprints
    _register_blueprints(app)
    
    # Register error handlers
    _register_error_handlers(app)
    
    # Register request hooks
    _register_hooks(app)
    
    # Register health check endpoint
    _register_health_check(app)
    
    logger.info(f"CargoOpt application created in {config_class.FLASK_ENV} mode")
    
    return app


def _init_extensions(app):
    """Initialize Flask extensions."""
    # Enable CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": app.config.get('CORS_ORIGINS', ['http://localhost:3000']),
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        }
    })
    
    # Initialize database
    with app.app_context():
        try:
            db_manager.init_app(app)
            logger.info("Database manager initialized")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")


def _register_blueprints(app):
    """Register Flask blueprints for API routes."""
    from backend.api.routes import api_bp
    from backend.api.optimization import optimization_bp
    from backend.api.containers import containers_bp
    from backend.api.items import items_bp
    from backend.api.history import history_bp
    from backend.api.exports import exports_bp
    
    # Register main API blueprint
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(optimization_bp, url_prefix='/api/optimize')
    app.register_blueprint(containers_bp, url_prefix='/api/containers')
    app.register_blueprint(items_bp, url_prefix='/api/items')
    app.register_blueprint(history_bp, url_prefix='/api/history')
    app.register_blueprint(exports_bp, url_prefix='/api/exports')
    
    logger.info("API blueprints registered")


def _register_error_handlers(app):
    """Register error handlers for the application."""
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'error': 'Bad Request',
            'message': str(error.description) if hasattr(error, 'description') else 'Invalid request',
            'status_code': 400
        }), 400
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': 'Not Found',
            'message': 'The requested resource was not found',
            'status_code': 404
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            'error': 'Method Not Allowed',
            'message': f'Method {request.method} is not allowed for this endpoint',
            'status_code': 405
        }), 405
    
    @app.errorhandler(422)
    def unprocessable_entity(error):
        return jsonify({
            'error': 'Unprocessable Entity',
            'message': str(error.description) if hasattr(error, 'description') else 'Invalid data',
            'status_code': 422
        }), 422
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {error}")
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred',
            'status_code': 500
        }), 500
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        if isinstance(error, HTTPException):
            return jsonify({
                'error': error.name,
                'message': error.description,
                'status_code': error.code
            }), error.code
        
        logger.exception(f"Unhandled exception: {error}")
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred',
            'status_code': 500
        }), 500


def _register_hooks(app):
    """Register request/response hooks."""
    
    @app.before_request
    def before_request():
        g.request_start_time = datetime.utcnow()
        g.request_id = request.headers.get('X-Request-ID', os.urandom(8).hex())
    
    @app.after_request
    def after_request(response):
        # Add request timing
        if hasattr(g, 'request_start_time'):
            elapsed = (datetime.utcnow() - g.request_start_time).total_seconds()
            response.headers['X-Response-Time'] = f"{elapsed:.3f}s"
        
        # Add request ID
        if hasattr(g, 'request_id'):
            response.headers['X-Request-ID'] = g.request_id
        
        # Log request
        if request.path != '/api/health':
            logger.info(
                f"{request.method} {request.path} - {response.status_code} "
                f"({response.headers.get('X-Response-Time', 'N/A')})"
            )
        
        return response
    
    @app.teardown_appcontext
    def teardown_db(exception):
        db = g.pop('db_conn', None)
        if db is not None:
            db.close()


def _register_health_check(app):
    """Register health check endpoint."""
    
    @app.route('/api/health', methods=['GET'])
    def health_check():
        health = {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0',
            'components': {}
        }
        
        # Check database
        try:
            if db_manager.test_connection():
                health['components']['database'] = 'healthy'
            else:
                health['components']['database'] = 'unhealthy'
                health['status'] = 'degraded'
        except Exception as e:
            health['components']['database'] = f'error: {str(e)}'
            health['status'] = 'unhealthy'
        
        status_code = 200 if health['status'] == 'healthy' else 503
        return jsonify(health), status_code
    
    @app.route('/', methods=['GET'])
    def root():
        return jsonify({
            'name': 'CargoOpt API',
            'version': '1.0.0',
            'description': 'AI-Powered Container Optimization System',
            'docs': '/api/docs',
            'health': '/api/health'
        })