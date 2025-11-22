"""
API Tests
Tests for REST API endpoints
"""

import pytest
import json
from backend.main import create_app


@pytest.fixture
def client():
    """Create test client."""
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.mark.api
class TestHealthEndpoints:
    """Test health and info endpoints."""
    
    def test_health_check(self, client):
        """Test /api/health endpoint."""
        response = client.get('/api/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'status' in data
    
    def test_api_info(self, client):
        """Test /api/info endpoint."""
        response = client.get('/api/info')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'version' in data


@pytest.mark.api
class TestOptimizationEndpoints:
    """Test optimization API endpoints."""
    
    def test_optimization_request(self, client, sample_optimization_request):
        """Test POST /api/optimize."""
        response = client.post(
            '/api/optimize',
            data=json.dumps(sample_optimization_request),
            content_type='application/json'
        )
        assert response.status_code in [200, 202]
        data = json.loads(response.data)
        assert 'optimization_id' in data
    
    def test_get_optimization_status(self, client):
        """Test GET /api/optimize/{id}/status."""
        # Create optimization first
        opt_response = client.post('/api/optimize', 
                                   data=json.dumps({'container': {}, 'items': []}),
                                   content_type='application/json')
        
        if opt_response.status_code == 200:
            opt_id = json.loads(opt_response.data)['optimization_id']
            response = client.get(f'/api/optimize/{opt_id}/status')
            assert response.status_code in [200, 404]


@pytest.mark.api
class TestValidationEndpoint:
    """Test validation endpoint."""
    
    def test_validate_data(self, client, sample_optimization_request):
        """Test POST /api/validate."""
        response = client.post(
            '/api/validate',
            data=json.dumps(sample_optimization_request),
            content_type='application/json'
        )
        assert response.status_code in [200, 400]
        data = json.loads(response.data)
        assert 'valid' in data