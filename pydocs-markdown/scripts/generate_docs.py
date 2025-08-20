import os
import sys
import json
import yaml
import subprocess
import argparse
from pathlib import Path
from typing import Dict, List, Optional
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class PyDocMarkdownGenerator:
    """Wrapper for pydoc-markdown with UML generation."""
    
    def __init__(self, source_dir: str, output_dir: str, uml_dir: Optional[str] = None):
        """
        Initialize the documentation generator.
        
        Args:
            source_dir: Root directory containing Python source files
            output_dir: Directory where markdown files will be saved
            uml_dir: Directory for UML diagrams (optional)
        """
        self.source_dir = Path(source_dir).resolve()
        self.output_dir = Path(output_dir).resolve()
        self.uml_dir = Path(uml_dir).resolve() if uml_dir else self.output_dir / "uml"
        
        # Create directories
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.uml_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Source directory: {self.source_dir}")
        logger.info(f"Output directory: {self.output_dir}")
        logger.info(f"UML directory: {self.uml_dir}")
    
    def generate_uml_for_module(self, module_path: Path) -> Optional[str]:
        """
        Generate UML diagram for a Python module using pyreverse.
        
        Args:
            module_path: Path to the Python module
            
        Returns:
            Relative path to the generated UML diagram or None if failed
        """
        try:
            # Get module name for output
            relative_path = module_path.relative_to(self.source_dir)
            module_name = str(relative_path.with_suffix('')).replace('/', '_').replace('\\', '_')
            
            # Output path for UML
            output_name = f"classes_{module_name}"
            
            # Run pyreverse
            cmd = [
                "pyreverse",
                "-o", "png",
                "-p", module_name,
                "-d", str(self.uml_dir),
                "--colorized",
                "--module-names", "y",
                str(module_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Check if file was created
                uml_file = self.uml_dir / f"{output_name}.png"
                if uml_file.exists():
                    logger.info(f"  ✓ Generated UML: {uml_file.name}")
                    # Return relative path from output directory
                    return f"uml/{output_name}.png"
            else:
                logger.warning(f"  ✗ UML generation failed: {result.stderr}")
                
        except Exception as e:
            logger.warning(f"  ✗ Could not generate UML: {e}")
        
        return None
    
    def create_pydoc_config(self, modules: List[Path]) -> Dict:
        """
        Create pydoc-markdown configuration for given modules.
        
        Args:
            modules: List of Python module paths
            
        Returns:
            Configuration dictionary for pydoc-markdown
        """
        # Convert paths to module names
        module_names = []
        for module_path in modules:
            try:
                relative_path = module_path.relative_to(self.source_dir)
                module_name = str(relative_path.with_suffix('')).replace('/', '.').replace('\\', '.')
                module_names.append(module_name)
            except ValueError:
                logger.warning(f"Module {module_path} is not in source directory")
        
        config = {
            'loaders': [
                {
                    'type': 'python',
                    'search_path': [str(self.source_dir)],
                    'modules': module_names,
                    'filter': {
                        'skip_empty_modules': True,
                        'exclude_private': False,  # Include private methods with docstrings
                        'exclude_special': False   # Include __init__, __str__, etc.
                    }
                }
            ],
            'processors': [
                {
                    'type': 'filter',
                    'skip_empty_modules': True,
                    'documented_only': False,
                    'exclude_private': False,
                    'exclude_special': False
                },
                {
                    'type': 'smart',
                    'show_module_path': True
                },
                {
                    'type': 'crossref'
                }
            ],
            'renderer': {
                'type': 'markdown',
                'render_module_header': True,
                'render_toc': True,
                'render_toc_title': '## Table of Contents',
                'render_module_header_template': '# {module_name}\n\n',
                'render_class_header_template': '## {class_name}\n\n',
                'render_function_header_template': '### {function_name}\n\n',
                'descriptive_class_title': True,
                'descriptive_function_title': True,
                'add_method_class_prefix': True,
                'add_member_class_prefix': True,
                'code_block_style': 'fenced',
                'format_code': True,
                'signature_with_def': True,
                'use_fixed_header_levels': True,
                'header_level_by_type': {
                    'Module': 1,
                    'Class': 2,
                    'Method': 3,
                    'Function': 3,
                    'Data': 3
                }
            }
        }
        
        return config
    
    def process_single_module(self, module_path: Path) -> bool:
        """
        Process a single Python module to generate documentation.
        
        Args:
            module_path: Path to the Python module
            
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Processing: {module_path}")
        
        try:
            # Generate UML diagram
            uml_path = self.generate_uml_for_module(module_path)
            
            # Create pydoc-markdown config for this module
            config = self.create_pydoc_config([module_path])
            
            # Save config to temporary file
            config_file = self.output_dir / '.pydoc-markdown.yml'
            with open(config_file, 'w') as f:
                yaml.dump(config, f)
            
            # Determine output file path
            relative_path = module_path.relative_to(self.source_dir)
            output_path = self.output_dir / relative_path.with_suffix('.md')
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Run pydoc-markdown
            cmd = [
                sys.executable, "-m", "pydoc_markdown",
                "-c", str(config_file),
                "--quiet"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Get the output
                markdown_content = result.stdout
                
                # Add UML diagram reference if generated
                if uml_path:
                    # Insert UML after the module header
                    lines = markdown_content.split('\n')
                    for i, line in enumerate(lines):
                        if line.startswith('# ') and i < len(lines) - 1:
                            # Found module header, insert UML after it
                            lines.insert(i + 1, f"\n![UML Class Diagram]({uml_path})\n")
                            break
                    markdown_content = '\n'.join(lines)
                
                # Add file metadata
                metadata = f"<!-- Generated from: {relative_path} -->\n\n"
                markdown_content = metadata + markdown_content
                
                # Write to file
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(markdown_content)
                
                logger.info(f"  ✓ Generated: {output_path}")
                
                # Clean up config file
                config_file.unlink()
                return True
            else:
                logger.error(f"  ✗ Failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"  ✗ Error processing {module_path}: {e}")
            return False
    
    def generate_batch_documentation(self, config_path: Optional[str] = None) -> None:
        """
        Generate documentation for multiple modules using a config file.
        
        Args:
            config_path: Path to pydoc-markdown.yml config file
        """
        if config_path and Path(config_path).exists():
            logger.info(f"Using config file: {config_path}")
            
            # Run pydoc-markdown with the config file
            cmd = [
                sys.executable, "-m", "pydoc_markdown",
                "-c", config_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Save output
                output_file = self.output_dir / "documentation.md"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(result.stdout)
                logger.info(f"✓ Generated batch documentation: {output_file}")
            else:
                logger.error(f"✗ Batch generation failed: {result.stderr}")
    
    def generate_documentation(self, 
                             include_patterns: List[str] = None,
                             exclude_patterns: List[str] = None) -> None:
        """
        Generate documentation for all Python files matching patterns.
        
        Args:
            include_patterns: List of glob patterns to include (default: ["**/*.py"])
            exclude_patterns: List of glob patterns to exclude
        """
        include_patterns = include_patterns or ["**/*.py"]
        exclude_patterns = exclude_patterns or [
            "**/test_*.py", "**/*_test.py", "**/__pycache__/**",
            "**/tests/**", "**/venv/**", "**/env/**", "**/.venv/**"
        ]
        
        # Find all Python files
        python_files = []
        for pattern in include_patterns:
            python_files.extend(self.source_dir.glob(pattern))
        
        # Remove duplicates and sort
        python_files = sorted(set(python_files))
        
        # Filter out excluded patterns
        filtered_files = []
        for file_path in python_files:
            excluded = False
            for pattern in exclude_patterns:
                if file_path.match(pattern):
                    excluded = True
                    break
            if not excluded:
                filtered_files.append(file_path)
        
        logger.info(f"Found {len(filtered_files)} Python files to document")
        
        # Process each file
        successful = 0
        failed = 0
        for file_path in filtered_files:
            if self.process_single_module(file_path):
                successful += 1
            else:
                failed += 1
        
        # Generate index
        self.generate_index()
        
        # Summary
        logger.info(f"\n{'='*50}")
        logger.info(f"Documentation generation complete!")
        logger.info(f"  ✓ Successful: {successful}")
        if failed > 0:
            logger.info(f"  ✗ Failed: {failed}")
        logger.info(f"  📁 Output directory: {self.output_dir}")
    
    def generate_index(self) -> None:
        """Generate an index file listing all documented modules."""
        logger.info("Generating documentation index...")
        
        md_files = sorted(self.output_dir.rglob("*.md"))
        md_files = [f for f in md_files if f.name != "index.md" and f.name != "README.md"]
        
        index_content = ["# Documentation Index\n"]
        index_content.append(f"Generated documentation for {len(md_files)} modules.\n")
        
        # Group by directory
        by_package = {}
        for md_file in md_files:
            relative_path = md_file.relative_to(self.output_dir)
            package = relative_path.parent
            if package not in by_package:
                by_package[package] = []
            by_package[package].append(relative_path)
        
        # Generate index content
        for package in sorted(by_package.keys()):
            if str(package) != ".":
                index_content.append(f"\n## {package}\n")
            else:
                index_content.append(f"\n## Root Modules\n")
            
            for file_path in sorted(by_package[package]):
                module_name = file_path.stem
                index_content.append(f"- [{module_name}]({file_path})")
        
        # Add UML diagrams section if any exist
        uml_files = list(self.uml_dir.glob("*.png"))
        if uml_files:
            index_content.append(f"\n## UML Diagrams\n")
            index_content.append(f"Generated {len(uml_files)} UML class diagrams.\n")
            for uml_file in sorted(uml_files):
                name = uml_file.stem.replace("classes_", "")
                index_content.append(f"- [{name}](uml/{uml_file.name})")
        
        # Write index
        index_path = self.output_dir / "index.md"
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(index_content))
        
        logger.info(f"  ✓ Generated index: {index_path}")


def main():
    """Main entry point for the documentation generator."""
    parser = argparse.ArgumentParser(
        description="Generate Python documentation using pydoc-markdown with UML diagrams"
    )
    parser.add_argument(
        "source",
        help="Source directory containing Python files"
    )
    parser.add_argument(
        "output",
        help="Output directory for documentation"
    )
    parser.add_argument(
        "--uml-dir",
        help="Directory for UML diagrams (default: output/uml)"
    )
    parser.add_argument(
        "--config",
        help="Path to pydoc-markdown.yml config file for batch processing"
    )
    parser.add_argument(
        "--include",
        nargs="+",
        default=["**/*.py"],
        help="Include patterns (default: **/*.py)"
    )
    parser.add_argument(
        "--exclude",
        nargs="+",
        help="Exclude patterns"
    )
    parser.add_argument(
        "--no-uml",
        action="store_true",
        help="Skip UML diagram generation"
    )
    
    args = parser.parse_args()
    
    # Create generator
    generator = PyDocMarkdownGenerator(
        source_dir=args.source,
        output_dir=args.output,
        uml_dir=args.uml_dir
    )
    
    # Disable UML if requested
    if args.no_uml:
        generator.generate_uml_for_module = lambda x: None
    
    # Run appropriate generation method
    if args.config:
        generator.generate_batch_documentation(config_path=args.config)
    else:
        generator.generate_documentation(
            include_patterns=args.include,
            exclude_patterns=args.exclude
        )


if __name__ == "__main__":
    main()
