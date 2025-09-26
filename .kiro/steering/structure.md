# Project Structure

## Directory Organization

```
speech-to-text/
├── .git/                   # Git repository
├── .kiro/                  # Kiro IDE configuration and specs
├── cli/                    # CLI service (command-line interface)
├── stt-service/           # Core speech-to-text processing service
├── audio-format-service/  # Audio format handling service
├── shared/                # Shared libraries and interfaces
├── tests/                 # Integration and end-to-end tests
├── data/                  # Shared data directory (runtime)
├── models/                # ML model storage (gitignored)
└── docker-compose.yml     # Service orchestration
```

## Service Structure Pattern

Each service follows a consistent structure:

```
service-name/
├── Dockerfile
├── requirements.txt       # Service-specific dependencies
└── src/
    ├── __init__.py
    └── [service modules]
```

## Shared Package Structure

The `shared/` directory contains common code used across services:

```
shared/
├── setup.py              # Package configuration
├── requirements.txt      # Shared dependencies
├── validate_setup.py     # Setup validation script
└── src/
    ├── __init__.py
    ├── models.py         # Common data models
    ├── exceptions.py     # Custom exceptions
    └── interfaces/       # Abstract interfaces
        ├── __init__.py
        ├── audio_format.py    # Audio format handler interface
        └── stt_model.py       # Speech-to-text model interface
```

## Key Conventions

### File Naming
- Use snake_case for Python files and directories
- Service directories use kebab-case (e.g., `audio-format-service`)
- Interface files are singular (e.g., `audio_format.py`, not `audio_formats.py`)

### Package Dependencies
- Each service includes `shared` as editable dependency: `-e ../shared`
- Services are isolated - no direct imports between service directories
- All inter-service communication goes through APIs or shared interfaces

### Data Models Location
- Common data models in `shared/src/models.py`
- Service-specific models in respective service `src/` directories
- All models use dataclasses with validation in `__post_init__`

### Interface Definitions
- Abstract base classes in `shared/src/interfaces/`
- Use ABC and abstractmethod decorators
- Implementations in respective services, not in shared

### Testing Structure
```
tests/
├── __init__.py
├── requirements.txt      # Test-specific dependencies
├── test-data/           # Small test audio files
└── [test modules]
```

### Configuration Files
- `docker-compose.yml`: Main orchestration
- `docker-compose.test.yml`: Test environment
- Service-specific configs in respective service directories

## Import Patterns

### Within Services
```python
# Import from shared package
from stt_shared.models import AudioRequest, TranscriptionResult
from stt_shared.interfaces.stt_model import SpeechToTextModel

# Import within service
from .local_module import LocalClass
```

### Shared Package Imports
```python
# In shared package modules
from .models import AudioRequest
from .interfaces.audio_format import AudioFormatHandler
```

## Development Workflow

### Adding New Services
1. Create service directory following naming convention
2. Add Dockerfile and requirements.txt
3. Include `-e ../shared` in requirements.txt
4. Create src/ directory with __init__.py
5. Update docker-compose.yml

### Adding Shared Functionality
1. Add to appropriate module in `shared/src/`
2. Update shared/setup.py if needed
3. Run validation: `cd shared && python validate_setup.py`

### Interface Implementation
1. Define interface in `shared/src/interfaces/`
2. Implement in respective service
3. Register implementation through dependency injection