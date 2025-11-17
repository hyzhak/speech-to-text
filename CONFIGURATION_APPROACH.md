# Configuration Approach - Audio Format Service

## Philosophy: Fail-Fast Configuration

We follow two key principles:

1. **[12-Factor App](https://12factor.net/config)**: Configuration is stored in environment variables, not hardcoded
2. **Fail-Fast**: The application **refuses to start** if required configuration is missing

### Why Fail-Fast?

**❌ Silent Defaults are Dangerous:**

```python
# BAD: Silently uses default if env var missing
port = os.getenv('PORT', 8001)  # Might be wrong for production!
```

**✅ Explicit Configuration is Safe:**

```python
# GOOD: Fails loudly if env var missing
port = os.getenv('PORT')  # Raises error if not set
if port is None:
    raise SystemExit("PORT environment variable required!")
```

### Benefits of Fail-Fast:

1. **Catch errors early** - At startup, not in production
2. **Clear error messages** - Know exactly what's missing
3. **No surprises** - Can't accidentally use wrong defaults
4. **Explicit is better than implicit** - Python Zen

## Why Environment Variables?

### ✅ Benefits:

1. **Separation of Concerns**: Code and config are separate
2. **Environment-Specific**: Different values for dev/staging/prod
3. **Security**: Secrets not in source control
4. **Flexibility**: Change config without rebuilding
5. **Docker-Friendly**: Standard practice for containers

### ❌ Problems with Hardcoding:

1. Need to rebuild for config changes
2. Can't have different dev/prod settings
3. Secrets might leak into source control
4. Violates 12-factor principles

## Our Implementation

### Layer 1: Application Validation (config.py)

```python
class Settings(BaseSettings):
    host: str = Field(..., description="Server bind address")  # NO DEFAULT!
    port: int = Field(..., gt=0, lt=65536)                     # NO DEFAULT!
    reload: bool = Field(...)                                   # NO DEFAULT!
    log_level: str = Field(...)                                 # NO DEFAULT!
```

**Purpose**:

- **Validate** configuration (port range, positive numbers, etc.)
- **Require** all values explicitly (no defaults)
- **Fail loudly** with helpful error messages if anything is missing

### Layer 2: Environment Variables

```bash
export AUDIO_FORMAT_PORT=8002
export AUDIO_FORMAT_LOG_LEVEL=debug
```

**Purpose**: Override defaults for specific environments

### Layer 3: Docker Compose (docker-compose.yml)

```yaml
environment:
  - AUDIO_FORMAT_PORT=8001 # Explicit value
  - AUDIO_FORMAT_LOG_LEVEL=info # Explicit value
```

**Purpose**:

- **Provide** all required values explicitly
- **Document** what the service needs
- **Ensure** service can start successfully

### Layer 4: .env File (optional)

```bash
# .env
AUDIO_FORMAT_PORT=8002
AUDIO_FORMAT_LOG_LEVEL=debug
```

**Purpose**: Local development convenience (not committed to git)

## Configuration Hierarchy (Priority Order)

1. **Environment Variables** (highest priority) - Override docker-compose
2. **Docker Compose environment section** - Provides required values
3. **No defaults in config.py** - Application fails if values missing

### Fail-Fast Behavior

```python
# If ANY required variable is missing:
❌ CONFIGURATION ERROR: Required environment variables missing or invalid
======================================================================

Missing required environment variables:
  - AUDIO_FORMAT_PORT
  - AUDIO_FORMAT_LOG_LEVEL

Please ensure all required environment variables are set...
```

This prevents the service from starting with incorrect configuration.

## Example Scenarios

### Scenario 1: Docker Deployment (Recommended)

```bash
# All required vars are set in docker-compose.yml
docker-compose up
# → Runs on 0.0.0.0:8001 with info logging
```

### Scenario 2: Local Development with .env

```bash
# Copy and customize .env file
cp .env.example .env
# Edit .env to set all required variables

python src/main.py
# → Reads all config from .env file
```

### Scenario 3: Local Development with Exports

```bash
# Set all required variables
export AUDIO_FORMAT_HOST=0.0.0.0
export AUDIO_FORMAT_PORT=8002
export AUDIO_FORMAT_RELOAD=true
export AUDIO_FORMAT_LOG_LEVEL=debug
export AUDIO_FORMAT_TEMP_DIR=/tmp
export AUDIO_FORMAT_MAX_FILE_SIZE=104857600

python src/main.py
# → Runs on 0.0.0.0:8002 with debug logging and auto-reload
```

### Scenario 3: Docker with Defaults

```bash
docker-compose up
# → Uses defaults from docker-compose.yml (port 8001)
```

### Scenario 4: Docker with Custom Port

```bash
AUDIO_FORMAT_PORT=8002 docker-compose up
# → Runs on port 8002, overriding docker-compose default
```

### Scenario 5: Production with .env

```bash
# .env file
AUDIO_FORMAT_PORT=8001
AUDIO_FORMAT_LOG_LEVEL=warning
AUDIO_FORMAT_MAX_FILE_SIZE=209715200

docker-compose up
# → Uses values from .env file
```

## Port Configuration Specifically

### Why Port is in Both Places?

**In config.py:**

```python
port: int = 8001  # Application default
```

- Fallback if no env var is set
- Makes the app runnable without any configuration

**In docker-compose.yml:**

```yaml
ports:
  - "${AUDIO_FORMAT_PORT:-8001}:${AUDIO_FORMAT_PORT:-8001}"
environment:
  - AUDIO_FORMAT_PORT=${AUDIO_FORMAT_PORT:-8001}
```

- Maps host port to container port
- Passes the port value into the container
- Allows runtime override: `AUDIO_FORMAT_PORT=8002 docker-compose up`

### Port Mapping Explained

```yaml
ports:
  - "HOST_PORT:CONTAINER_PORT"
  - "${AUDIO_FORMAT_PORT:-8001}:${AUDIO_FORMAT_PORT:-8001}"
```

This means:

- **Left side (host)**: Port on your machine
- **Right side (container)**: Port inside Docker container
- **Both use same variable**: Keeps them in sync
- **`:-8001` syntax**: Use 8001 if variable not set

## Best Practices We Follow

### ✅ DO:

- Use environment variables for all configuration
- Provide sensible defaults
- Document all variables
- Use consistent naming (prefix: `AUDIO_FORMAT_`)
- Keep .env.example in repo, .env out of repo

### ❌ DON'T:

- Hardcode configuration in application code
- Commit .env files with secrets
- Use different variable names in different places
- Require configuration for basic functionality

## Adding New Configuration

When adding a new config value:

1. **Add to config.py** with default:

   ```python
   class Settings(BaseSettings):
       new_setting: str = "default_value"
   ```

2. **Document in .env.example**:

   ```bash
   AUDIO_FORMAT_NEW_SETTING=default_value
   ```

3. **Add to docker-compose.yml** if needed:

   ```yaml
   environment:
     - AUDIO_FORMAT_NEW_SETTING=${AUDIO_FORMAT_NEW_SETTING:-default_value}
   ```

4. **Update README.md** with description

## Testing Configuration

```python
# Test with custom config
import os
os.environ['AUDIO_FORMAT_PORT'] = '8002'
from config import settings
assert settings.port == 8002
```

## Summary

**The application reads from environment variables, docker-compose sets them, and config.py provides defaults.**

This approach gives us:

- ✅ Flexibility (change without rebuild)
- ✅ Security (secrets in env, not code)
- ✅ Simplicity (works out-of-box with defaults)
- ✅ Docker-native (standard practice)
- ✅ 12-factor compliant (industry best practice)


## Fail-Fast Example

### What Happens When Config is Missing?

```bash
# Try to run without configuration
python src/main.py

# ❌ Application fails immediately:
======================================================================
❌ CONFIGURATION ERROR: Required environment variables missing or invalid
======================================================================

Missing required environment variables:
  - AUDIO_FORMAT_HOST
  - AUDIO_FORMAT_PORT
  - AUDIO_FORMAT_RELOAD
  - AUDIO_FORMAT_LOG_LEVEL
  - AUDIO_FORMAT_TEMP_DIR
  - AUDIO_FORMAT_MAX_FILE_SIZE

Please ensure all required environment variables are set in:
  - docker-compose.yml (for Docker deployment)
  - .env file (for local development)
  - Environment (for direct execution)

See .env.example for required variables and their formats.
======================================================================
```

### Why This is Better Than Defaults

**With Silent Defaults:**
```python
# Application starts with wrong config
port = 8001  # Default
# Later in production: "Why is it on port 8001? We need 8080!"
# Service is running but misconfigured - hard to debug
```

**With Fail-Fast:**
```python
# Application refuses to start
# Error message tells you exactly what's missing
# Fix it before the service ever runs
# No surprises in production
```

## Comparison: Defaults vs Fail-Fast

| Aspect | With Defaults | Fail-Fast (Our Approach) |
|--------|---------------|--------------------------|
| **Missing config** | Uses default silently | Fails with clear error |
| **Wrong config** | Runs with wrong value | Caught at startup |
| **Debugging** | Hard to find issues | Obvious from error message |
| **Production safety** | Risky (might use dev defaults) | Safe (must be explicit) |
| **Developer experience** | Convenient but dangerous | Slightly more setup, much safer |

## Implementation Details

### config.py - Validation and Fail-Fast

```python
class Settings(BaseSettings):
    # Use Field(...) with no default - makes it required
    port: int = Field(
        ...,  # <-- This means REQUIRED
        gt=0,
        lt=65536,
        description="Server port number (1-65535)"
    )

def load_settings() -> Settings:
    try:
        return Settings()
    except ValidationError as e:
        # Format helpful error message
        print("❌ CONFIGURATION ERROR: ...")
        raise SystemExit(1)

# Fail immediately on import if config is bad
settings = load_settings()
```

### docker-compose.yml - Explicit Values

```yaml
environment:
  # Set ALL required values explicitly
  - AUDIO_FORMAT_HOST=0.0.0.0
  - AUDIO_FORMAT_PORT=8001
  - AUDIO_FORMAT_RELOAD=false
  - AUDIO_FORMAT_LOG_LEVEL=info
  - AUDIO_FORMAT_TEMP_DIR=/app/temp
  - AUDIO_FORMAT_MAX_FILE_SIZE=104857600
```

**No `${VAR:-default}` syntax** - we set explicit values that we know are correct.

### .env.example - Documentation

```bash
# Documents ALL required variables
# Developers copy this to .env
# All variables have comments explaining their purpose
AUDIO_FORMAT_PORT=8001
```

## Migration from Defaults to Fail-Fast

### Before (Risky):
```python
class Settings(BaseSettings):
    port: int = 8001  # Default - might be wrong!
```

### After (Safe):
```python
class Settings(BaseSettings):
    port: int = Field(..., gt=0, lt=65536)  # Required!
```

### Migration Checklist:
1. ✅ Remove all default values from Settings class
2. ✅ Use `Field(...)` to make fields required
3. ✅ Add validation (gt, lt, regex, etc.)
4. ✅ Implement `load_settings()` with helpful error messages
5. ✅ Set all values explicitly in docker-compose.yml
6. ✅ Document all variables in .env.example
7. ✅ Update README with fail-fast behavior
8. ✅ Add tests for missing/invalid config

## Testing Configuration

```python
def test_config_fails_without_env_vars():
    """Test that config fails when env vars are missing."""
    # Clear env vars
    for key in list(os.environ.keys()):
        if key.startswith('AUDIO_FORMAT_'):
            os.environ.pop(key)
    
    # Should fail to import
    with pytest.raises(SystemExit):
        import config
```

## Summary: Why Fail-Fast is Better

### Silent Defaults (Bad):
- ❌ Service starts with wrong config
- ❌ Errors appear later in production
- ❌ Hard to debug
- ❌ Might use dev settings in prod

### Fail-Fast (Good):
- ✅ Service refuses to start if config is wrong
- ✅ Errors caught immediately at startup
- ✅ Clear error messages
- ✅ Impossible to run with missing config
- ✅ Forces explicit, documented configuration

**"Explicit is better than implicit"** - The Zen of Python
