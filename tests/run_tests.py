#!/usr/bin/env python3
"""
Test runner for CargoOpt backend tests
"""

import pytest
import sys
import os

def main():
    """Run all tests"""
    # Add the project root to Python path
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, project_root)
    
    # Run tests
    exit_code = pytest.main([
        "tests/",
        "-v",
        "--tb=short",
        "--cov=backend",
        "--cov-report=html",
        "--cov-report=term"
    ])
    
    sys.exit(exit_code)

if __name__ == "__main__":
    main()