# tests/test_cache.py
import pytest
from unittest.mock import patch, MagicMock
from app.cache.redis_config import GenericCacheConfig
from app.cache.cache_decorators import cache_result

@pytest.fixture
def mock_redis_client():
    """Mock del cliente de Redis para pruebas unitarias."""
    with patch('redis.Redis') as mock:
        mock_instance = mock.return_value
        yield mock_instance

def test_cache_set_and_get(mock_redis_client):
    """Verifica que los datos se pueden almacenar y recuperar del cache."""
    cache_manager = GenericCacheConfig()
    test_key = "test:data:1"
    test_value = {"key": "value"}
    
    mock_redis_client.setex.return_value = True
    assert cache_manager.set_cache(test_key, test_value)
    
    mock_redis_client.get.return_value = '{"key": "value"}'
    retrieved_value = cache_manager.get_cache(test_key)
    assert retrieved_value == test_value

def test_cache_decorator(mock_redis_client):
    """Verifica que el decorador de cache funciona correctamente."""
    mock_redis_client.get.return_value = None
    
    @cache_result(key_prefix="test_func")
    def dummy_function():
        return "cached data"

    result = dummy_function()
    assert result == "cached data"
    
    mock_redis_client.setex.assert_called_once()
    mock_redis_client.get.return_value = '"cached data"'
    
    result_from_cache = dummy_function()
    assert result_from_cache == "cached data"
    mock_redis_client.setex.assert_called_once()  # La función no debe ser llamada de nuevo

def test_cache_invalidation(mock_redis_client):
    """Verifica la invalidación del cache por patrón."""
    cache_manager = GenericCacheConfig()
    pattern = "test:*:*"
    mock_redis_client.keys.return_value = ["test:data:1", "test:data:2"]
    
    cache_manager.invalidate_cache(pattern)
    
    mock_redis_client.keys.assert_called_with(pattern)
    mock_redis_client.delete.assert_called_with("test:data:1", "test:data:2")