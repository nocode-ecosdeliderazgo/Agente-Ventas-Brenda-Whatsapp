#!/usr/bin/env python3
"""
Test runner script for the database wrapper tool system.
Provides easy commands for running different types of tests.
"""

import sys
import subprocess
import os
from pathlib import Path

def print_header(title: str):
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print(f"{'='*60}")

def run_command(cmd: list, description: str):
    """Run a command and handle errors."""
    print(f"\n▶️ {description}")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed with exit code {e.returncode}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False
    except FileNotFoundError:
        print(f"❌ Command not found: {cmd[0]}")
        print(f"   Install it with: pip install {cmd[0]}")
        return False

def check_dependencies():
    """Check if required dependencies are installed."""
    print_header("CHECKING DEPENDENCIES")
    
    dependencies = ["pytest", "ruff", "mypy"]
    missing = []
    
    for dep in dependencies:
        try:
            subprocess.run([dep, "--version"], check=True, capture_output=True)
            print(f"✅ {dep} is installed")
        except (subprocess.CalledProcessError, FileNotFoundError):
            missing.append(dep)
            print(f"❌ {dep} is missing")
    
    if missing:
        print(f"\n💡 Install missing dependencies with:")
        print(f"   pip install -r requirements_dev.txt")
        return False
    
    return True

def run_unit_tests():
    """Run unit tests for the tool_db system."""
    print_header("RUNNING UNIT TESTS")
    
    test_files = [
        "tests/test_tool_db.py",
        "tests/test_generate_intelligent_response.py", 
        "tests/test_anti_hallucination.py"
    ]
    
    # Check if test files exist
    missing_tests = []
    for test_file in test_files:
        if not os.path.exists(test_file):
            missing_tests.append(test_file)
    
    if missing_tests:
        print(f"❌ Missing test files: {missing_tests}")
        return False
    
    # Run pytest
    cmd = ["python3", "-m", "pytest"] + test_files + ["-v", "--tb=short"]
    return run_command(cmd, "Running pytest on tool_db test suite")

def run_integration_tests():
    """Run integration tests."""
    print_header("RUNNING INTEGRATION TESTS")
    
    integration_test = "test_tool_db_integration.py"
    if not os.path.exists(integration_test):
        print(f"❌ Integration test file not found: {integration_test}")
        return False
    
    cmd = ["python3", integration_test]
    return run_command(cmd, "Running integration test suite")

def run_linting():
    """Run code linting with ruff."""
    print_header("RUNNING CODE LINTING")
    
    files_to_lint = [
        "app/infrastructure/tools/tool_db.py",
        "app/application/usecases/anti_hallucination_use_case.py",
        "app/application/usecases/generate_intelligent_response.py",
        "prompts/agent_prompts.py"
    ]
    
    success = True
    
    for file_path in files_to_lint:
        if os.path.exists(file_path):
            cmd = ["ruff", "check", file_path]
            if not run_command(cmd, f"Linting {file_path}"):
                success = False
        else:
            print(f"⚠️ File not found: {file_path}")
    
    return success

def run_type_checking():
    """Run type checking with mypy."""
    print_header("RUNNING TYPE CHECKING")
    
    files_to_check = [
        "app/infrastructure/tools/tool_db.py",
        "tests/test_tool_db.py"
    ]
    
    success = True
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            cmd = ["mypy", file_path, "--ignore-missing-imports"]
            if not run_command(cmd, f"Type checking {file_path}"):
                success = False
        else:
            print(f"⚠️ File not found: {file_path}")
    
    return success

def run_all_tests():
    """Run complete test suite."""
    print_header("RUNNING COMPLETE TEST SUITE")
    
    tests = [
        ("Dependency Check", check_dependencies),
        ("Unit Tests", run_unit_tests),
        ("Integration Tests", run_integration_tests),
        ("Code Linting", run_linting),
        ("Type Checking", run_type_checking)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔄 Running {test_name}...")
        success = test_func()
        results.append((test_name, success))
        
        if success:
            print(f"✅ {test_name} passed")
        else:
            print(f"❌ {test_name} failed")
    
    # Summary
    print_header("TEST SUMMARY")
    
    passed_tests = sum(1 for _, success in results if success)
    total_tests = len(results)
    
    print(f"\n📊 Results: {passed_tests}/{total_tests} tests passed")
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {status} - {test_name}")
    
    if passed_tests == total_tests:
        print(f"\n🎉 ALL TESTS PASSED!")
        print("✅ Database wrapper tool system is ready for production")
        return True
    else:
        print(f"\n⚠️ {total_tests - passed_tests} test(s) failed")
        print("🔧 Fix issues before using in production")
        return False

def main():
    """Main test runner function."""
    if len(sys.argv) < 2:
        print("🧪 Test Runner for Database Wrapper Tool System")
        print("\nUsage:")
        print("  python3 run_tests.py [command]")
        print("\nCommands:")
        print("  all          - Run complete test suite")
        print("  unit         - Run unit tests only")
        print("  integration  - Run integration tests only")
        print("  lint         - Run code linting only")
        print("  types        - Run type checking only")
        print("  deps         - Check dependencies only")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    # Change to project root directory
    os.chdir(Path(__file__).parent)
    
    if command == "all":
        success = run_all_tests()
    elif command == "unit":
        success = run_unit_tests()
    elif command == "integration":
        success = run_integration_tests()
    elif command == "lint":
        success = run_linting()
    elif command == "types":
        success = run_type_checking()
    elif command == "deps":
        success = check_dependencies()
    else:
        print(f"❌ Unknown command: {command}")
        sys.exit(1)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()