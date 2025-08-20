#!/usr/bin/env python3
"""
Quick script to generate documentation
Usage: python run_docs.py
"""

import subprocess
import sys
from pathlib import Path

def main():
    # Configuration
    SOURCE_DIR = "src"  # Change to your source directory
    OUTPUT_DIR = "docs/api"
    UML_DIR = "docs/api/uml"
    
    # Check if script exists
    script_path = Path("scripts/generate_docs.py")
    if not script_path.exists():
        print("Error: scripts/generate_docs.py not found!")
        print("Please ensure the documentation generator script is in place.")
        sys.exit(1)
    
    # Run documentation generator
    cmd = [
        sys.executable,
        str(script_path),
        SOURCE_DIR,
        OUTPUT_DIR,
        "--uml-dir", UML_DIR
    ]
    
    print(f"Generating documentation...")
    print(f"  Source: {SOURCE_DIR}")
    print(f"  Output: {OUTPUT_DIR}")
    print(f"  UML: {UML_DIR}")
    print()
    
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print("\n✅ Documentation generated successfully!")
        print(f"View documentation at: {OUTPUT_DIR}/index.md")
    else:
        print("\n❌ Documentation generation failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
