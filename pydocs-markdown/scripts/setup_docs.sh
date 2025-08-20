#!/bin/sh

set -e  # Exit on error

echo "📚 Setting up Python documentation automation with pydoc-markdown"
echo "================================================================"

# Check Python version
python_version=$(python3 --version 2>&1 | grep -Po '(?<=Python )[\d.]+')
echo "✓ Python version: $python_version"

# Create necessary directories
echo ""
echo "Creating directory structure..."
mkdir -p scripts
mkdir -p docs/api/uml
mkdir -p .github/workflows

# Create requirements file if it doesn't exist
echo ""
echo "Creating requirements file..."
cat > requirements-docs.txt << 'EOF'
# Documentation generation requirements
pydoc-markdown>=4.8.2
pydoc-markdown[markdown]>=4.8.2
pylint>=2.15.0  # For pyreverse UML generation
pyyaml>=6.0
pathlib>=1.0.1

# Optional: for better markdown rendering
pygments>=2.16.0
markupsafe>=2.1.0
EOF
echo "  ✓ Created requirements-docs.txt"

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements-docs.txt
echo "  ✓ Dependencies installed"

# Create default pydoc-markdown.yml if it doesn't exist
if [ ! -f "pydoc-markdown.yml" ]; then
    echo ""
    echo "Creating default pydoc-markdown.yml configuration..."
    cat > pydoc-markdown.yml << 'EOF'
# Auto-generated pydoc-markdown configuration
# Customize this file based on your project structure

loaders:
  - type: python
    search_path: [src]  # Change to your source directory
    modules: ["**"]  # Document all modules

processors:
  - type: filter
    skip_empty_modules: true
    exclude_private: false
    exclude_special: false
  - type: smart
  - type: crossref

renderer:
  type: markdown
  render_module_header: true
  descriptive_class_title: true
  descriptive_function_title: true
  add_method_class_prefix: true
  signature_with_def: true
EOF
    echo "  ✓ Created pydoc-markdown.yml"
    echo "  ⚠ Please edit pydoc-markdown.yml to match your project structure"
fi

# Test the setup
echo ""
echo "Testing the setup..."
if command -v pyreverse &> /dev/null; then
    echo "  ✓ pyreverse (UML generator) is available"
else
    echo "  ✗ pyreverse not found - UML generation will not work"
fi

if python3 -c "import pydoc_markdown" 2>/dev/null; then
    echo "  ✓ pydoc-markdown is installed"
else
    echo "  ✗ pydoc-markdown import failed"
fi

# Create a simple Makefile for convenience
echo ""
echo "Creating Makefile for convenience..."
cat > Makefile.docs << 'EOF'
# Makefile for documentation generation

.PHONY: docs docs-no-uml docs-clean docs-serve help

# Default source and output directories
SOURCE_DIR ?= src
OUTPUT_DIR ?= docs/api
UML_DIR ?= docs/api/uml

help:
	@echo "Documentation generation commands:"
	@echo "  make docs          - Generate documentation with UML diagrams"
	@echo "  make docs-no-uml   - Generate documentation without UML"
	@echo "  make docs-clean    - Clean generated documentation"
	@echo "  make docs-serve    - Serve documentation locally (requires Python http.server)"

docs:
	@echo "Generating documentation with UML diagrams..."
	python scripts/generate_docs.py $(SOURCE_DIR) $(OUTPUT_DIR) --uml-dir $(UML_DIR)

docs-no-uml:
	@echo "Generating documentation without UML diagrams..."
	python scripts/generate_docs.py $(SOURCE_DIR) $(OUTPUT_DIR) --no-uml

docs-clean:
	@echo "Cleaning documentation..."
	rm -rf $(OUTPUT_DIR)
	@echo "Documentation cleaned"

docs-serve: docs
	@echo "Serving documentation at http://localhost:8000/docs/api/"
	cd docs && python -m http.server 8000

# Install documentation dependencies
docs-deps:
	pip install -r requirements-docs.txt
EOF
echo "  ✓ Created Makefile.docs"

# Provide usage instructions
echo ""
echo "================================================================"
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit 'pydoc-markdown.yml' to configure your source directory"
echo "2. Copy the Python script to 'scripts/generate_docs.py'"
echo "3. Copy the GitHub Actions workflow to '.github/workflows/generate-docs.yml'"
echo ""
echo "To generate documentation manually:"
echo "  python scripts/generate_docs.py <source_dir> <output_dir>"
echo ""
echo "Or use the Makefile:"
echo "  make -f Makefile.docs docs"
echo ""
echo "The GitHub Actions workflow will automatically generate"
echo "documentation on every push to main/develop branches."
echo "================================================================"
