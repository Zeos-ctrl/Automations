# Python Documentation Automation with PyDoc-Markdown

This setup provides automated documentation generation for Python projects using `pydoc-markdown` with UML diagram generation via `pyreverse`. The documentation is automatically generated and committed back to your repository via GitHub Actions.

## Features

- [x] **Automatic Markdown Generation** - Converts Python docstrings to clean markdown documentation
- [x] **UML Class Diagrams** - Generates UML diagrams for each module using pyreverse
- [x] **GitHub Actions Integration** - Automatically updates docs on every push
- [x] **In-Repository Storage** - Documentation stays in your private repo
- [x] **Customizable Format** - Matches your specified documentation style
- [x] **Incremental Updates** - Only regenerates changed files
- [x] **Pull Request Comments** - Preview documentation changes in PRs

## Quick Start

### 1. Initial Setup

```bash
# Install dependencies
pip install pydoc-markdown[markdown] pylint pyyaml

# Create directory structure
mkdir -p scripts docs/api .github/workflows
```

### 2. Add Required Files

Copy these files to your repository:

1. **`scripts/generate_docs.py`** - The main documentation generator (from first artifact)
2. **`pydoc-markdown.yml`** - Configuration file (from second artifact)
3. **`.github/workflows/generate-docs.yml`** - GitHub Actions workflow (from third artifact)
4. **`requirements-docs.txt`** - Documentation dependencies

### 3. Configure for Your Project

Edit `pydoc-markdown.yml`:
```yaml
loaders:
  - type: python
    search_path: [src]  # Change to your source directory
    modules: ["**"]     # Or specify specific modules
```

Edit the GitHub Actions workflow:
```yaml
env:
  SOURCE_DIR: src       # Your source directory
  OUTPUT_DIR: docs/api  # Where to save documentation
  UML_DIR: docs/api/uml # Where to save UML diagrams
```

### 4. Run Locally (Optional)

```bash
# Generate documentation manually
python scripts/generate_docs.py src docs/api

# Or use the Makefile
make -f Makefile.docs docs
```

## Usage

### Automatic Generation

Documentation is automatically generated when:
- You push to `main` or `develop` branches
- Python files are modified
- You manually trigger the workflow

### Manual Generation

```bash
# Basic usage
python scripts/generate_docs.py <source_dir> <output_dir>

# With custom UML directory
python scripts/generate_docs.py src docs/api --uml-dir docs/uml

# Skip UML generation (faster)
python scripts/generate_docs.py src docs/api --no-uml

# Custom include/exclude patterns
python scripts/generate_docs.py src docs/api \
  --include "**/*.py" \
  --exclude "test_*.py" "*_test.py"
```

### Using the Makefile

```bash
make -f Makefile.docs docs          # Generate with UML
make -f Makefile.docs docs-no-uml   # Generate without UML
make -f Makefile.docs docs-clean    # Clean generated docs
make -f Makefile.docs docs-serve    # Serve docs locally
```

## Documentation Format

The generated documentation follows this structure:

```
docs/api/
├── index.md                 # Main index with links to all modules
├── module1.md              # Documentation for module1.py
├── package/
│   ├── submodule.md       # Documentation for package/submodule.py
│   └── ...
└── uml/
    ├── classes_module1.png # UML diagram for module1
    └── ...
```

Each markdown file contains:
- Module/class description
- Constructor documentation (for classes)
- Method signatures and descriptions
- Function documentation
- UML class diagram (if applicable)

## Docstring Styles

The tool supports multiple docstring formats:

### Google Style (Recommended)
```python
def function(param1: str, param2: int) -> bool:
    """Brief description of function.
    
    Longer description if needed.
    
    Args:
        param1: Description of param1
        param2: Description of param2
    
    Returns:
        Description of return value
    
    Raises:
        ValueError: When something is wrong
    """
```

### NumPy Style
```python
def function(param1, param2):
    """
    Brief description.
    
    Parameters
    ----------
    param1 : str
        Description of param1
    param2 : int
        Description of param2
    
    Returns
    -------
    bool
        Description of return value
    """
```

## GitHub Actions Workflow

The workflow automatically:

1. **Triggers on:**
   - Push to main/develop branches
   - Pull requests
   - Manual dispatch

2. **Actions performed:**
   - Install dependencies
   - Generate documentation
   - Create UML diagrams
   - Commit changes back to repository
   - Comment on PRs with preview
   - Upload artifacts

3. **Customization:**
   - Edit `.github/workflows/generate-docs.yml`
   - Adjust paths and branches as needed
   - Add/remove trigger conditions

## Advanced Configuration

### Custom Templates

Edit the renderer templates in `pydoc-markdown.yml`:

```yaml
renderer:
  render_class_header_template: |
    ## Class: {class_name}
    **Inherits from:** {bases}
```

### Exclude Patterns

```yaml
filter:
  exclude:
    - "test_.*"
    - ".*_test"
    - "_internal.*"
```

### Multiple Source Directories

```yaml
loaders:
  - type: python
    search_path: [src, lib, utils]
```

## Troubleshooting

### Common Issues

1. **Import errors during generation**
   - Ensure your project is installed or PYTHONPATH is set
   - Install project dependencies: `pip install -r requirements.txt`

2. **UML generation fails**
   - Install graphviz system package: `sudo apt-get install graphviz`
   - Check pyreverse is installed: `pip install pylint`

3. **Documentation not updating**
   - Check GitHub Actions logs
   - Ensure workflow has write permissions
   - Verify file paths in configuration

4. **Large repositories**
   - Use `--no-uml` flag to speed up generation
   - Specify specific modules instead of `**`

### Debug Mode

Run with verbose output:
```bash
python scripts/generate_docs.py src docs/api --verbose
```

Check pydoc-markdown directly:
```bash
pydoc-markdown -c pydoc-markdown.yml --verbose
```

## Integration with Existing Documentation

### Adding to MkDocs

```yaml
# mkdocs.yml
nav:
  - Home: index.md
  - API Reference: api/index.md
```

### Adding to Sphinx

```python
# conf.py
html_extra_path = ['../docs/api']
```

### Adding to README

```markdown
## API Documentation

Full API documentation is available in [docs/api/](docs/api/index.md).
```

## Best Practices

1. **Write good docstrings** - The quality of generated docs depends on your docstrings
2. **Use type hints** - They're included in the documentation
3. **Document classes** - Include class-level docstrings
4. **Keep it updated** - Let GitHub Actions handle regeneration
5. **Review PR previews** - Check documentation changes in pull requests

## File Structure Example

```
your-project/
├── src/                     # Your source code
│   ├── __init__.py
│   ├── module1.py
│   └── package/
│       └── module2.py
├── scripts/
│   └── generate_docs.py     # Documentation generator
├── docs/
│   └── api/                 # Generated documentation
│       ├── index.md
│       ├── module1.md
│       └── uml/
├── .github/
│   └── workflows/
│       └── generate-docs.yml
├── pydoc-markdown.yml      # Configuration
└── requirements-docs.txt    # Documentation dependencies
```

## License

This documentation automation setup is provided as-is for use in your projects.

## Support

For issues with:
- **pydoc-markdown**: Check [pydoc-markdown documentation](https://pydoc-markdown.readthedocs.io/)
- **pyreverse**: See [Pylint documentation](https://pylint.readthedocs.io/en/latest/pyreverse.html)
- **GitHub Actions**: Refer to [GitHub Actions documentation](https://docs.github.com/en/actions)
