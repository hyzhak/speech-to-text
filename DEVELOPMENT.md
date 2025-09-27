# Development Guide

## 🚨 CRITICAL: Docker-Only Development Policy

**This project strictly enforces Docker-only development. Using system Python or local package managers is prohibited.**

### Why Docker-Only?

1. **Environment Consistency**: Ensures identical development environments across all machines
2. **Dependency Isolation**: Prevents conflicts with system Python installations
3. **Reproducible Builds**: Guarantees consistent behavior in development, testing, and production
4. **Simplified Onboarding**: New developers only need Docker installed
5. **Production Parity**: Development environment matches production containers

### Prohibited Actions

❌ **DO NOT** use these commands:
```bash
python -m pip install ...
pip install ...
python setup.py ...
python -m pytest ...
python script.py
conda install ...
pipenv install ...
poetry install ...
```

✅ **DO** use these Docker-based alternatives:
```bash
docker compose run --rm shared python -m pytest
docker compose run --rm cli python script.py
./scripts/lint.sh
docker compose -f docker-compose.test.yml up --build --abort-on-container-exit
```

## Development Workflow

### 1. Initial Setup

```bash
# Clone repository
git clone <repository-url>
cd speech-to-text

# Verify Docker is working
docker --version
docker compose --version

# No other setup required!
```

### 2. Running Tests

```bash
# Test shared package only
docker compose -f docker-compose.test.yml up --build test-shared --abort-on-container-exit

# Test all components
docker compose -f docker-compose.test.yml up --build --abort-on-container-exit

# Test specific component
docker compose -f docker-compose.test.yml up --build test-[component] --abort-on-container-exit
```

### 3. Code Quality Checks

```bash
# Check code quality (read-only)
./scripts/lint.sh

# Fix safe issues automatically
./scripts/lint.sh --fix

# Fix all issues (including potentially unsafe ones)
./scripts/lint.sh --fix --unsafe-fixes
```

### 4. Development Tasks

```bash
# Start development environment
docker compose up --build

# Run CLI commands
docker compose run --rm cli python -m src.main --help

# Access service shell for debugging
docker compose run --rm [service-name] bash

# Validate shared package
docker compose run --rm shared python validate_setup.py

# View service logs
docker compose logs -f [service-name]
```

### 5. Adding Dependencies

To add new Python dependencies:

1. **For shared package**: Edit `shared/requirements.txt`
2. **For specific service**: Edit `[service]/requirements.txt`
3. **For tests**: Edit `tests/requirements.txt`
4. **Rebuild containers**: `docker compose build`

Example:
```bash
# Add dependency to shared package
echo "new-package==1.0.0" >> shared/requirements.txt

# Rebuild and test
docker compose build shared
docker compose -f docker-compose.test.yml up --build test-shared --abort-on-container-exit
```

### 6. Creating New Services

1. Create service directory: `mkdir new-service`
2. Add `Dockerfile` and `requirements.txt`
3. Update `docker-compose.yml`
4. Add service to test configuration
5. Follow existing service patterns

## File Structure Guidelines

### Service Structure
```
service-name/
├── Dockerfile              # Container definition
├── requirements.txt        # Python dependencies
└── src/                   # Source code
    ├── __init__.py
    └── [service modules]
```

### Shared Package Structure
```
shared/
├── setup.py               # Package configuration
├── requirements.txt       # Shared dependencies
├── validate_setup.py      # Setup validation
└── src/                  # Source code
    ├── __init__.py
    ├── models.py         # Data models
    ├── exceptions.py     # Custom exceptions
    └── interfaces/       # Abstract interfaces
```

## Testing Guidelines

### Test Organization
- **Unit tests**: In each service's `tests/` directory
- **Integration tests**: In root `tests/` directory
- **Shared tests**: In `shared/tests/` directory

### Test Commands
```bash
# Run specific test file
docker compose run --rm shared python -m pytest tests/test_specific.py -v

# Run tests with coverage
docker compose run --rm shared python -m pytest --cov=src tests/

# Run tests with specific markers
docker compose run --rm shared python -m pytest -m "not slow" tests/
```

## Debugging

### Container Debugging
```bash
# Access running container
docker compose exec [service-name] bash

# Run container with shell
docker compose run --rm [service-name] bash

# View container logs
docker compose logs -f [service-name]

# Inspect container
docker compose run --rm [service-name] python -c "import sys; print(sys.path)"
```

### Common Debug Commands
```bash
# Check Python environment
docker compose run --rm shared python -c "import sys; print(sys.version)"

# List installed packages
docker compose run --rm shared pip list

# Check import paths
docker compose run --rm shared python -c "import sys; print('\n'.join(sys.path))"

# Validate package installation
docker compose run --rm shared python -c "import stt_shared; print('OK')"
```

## Performance Optimization

### Docker Build Optimization
- Use `.dockerignore` to exclude unnecessary files
- Leverage Docker layer caching
- Use multi-stage builds when appropriate
- Pin base image versions

### Development Speed
```bash
# Use cached builds when possible
docker compose up --build [service-name]

# Clean up when needed
docker compose down -v --remove-orphans
docker system prune -f
```

## Troubleshooting

### Common Issues

**Import Errors**
```bash
# Check if shared package is installed
docker compose run --rm [service] python -c "import stt_shared"

# Reinstall shared package
docker compose build [service]
```

**Permission Issues**
```bash
# Fix file permissions (if needed)
sudo chown -R $USER:$USER .
```

**Port Conflicts**
```bash
# Check what's using ports
docker compose ps
netstat -tulpn | grep :8000
```

**Build Failures**
```bash
# Clean rebuild
docker compose down -v
docker compose build --no-cache
docker compose up
```

### Getting Help

1. **Check logs**: `docker compose logs -f [service-name]`
2. **Validate setup**: `docker compose run --rm shared python validate_setup.py`
3. **Test environment**: `docker compose -f docker-compose.test.yml up --build test-shared --abort-on-container-exit`
4. **Review specs**: Check `.kiro/specs/` for detailed requirements

## Best Practices

### Code Organization
- Keep services loosely coupled
- Use shared package for common functionality
- Follow interface-based design
- Maintain clear separation of concerns

### Container Management
- Always use `--rm` for one-off containers
- Use `docker compose down` to clean up
- Monitor resource usage with `docker stats`
- Use specific service names when possible

### Development Workflow
- Run tests before committing
- Use linting tools consistently
- Keep containers updated
- Document any new patterns or conventions

Remember: **If you find yourself installing Python packages locally, you're doing it wrong!** Always use Docker containers.