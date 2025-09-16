# MantaTools - Modular Structure

This is a refactored version of MantaTools with a clean, modular structure similar to the reference image.

## Project Structure

```
mantatools/
├── __init__.py                 # Main package exports
├── app.py                      # Application entry point
├── core/                       # Core functionality
│   ├── __init__.py
│   ├── paths.py               # Path utilities and Steam detection
│   ├── warmup.py              # Type warmup functionality
│   ├── steam_meta.py          # Steam metadata and app type fetching
│   ├── lua_patch.py           # Lua patch and scan utilities
│   ├── delisted.py            # Delisted games support
│   ├── images.py              # Image loading, caching, and utilities
│   ├── settings.py            # Settings management
│   └── workers.py             # Background worker classes
├── ui/                        # UI components
│   ├── __init__.py
│   ├── theme.py               # Theme constants and styling
│   ├── snack.py               # Toast notification system
│   ├── progress.py            # Modern progress bar component
│   ├── sections.py            # Section UI components
│   ├── right_panel.py         # Right panel with collapsible sections
│   ├── sidebar.py             # Sidebar navigation component
│   ├── list_items.py          # List item components for games and DLC
│   ├── scrolling.py           # Smooth scrolling components
│   └── gfx.py                 # Graphics utilities
├── pages/                     # Page components
│   ├── __init__.py
│   ├── games_page.py          # Games page components
│   └── settings_page.py       # Settings page component
└── windows/                   # Window components
    ├── __init__.py
    └── main_window.py         # Main application window
```

## Key Features

### Modular Architecture
- **Core**: Contains all business logic, utilities, and data management
- **UI**: Reusable UI components and widgets
- **Pages**: Complete page implementations
- **Windows**: Main window and dialog components

### Clean Separation of Concerns
- Each module has a specific responsibility
- Minimal coupling between modules
- Easy to maintain and extend

### 1:1 Function Mapping
- All functions from the original `mantatools.py` have been preserved
- Functions are organized logically into appropriate modules
- No functionality has been lost in the refactoring

## Usage

### Running the Application
```bash
python main.py
```

### Importing Components
```python
from mantatools import main, MainWindow
from mantatools.core import ensure_types_for, load_user_settings
from mantatools.ui import Snack, ModernProgressBar
from mantatools.pages import SettingsPage, GameDetail
```

## Benefits of This Structure

1. **Maintainability**: Each module has a clear purpose and is easy to understand
2. **Reusability**: UI components can be easily reused across different pages
3. **Testability**: Individual modules can be tested in isolation
4. **Scalability**: New features can be added without affecting existing code
5. **Readability**: Code is organized logically and easy to navigate

## Migration from Original

The original `mantatools.py` file contained all functionality in a single file. This refactoring:

- Preserves all existing functionality
- Organizes code into logical modules
- Improves code maintainability
- Makes the codebase more professional and scalable

All imports have been updated to use the new modular structure, ensuring compatibility with existing code that might depend on specific functions.
