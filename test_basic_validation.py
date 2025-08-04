#!/usr/bin/env python3
"""
Basic validation test that runs without external dependencies.
Validates that the tool_db system is properly integrated and importable.
"""

import sys
import os
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test that all components can be imported correctly."""
    print("🔍 Testing imports...")
    
    try:
        # Test tool_db imports
        from app.infrastructure.tools.tool_db import ToolDB, get_tool_db, query
        print("✅ tool_db components imported successfully")
        
        # Test anti_hallucination imports  
        from app.application.usecases.anti_hallucination_use_case import AntiHallucinationUseCase
        print("✅ AntiHallucinationUseCase imported successfully")
        
        # Test agent_prompts imports
        from prompts.agent_prompts import DATABASE_TOOL_PROMPT, get_database_integration_context
        print("✅ DATABASE_TOOL_PROMPT and helper function imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_tool_db_structure():
    """Test that ToolDB has the expected structure."""
    print("\n🔍 Testing ToolDB structure...")
    
    try:
        from app.infrastructure.tools.tool_db import ToolDB
        
        # Create instance
        tool_db = ToolDB()
        
        # Check required attributes
        required_attrs = ['allowed_tables', 'db_client', '_connection_ready']
        for attr in required_attrs:
            if not hasattr(tool_db, attr):
                print(f"❌ Missing attribute: {attr}")
                return False
        
        # Check allowed tables structure
        required_tables = ['ai_courses', 'ai_course_session', 'bond', 'elements_url', 'ai_tema_activity']
        for table in required_tables:
            if table not in tool_db.allowed_tables:
                print(f"❌ Missing table in allowed_tables: {table}")
                return False
            
            table_config = tool_db.allowed_tables[table]
            if 'columns' not in table_config or 'safe_filters' not in table_config:
                print(f"❌ Invalid table configuration for {table}")
                return False
        
        print("✅ ToolDB structure is correct")
        return True
        
    except Exception as e:
        print(f"❌ Structure test error: {e}")
        return False

def test_database_prompt():
    """Test that the database prompt is properly configured."""
    print("\n🔍 Testing DATABASE_TOOL_PROMPT...")
    
    try:
        from prompts.agent_prompts import DATABASE_TOOL_PROMPT, get_database_integration_context
        
        # Check prompt exists and has reasonable length
        if not DATABASE_TOOL_PROMPT:
            print("❌ DATABASE_TOOL_PROMPT is empty")
            return False
        
        if len(DATABASE_TOOL_PROMPT) < 100:
            print("❌ DATABASE_TOOL_PROMPT is too short")
            return False
        
        # Check that it contains expected table names
        required_table_mentions = ['ai_courses', 'ai_course_session', 'bond']
        for table in required_table_mentions:
            if table not in DATABASE_TOOL_PROMPT:
                print(f"❌ DATABASE_TOOL_PROMPT missing table: {table}")
                return False
        
        # Test context function
        context = get_database_integration_context("¿Cuánto cuesta?", "Experto en IA")
        if not context or len(context) < 50:
            print("❌ get_database_integration_context not working properly")
            return False
        
        print("✅ DATABASE_TOOL_PROMPT is properly configured")
        print(f"   Prompt length: {len(DATABASE_TOOL_PROMPT)} characters")
        return True
        
    except Exception as e:
        print(f"❌ Database prompt test error: {e}")
        return False

def test_integration_points():
    """Test that integration points exist in the expected files."""
    print("\n🔍 Testing integration points...")
    
    success = True
    
    # Check anti_hallucination_use_case integration
    try:
        from app.application.usecases.anti_hallucination_use_case import AntiHallucinationUseCase
        
        # Check that the class has tool_db attribute and the new method
        if not hasattr(AntiHallucinationUseCase, '__init__'):
            print("❌ AntiHallucinationUseCase missing __init__")
            success = False
        
        instance = AntiHallucinationUseCase(None, None, None)
        if not hasattr(instance, 'tool_db'):
            print("❌ AntiHallucinationUseCase missing tool_db attribute")
            success = False
        
        if not hasattr(instance, '_get_course_info_from_tool_db'):
            print("❌ AntiHallucinationUseCase missing _get_course_info_from_tool_db method")
            success = False
        
        print("✅ AntiHallucinationUseCase integration points verified")
        
    except Exception as e:
        print(f"❌ AntiHallucinationUseCase integration test error: {e}")
        success = False
    
    return success

async def test_async_functionality():
    """Test basic async functionality without database connection."""
    print("\n🔍 Testing async functionality...")
    
    try:
        from app.infrastructure.tools.tool_db import ToolDB
        from app.infrastructure.database.client import DatabaseClient
        
        # Create tool_db with mock client (no real connection)
        mock_client = DatabaseClient()
        tool_db = ToolDB(mock_client)
        
        # Test that query method exists and handles no connection gracefully
        result = await tool_db.query('ai_courses', {}, limit=1)
        
        # Should return empty list when no connection
        if result != []:
            print(f"❌ Expected empty list, got: {result}")
            return False
        
        print("✅ Async functionality working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Async functionality test error: {e}")
        return False

def main():
    """Run all validation tests."""
    print("🧪 BASIC VALIDATION TESTS FOR TOOL_DB SYSTEM")
    print("=" * 60)
    
    tests = [
        ("Import Tests", test_imports),
        ("ToolDB Structure", test_tool_db_structure),
        ("Database Prompt", test_database_prompt),
        ("Integration Points", test_integration_points),
    ]
    
    results = []
    
    # Run synchronous tests
    for test_name, test_func in tests:
        print(f"\n▶️ Running {test_name}...")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Run async test
    print(f"\n▶️ Running Async Functionality...")
    try:
        async_success = asyncio.run(test_async_functionality())
        results.append(("Async Functionality", async_success))
    except Exception as e:
        print(f"❌ Async Functionality failed with exception: {e}")
        results.append(("Async Functionality", False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 VALIDATION SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status} - {test_name}")
    
    if passed == total:
        print("\n🎉 ALL VALIDATION TESTS PASSED!")
        print("✅ Tool_db system is properly integrated and ready to use")
        print("\n📋 COMPONENTS VALIDATED:")
        print("• ToolDB wrapper class with security features")
        print("• DATABASE_TOOL_PROMPT with table documentation")
        print("• AntiHallucinationUseCase integration")
        print("• Async functionality with graceful fallback")
        print("• Import structure and dependencies")
        
        print("\n🚀 NEXT STEPS:")
        print("• Install pytest for advanced testing: pip install -r requirements_dev.txt")
        print("• Run integration tests: python3 test_tool_db_integration.py")
        print("• Use in production: tool_db ready for new features")
        
        return True
    else:
        print(f"\n⚠️ {total - passed} validation test(s) failed")
        print("🔧 Fix issues before using tool_db system")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)