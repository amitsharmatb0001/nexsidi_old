"""
INTEGRATION TEST RUNNER - ALL 9 AGENTS
Location: backend/tests/run_integration_test.py

Quick test runner for the full pipeline integration test.

Usage:
    # Run all tests
    python tests/run_integration_test.py
    
    # Run specific test class
    python tests/run_integration_test.py --test individual
    python tests/run_integration_test.py --test pipeline
    python tests/run_integration_test.py --test errors
    
    # Verbose output
    python tests/run_integration_test.py --verbose
"""

import sys
import os
import asyncio
import argparse
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))


def run_tests(test_class: str = "all", verbose: bool = False):
    """
    Run integration tests.
    
    Args:
        test_class: Which test class to run (all, individual, pipeline, errors, performance)
        verbose: Show detailed output
    """
    import pytest
    
    # Build pytest args
    args = [
        "tests/integration/test_full_pipeline.py",
        "-v" if verbose else "",
        "-s",  # Show print statements
        "--tb=short",  # Short traceback
        "--color=yes"
    ]
    
    # Filter by test class
    if test_class != "all":
        test_map = {
            "individual": "TestIndividualAgents",
            "pipeline": "TestFullPipeline",
            "errors": "TestErrorHandling",
            "performance": "TestPerformance"
        }
        
        if test_class in test_map:
            args.append(f"-k {test_map[test_class]}")
        else:
            print(f"❌ Unknown test class: {test_class}")
            print(f"Available: {', '.join(test_map.keys())}")
            return 1
    
    # Remove empty strings
    args = [arg for arg in args if arg]
    
    print("="*80)
    print("NEXSIDI INTEGRATION TEST - ALL 9 AGENTS")
    print("="*80)
    print(f"Test Class: {test_class}")
    print(f"Verbose: {verbose}")
    print("="*80 + "\n")
    
    # Run pytest
    return pytest.main(args)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Run NexSidi integration tests for all 9 agents"
    )
    
    parser.add_argument(
        "--test",
        choices=["all", "individual", "pipeline", "errors", "performance"],
        default="all",
        help="Which test class to run"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show verbose output"
    )
    
    args = parser.parse_args()
    
    # Run tests
    exit_code = run_tests(test_class=args.test, verbose=args.verbose)
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
