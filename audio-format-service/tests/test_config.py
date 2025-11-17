"""Tests for configuration management."""

import os
import pytest
from pydantic import ValidationError


def test_config_requires_all_env_vars():
    """Test that config fails when required env vars are missing."""
    # Clear all AUDIO_FORMAT_ env vars
    env_backup = {}
    for key in list(os.environ.keys()):
        if key.startswith('AUDIO_FORMAT_'):
            env_backup[key] = os.environ.pop(key)
    
    try:
        # Importing config should fail without env vars
        import importlib
        import sys
        
        # Remove config from cache if it exists
        if 'config' in sys.modules:
            del sys.modules['config']
        
        # This should raise SystemExit
        with pytest.raises(SystemExit) as exc_info:
            import config
        
        assert exc_info.value.code == 1
        
    finally:
        # Restore env vars
        os.environ.update(env_backup)


def test_config_validates_port_range():
    """Test that port validation works."""
    # Set all required vars except port
    os.environ['AUDIO_FORMAT_HOST'] = '0.0.0.0'
    os.environ['AUDIO_FORMAT_PORT'] = '99999'  # Invalid port
    os.environ['AUDIO_FORMAT_RELOAD'] = 'false'
    os.environ['AUDIO_FORMAT_LOG_LEVEL'] = 'info'
    os.environ['AUDIO_FORMAT_TEMP_DIR'] = '/tmp'
    os.environ['AUDIO_FORMAT_MAX_FILE_SIZE'] = '104857600'
    
    try:
        import importlib
        import sys
        
        # Remove config from cache
        if 'config' in sys.modules:
            del sys.modules['config']
        
        # This should fail due to invalid port
        with pytest.raises(SystemExit):
            import config
            
    finally:
        # Clean up
        for key in list(os.environ.keys()):
            if key.startswith('AUDIO_FORMAT_'):
                os.environ.pop(key)


def test_config_loads_successfully_with_valid_vars():
    """Test that config loads when all required vars are present."""
    # Set all required vars
    os.environ['AUDIO_FORMAT_HOST'] = '0.0.0.0'
    os.environ['AUDIO_FORMAT_PORT'] = '8001'
    os.environ['AUDIO_FORMAT_RELOAD'] = 'false'
    os.environ['AUDIO_FORMAT_LOG_LEVEL'] = 'info'
    os.environ['AUDIO_FORMAT_TEMP_DIR'] = '/tmp'
    os.environ['AUDIO_FORMAT_MAX_FILE_SIZE'] = '104857600'
    
    try:
        import importlib
        import sys
        
        # Remove config from cache
        if 'config' in sys.modules:
            del sys.modules['config']
        
        # This should succeed
        import config
        
        assert config.settings.host == '0.0.0.0'
        assert config.settings.port == 8001
        assert config.settings.reload is False
        assert config.settings.log_level == 'info'
        assert config.settings.temp_dir == '/tmp'
        assert config.settings.max_file_size == 104857600
        
    finally:
        # Clean up
        for key in list(os.environ.keys()):
            if key.startswith('AUDIO_FORMAT_'):
                os.environ.pop(key)


def test_config_validates_file_size_positive():
    """Test that max_file_size must be positive."""
    os.environ['AUDIO_FORMAT_HOST'] = '0.0.0.0'
    os.environ['AUDIO_FORMAT_PORT'] = '8001'
    os.environ['AUDIO_FORMAT_RELOAD'] = 'false'
    os.environ['AUDIO_FORMAT_LOG_LEVEL'] = 'info'
    os.environ['AUDIO_FORMAT_TEMP_DIR'] = '/tmp'
    os.environ['AUDIO_FORMAT_MAX_FILE_SIZE'] = '-1'  # Invalid
    
    try:
        import importlib
        import sys
        
        if 'config' in sys.modules:
            del sys.modules['config']
        
        with pytest.raises(SystemExit):
            import config
            
    finally:
        for key in list(os.environ.keys()):
            if key.startswith('AUDIO_FORMAT_'):
                os.environ.pop(key)


def test_config_error_message_is_helpful():
    """Test that error messages are clear and helpful."""
    import sys
    from io import StringIO
    
    # Clear env vars
    env_backup = {}
    for key in list(os.environ.keys()):
        if key.startswith('AUDIO_FORMAT_'):
            env_backup[key] = os.environ.pop(key)
    
    try:
        # Capture stdout
        captured_output = StringIO()
        sys.stdout = captured_output
        
        if 'config' in sys.modules:
            del sys.modules['config']
        
        try:
            import config
        except SystemExit:
            pass
        
        # Restore stdout
        sys.stdout = sys.__stdout__
        
        output = captured_output.getvalue()
        
        # Check that error message contains helpful information
        assert 'CONFIGURATION ERROR' in output
        assert 'AUDIO_FORMAT_' in output
        assert 'docker-compose.yml' in output or '.env' in output
        
    finally:
        sys.stdout = sys.__stdout__
        os.environ.update(env_backup)
