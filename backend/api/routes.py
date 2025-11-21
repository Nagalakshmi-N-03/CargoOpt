"""
CargoOpt Main API Routes
Provides core API endpoints and version information.
"""

from flask import Blueprint, jsonify, request, current_app
from datetime import datetime
from functools import wraps

from backend.config.database import db_manager
from backend.config.settings import Config
from backend.utils.logger import get_logger

logger = get_logger(__name__)

# Create main API blueprint
api_bp = Blueprint('api', __name__)


# ============================================================================
# Decorators
# ============================================================================

def require_json(f):
    """Decorator to require JSON content type for POST/PUT requests."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.method in ['POST', 'PUT', 'PATCH']:
            if not request.is_json:
                return jsonify({
                    'error': 'Bad Request',
                    'message': 'Content-Type must be application/json'
                }), 400
        return f(*args, **kwargs)
    return decorated


def validate_pagination(f):
    """Decorator to validate and extract pagination parameters."""
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)
            
            if page < 1:
                page = 1
            if per_page < 1:
                per_page = 20
            if per_page > 100:
                per_page = 100
                
            kwargs['page'] = page
            kwargs['per_page'] = per_page
            
        except ValueError:
            return jsonify({
                'error': 'Bad Request',
                'message': 'Invalid pagination parameters'
            }), 400
            
        return f(*args, **kwargs)
    return decorated


# ============================================================================
# API Information Endpoints
# ============================================================================

@api_bp.route('/', methods=['GET'])
def api_index():
    """
    API root endpoint with version and documentation info.
    
    Returns:
        JSON with API information
    """
    return jsonify({
        'name': 'CargoOpt API',
        'version': '1.0.0',
        'description': 'AI-Powered Container Optimization System',
        'endpoints': {
            'health': '/api/health',
            'info': '/api/info',
            'optimize': '/api/optimize',
            'containers': '/api/containers',
            'items': '/api/items',
            'history': '/api/history',
            'exports': '/api/exports'
        },
        'documentation': '/api/docs'
    })


@api_bp.route('/info', methods=['GET'])
def api_info():
    """
    Detailed API information including configuration and capabilities.
    
    Returns:
        JSON with detailed API information
    """
    return jsonify({
        'api': {
            'name': 'CargoOpt API',
            'version': '1.0.0',
            'environment': Config.FLASK_ENV
        },
        'capabilities': {
            'optimization_algorithms': ['genetic_algorithm', 'constraint_programming'],
            'supported_item_types': Config.ITEM_TYPES,
            'storage_conditions': Config.STORAGE_CONDITIONS,
            'container_types': Config.CONTAINER_TYPES,
            'hazard_classes': Config.HAZARD_CLASSES
        },
        'limits': {
            'max_file_size_mb': Config.MAX_CONTENT_LENGTH / (1024 * 1024),
            'max_computation_time_seconds': Config.MAX_COMPUTATION_TIME,
            'max_items_per_request': 1000
        },
        'optimization_parameters': {
            'population_size': Config.GA_POPULATION_SIZE,
            'generations': Config.GA_GENERATIONS,
            'mutation_rate': Config.GA_MUTATION_RATE,
            'crossover_rate': Config.GA_CROSSOVER_RATE
        }
    })


@api_bp.route('/stats', methods=['GET'])
def api_stats():
    """
    Get API usage statistics.
    
    Returns:
        JSON with usage statistics
    """
    try:
        # Get optimization stats
        opt_stats = db_manager.execute_one("""
            SELECT 
                COUNT(*) as total_optimizations,
                COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed,
                COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed,
                AVG(utilization_percentage) as avg_utilization,
                AVG(computation_time_seconds) as avg_computation_time
            FROM optimizations
        """)
        
        # Get container stats
        container_count = db_manager.count('containers')
        
        # Get item stats
        item_stats = db_manager.execute_one("""
            SELECT 
                COUNT(*) as total_items,
                COUNT(DISTINCT item_type) as item_types
            FROM items
        """)
        
        # Get recent activity
        recent = db_manager.execute("""
            SELECT optimization_id, status, utilization_percentage, started_at
            FROM optimizations
            ORDER BY started_at DESC
            LIMIT 5
        """)
        
        return jsonify({
            'optimizations': {
                'total': opt_stats['total_optimizations'] if opt_stats else 0,
                'completed': opt_stats['completed'] if opt_stats else 0,
                'failed': opt_stats['failed'] if opt_stats else 0,
                'average_utilization': round(float(opt_stats['avg_utilization'] or 0), 2),
                'average_computation_time': round(float(opt_stats['avg_computation_time'] or 0), 3)
            },
            'containers': {
                'total': container_count
            },
            'items': {
                'total': item_stats['total_items'] if item_stats else 0,
                'types': item_stats['item_types'] if item_stats else 0
            },
            'recent_optimizations': [
                {
                    'id': r['optimization_id'],
                    'status': r['status'],
                    'utilization': float(r['utilization_percentage']) if r['utilization_percentage'] else None,
                    'timestamp': r['started_at'].isoformat() if r['started_at'] else None
                }
                for r in (recent or [])
            ],
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error fetching stats: {e}")
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'Failed to fetch statistics'
        }), 500


# ============================================================================
# Configuration Endpoints
# ============================================================================

@api_bp.route('/config', methods=['GET'])
def get_config():
    """
    Get current system configuration (non-sensitive).
    
    Returns:
        JSON with configuration settings
    """
    try:
        configs = db_manager.execute("""
            SELECT config_key, config_value, data_type, description
            FROM configurations
            ORDER BY config_key
        """)
        
        return jsonify({
            'configurations': [
                {
                    'key': c['config_key'],
                    'value': _parse_config_value(c['config_value'], c['data_type']),
                    'type': c['data_type'],
                    'description': c['description']
                }
                for c in (configs or [])
            ]
        })
        
    except Exception as e:
        logger.error(f"Error fetching config: {e}")
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'Failed to fetch configuration'
        }), 500


@api_bp.route('/config/<key>', methods=['GET'])
def get_config_value(key):
    """
    Get a specific configuration value.
    
    Args:
        key: Configuration key
        
    Returns:
        JSON with configuration value
    """
    try:
        config = db_manager.execute_one(
            "SELECT config_value, data_type FROM configurations WHERE config_key = %s",
            (key,)
        )
        
        if not config:
            return jsonify({
                'error': 'Not Found',
                'message': f'Configuration key "{key}" not found'
            }), 404
        
        return jsonify({
            'key': key,
            'value': _parse_config_value(config['config_value'], config['data_type']),
            'type': config['data_type']
        })
        
    except Exception as e:
        logger.error(f"Error fetching config value: {e}")
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'Failed to fetch configuration value'
        }), 500


@api_bp.route('/config/<key>', methods=['PUT'])
@require_json
def update_config_value(key):
    """
    Update a configuration value.
    
    Args:
        key: Configuration key
        
    Returns:
        JSON with updated configuration
    """
    try:
        data = request.get_json()
        
        if 'value' not in data:
            return jsonify({
                'error': 'Bad Request',
                'message': 'Missing "value" field'
            }), 400
        
        # Check if key exists
        existing = db_manager.execute_one(
            "SELECT id, data_type FROM configurations WHERE config_key = %s",
            (key,)
        )
        
        if not existing:
            return jsonify({
                'error': 'Not Found',
                'message': f'Configuration key "{key}" not found'
            }), 404
        
        # Update value
        db_manager.update(
            'configurations',
            {'config_value': str(data['value']), 'updated_at': datetime.utcnow()},
            'config_key = %s',
            (key,)
        )
        
        logger.info(f"Configuration updated: {key} = {data['value']}")
        
        return jsonify({
            'message': 'Configuration updated successfully',
            'key': key,
            'value': _parse_config_value(str(data['value']), existing['data_type'])
        })
        
    except Exception as e:
        logger.error(f"Error updating config: {e}")
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'Failed to update configuration'
        }), 500


# ============================================================================
# Validation Endpoint
# ============================================================================

@api_bp.route('/validate', methods=['POST'])
@require_json
def validate_data():
    """
    Validate optimization input data without running optimization.
    
    Returns:
        JSON with validation results
    """
    from backend.api.models import OptimizationRequestSchema
    
    try:
        data = request.get_json()
        schema = OptimizationRequestSchema()
        
        errors = schema.validate(data)
        
        if errors:
            return jsonify({
                'valid': False,
                'errors': errors
            }), 400
        
        # Additional business logic validation
        warnings = []
        
        # Check container capacity vs total item volume
        if 'container' in data and 'items' in data:
            container = data['container']
            items = data['items']
            
            container_volume = container['length'] * container['width'] * container['height']
            total_item_volume = sum(
                i['length'] * i['width'] * i['height'] * i.get('quantity', 1)
                for i in items
            )
            
            if total_item_volume > container_volume:
                warnings.append(
                    f"Total item volume ({total_item_volume:,} mm³) exceeds "
                    f"container volume ({container_volume:,} mm³)"
                )
            
            # Check weight
            container_max_weight = container.get('max_weight', float('inf'))
            total_weight = sum(i['weight'] * i.get('quantity', 1) for i in items)
            
            if total_weight > container_max_weight:
                warnings.append(
                    f"Total item weight ({total_weight:.2f} kg) exceeds "
                    f"container capacity ({container_max_weight:.2f} kg)"
                )
        
        return jsonify({
            'valid': True,
            'warnings': warnings,
            'message': 'Data is valid for optimization'
        })
        
    except Exception as e:
        logger.error(f"Validation error: {e}")
        return jsonify({
            'valid': False,
            'errors': {'_general': str(e)}
        }), 400


# ============================================================================
# Database Status Endpoint
# ============================================================================

@api_bp.route('/db/status', methods=['GET'])
def db_status():
    """
    Get database connection status.
    
    Returns:
        JSON with database status
    """
    try:
        pool_status = db_manager.get_pool_status()
        connection_ok = db_manager.test_connection()
        
        # Get table counts
        tables = {}
        for table in ['containers', 'items', 'optimizations', 'placements']:
            tables[table] = db_manager.count(table)
        
        return jsonify({
            'status': 'connected' if connection_ok else 'disconnected',
            'pool': pool_status,
            'tables': tables,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Database status error: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# ============================================================================
# Helper Functions
# ============================================================================

def _parse_config_value(value: str, data_type: str):
    """Parse configuration value based on its data type."""
    if value is None:
        return None
        
    try:
        if data_type == 'integer':
            return int(value)
        elif data_type == 'float':
            return float(value)
        elif data_type == 'boolean':
            return value.lower() in ('true', '1', 'yes')
        elif data_type == 'json':
            import json
            return json.loads(value)
        else:
            return value
    except (ValueError, TypeError):
        return value


def paginate_results(query_func, page: int, per_page: int, **kwargs):
    """
    Helper function to paginate query results.
    
    Args:
        query_func: Function that returns query results
        page: Current page number
        per_page: Items per page
        **kwargs: Additional arguments for query function
        
    Returns:
        Dictionary with paginated results and metadata
    """
    offset = (page - 1) * per_page
    
    results = query_func(limit=per_page, offset=offset, **kwargs)
    total = query_func(count_only=True, **kwargs)
    
    total_pages = (total + per_page - 1) // per_page
    
    return {
        'data': results,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_prev': page > 1
        }
    }