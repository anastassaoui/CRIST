# CRIST Documentation

This directory contains the Sphinx documentation for the CRIST project.

## Building the Documentation

### Windows

Simply run the build script from the project root:

```batch
build_docs.bat
```

This will:
1. Install documentation dependencies
2. Build the HTML documentation
3. Open it in your browser automatically

### Manual Build

If you prefer to build manually:

1. Install dependencies:
```batch
pip install -r requirements-docs.txt
```

2. Build HTML:
```batch
cd docs
sphinx-build -b html . _build/html
```

Or use the make.bat helper:
```batch
cd docs
make.bat html
```

3. Open the documentation:
```
docs\_build\html\index.html
```

## Documentation Structure

- `conf.py` - Sphinx configuration
- `index.rst` - Main documentation index
- `modules/` - Module-specific documentation
  - `evaporateurs.rst` - Evaporator module
  - `crystallizer.rst` - Crystallizer module
  - `optimisation.rst` - Optimization module
  - `visualization.rst` - Visualization module
  - `export.rst` - Export module

## Theme

The documentation uses the **Read the Docs** theme (`sphinx_rtd_theme`) for a professional, modern look.
