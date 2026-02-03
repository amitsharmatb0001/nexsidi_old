"""
TEST SCRIPT FOR SHUBHAM V2
Comprehensive testing of code generation agent
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from dotenv import load_dotenv
load_dotenv()

import asyncio
from shubham_v2_production import (
    Shubham,
    FileGenerationRequest,
    FileType,
    TilotmaValidator,
    generate_complete_backend
)


# =============================================================================
# TEST DATA
# =============================================================================

# Sample architecture for testing
SAMPLE_ARCHITECTURE = {
    "database": {
        "type": "PostgreSQL",
        "tables": [
            {
                "name": "users",
                "columns": [
                    {"name": "id", "type": "UUID", "primary_key": True},
                    {"name": "email", "type": "String", "unique": True},
                    {"name": "hashed_password", "type": "String"},
                    {"name": "is_active", "type": "Boolean", "default": True},
                    {"name": "created_at", "type": "DateTime"},
                ]
            },
            {
                "name": "posts",
                "columns": [
                    {"name": "id", "type": "UUID", "primary_key": True},
                    {"name": "title", "type": "String"},
                    {"name": "content", "type": "Text"},
                    {"name": "user_id", "type": "UUID", "foreign_key": "users.id"},
                    {"name": "created_at", "type": "DateTime"},
                ]
            }
        ]
    },
    "api": {
        "endpoints": [
            {
                "name": "auth",
                "endpoints": ["POST /register", "POST /login", "GET /me"]
            },
            {
                "name": "posts",
                "endpoints": ["GET /posts", "POST /posts", "GET /posts/{id}"]
            }
        ]
    },
    "authentication": {
        "type": "JWT",
        "token_expiry": 3600
    }
}


# =============================================================================
# TESTS
# =============================================================================

async def test_1_single_file_generation():
    """Test 1: Generate a single simple file"""
    print("\n" + "="*80)
    print("TEST 1: Single File Generation (database.py)")
    print("="*80)
    
    try:
        shubham = Shubham(
            project_id="test-project-123",
            user_id="test-user-456"
        )
        
        request = FileGenerationRequest(
            file_path="app/database.py",
            file_type=FileType.DATABASE,
            description="PostgreSQL database connection with SQLAlchemy",
            architecture=SAMPLE_ARCHITECTURE
        )
        
        result = await shubham.generate_file(request)
        
        print(f"✅ File generated: {result.file_path}")
        print(f"✅ Tokens used: {result.tokens_used}")
        print(f"✅ Model: {result.model_used}")
        print(f"✅ Cost: ₹{result.cost:.4f}")
        print(f"✅ Syntax valid: {result.syntax_valid}")
        print(f"✅ Was escalated: {result.was_escalated}")
        
        print(f"\n📄 Generated code (first 500 chars):")
        print(result.content[:500])
        print("...")
        
        return result.syntax_valid
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_2_models_generation():
    """Test 2: Generate models.py (more complex)"""
    print("\n" + "="*80)
    print("TEST 2: Models Generation (complex file)")
    print("="*80)
    
    try:
        shubham = Shubham(
            project_id="test-project-123",
            user_id="test-user-456"
        )
        
        request = FileGenerationRequest(
            file_path="app/models.py",
            file_type=FileType.MODELS,
            description="SQLAlchemy ORM models for all database tables",
            architecture=SAMPLE_ARCHITECTURE
        )
        
        result = await shubham.generate_file(request)
        
        print(f"✅ File generated: {result.file_path}")
        print(f"✅ Tokens used: {result.tokens_used}")
        print(f"✅ Model: {result.model_used}")
        print(f"✅ Syntax valid: {result.syntax_valid}")
        print(f"✅ Was split: {result.was_split}")
        
        # Check for expected content
        has_user_model = "class User" in result.content
        has_post_model = "class Post" in result.content
        has_imports = "from sqlalchemy import" in result.content
        
        print(f"✅ Has User model: {has_user_model}")
        print(f"✅ Has Post model: {has_post_model}")
        print(f"✅ Has imports: {has_imports}")
        
        print(f"\n📄 Generated code (first 500 chars):")
        print(result.content[:500])
        print("...")
        
        return result.syntax_valid and has_user_model and has_post_model
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_3_multiple_files():
    """Test 3: Generate multiple files in order"""
    print("\n" + "="*80)
    print("TEST 3: Multiple Files Generation")
    print("="*80)
    
    try:
        shubham = Shubham(
            project_id="test-project-123",
            user_id="test-user-456"
        )
        
        requests = [
            FileGenerationRequest(
                file_path="app/database.py",
                file_type=FileType.DATABASE,
                description="Database connection",
                architecture=SAMPLE_ARCHITECTURE
            ),
            FileGenerationRequest(
                file_path="app/models.py",
                file_type=FileType.MODELS,
                description="ORM models",
                architecture=SAMPLE_ARCHITECTURE
            ),
            FileGenerationRequest(
                file_path="requirements.txt",
                file_type=FileType.REQUIREMENTS,
                description="Python packages",
                architecture=SAMPLE_ARCHITECTURE
            ),
        ]
        
        results = await shubham.generate_multiple_files(requests)
        
        print(f"✅ Generated {len(results)} files")
        
        for result in results:
            print(f"  ✅ {result.file_path}: {result.tokens_used} tokens, "
                  f"₹{result.cost:.4f}, syntax_valid={result.syntax_valid}")
        
        total_tokens = sum(r.tokens_used for r in results)
        total_cost = sum(r.cost for r in results)
        all_valid = all(r.syntax_valid for r in results)
        
        print(f"\n✅ Total tokens: {total_tokens}")
        print(f"✅ Total cost: ₹{total_cost:.4f}")
        print(f"✅ All valid: {all_valid}")
        
        return all_valid
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_4_null_byte_cleaning():
    """Test 4: Verify NULL byte cleaning works"""
    print("\n" + "="*80)
    print("TEST 4: NULL Byte Cleaning")
    print("="*80)
    
    try:
        shubham = Shubham(
            project_id="test-project-123",
            user_id="test-user-456"
        )
        
        # Test cleaning function directly
        dirty_code = "from fastapi import\x00 FastAPI\napp = FastAPI()\x00"
        clean_code = shubham._clean_code_content(dirty_code)
        
        has_null_bytes = '\x00' in clean_code
        
        print(f"✅ Dirty code had NULL bytes: True")
        print(f"✅ Clean code has NULL bytes: {has_null_bytes}")
        print(f"✅ Cleaning worked: {not has_null_bytes}")
        
        # Test markdown removal
        markdown_code = "```python\nfrom fastapi import FastAPI\n```"
        clean_markdown = shubham._clean_code_content(markdown_code)
        has_backticks = "```" in clean_markdown
        
        print(f"✅ Markdown removed: {not has_backticks}")
        
        return not has_null_bytes and not has_backticks
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


async def test_5_syntax_validation():
    """Test 5: Verify syntax validation works"""
    print("\n" + "="*80)
    print("TEST 5: Syntax Validation")
    print("="*80)
    
    try:
        shubham = Shubham(
            project_id="test-project-123",
            user_id="test-user-456"
        )
        
        # Test valid code
        valid_code = """
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}
"""
        is_valid, errors = shubham._validate_syntax(valid_code, "test.py")
        
        print(f"✅ Valid code detected as valid: {is_valid}")
        print(f"✅ No errors: {len(errors) == 0}")
        
        # Test invalid code
        invalid_code = """
from fastapi import FastAPI

app = FastAPI(

@app.get("/")
async def root()
    return {"message": "Hello World"}
"""
        is_invalid, errors = shubham._validate_syntax(invalid_code, "test.py")
        
        print(f"✅ Invalid code detected as invalid: {not is_invalid}")
        print(f"✅ Has errors: {len(errors) > 0}")
        print(f"✅ Error message: {errors[0] if errors else 'None'}")
        
        return is_valid and not is_invalid and len(errors) > 0
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


async def test_6_tilotma_validation():
    """Test 6: Test Tilotma validation layer"""
    print("\n" + "="*80)
    print("TEST 6: Tilotma Validation")
    print("="*80)
    
    try:
        from shubham_v2_production import GeneratedFile
        
        validator = TilotmaValidator()
        
        # Create a mock generated file
        sample_code = """
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

app = FastAPI()

def get_db():
    # TODO: Implement database session
    pass

@app.get("/users")
async def get_users(db: Session = Depends(get_db)):
    # TODO: Implement query
    return {"users": []}
"""
        
        mock_file = GeneratedFile(
            file_path="app/main.py",
            content=sample_code,
            file_type=FileType.MAIN,
            tokens_used=100,
            model_used="gemini-3-pro",
            was_escalated=False,
            was_split=False,
            validation_passed=True,
            syntax_valid=True,
            cost=0.001
        )
        
        result = await validator.validate_code(mock_file, SAMPLE_ARCHITECTURE)
        
        print(f"✅ Validation completed")
        print(f"✅ Is valid: {result.is_valid}")
        print(f"✅ Logic issues: {len(result.logic_issues)}")
        print(f"✅ Suggestions: {len(result.suggestions)}")
        print(f"✅ Should regenerate: {result.should_regenerate}")
        
        if result.logic_issues:
            print(f"\n📝 Issues found:")
            for issue in result.logic_issues:
                print(f"  - {issue}")
        
        if result.suggestions:
            print(f"\n💡 Suggestions:")
            for suggestion in result.suggestions:
                print(f"  - {suggestion}")
        
        # Test passes if validation runs without error
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_7_token_limits():
    """Test 7: Verify token limits are applied correctly"""
    print("\n" + "="*80)
    print("TEST 7: Token Limit Strategy")
    print("="*80)
    
    try:
        from shubham_v2_production import TOKEN_LIMITS, FILE_COMPLEXITY
        
        print("Token limits per file type:")
        for file_type, limit in TOKEN_LIMITS.items():
            complexity = FILE_COMPLEXITY.get(file_type, "N/A")
            print(f"  {file_type.value:20} → {limit:6} tokens (complexity: {complexity})")
        
        # Verify reasonable limits
        assert TOKEN_LIMITS[FileType.MODELS] == 8192, "Models should have high limit"
        assert TOKEN_LIMITS[FileType.REQUIREMENTS] == 1000, "Requirements should have low limit"
        assert TOKEN_LIMITS[FileType.DATABASE] == 2000, "Database should have low limit"
        
        print(f"\n✅ All token limits are reasonable")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


# =============================================================================
# MAIN TEST RUNNER
# =============================================================================

async def main():
    """Run all tests"""
    
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "SHUBHAM V2 TEST SUITE" + " " * 37 + "║")
    print("║" + " " * 78 + "║")
    print("║  Testing production-ready code generation agent" + " " * 29 + "║")
    print("╚" + "═" * 78 + "╝")
    
    results = []
    
    # Run tests
    results.append(("Single File Generation", await test_1_single_file_generation()))
    results.append(("Models Generation", await test_2_models_generation()))
    results.append(("Multiple Files", await test_3_multiple_files()))
    results.append(("NULL Byte Cleaning", await test_4_null_byte_cleaning()))
    results.append(("Syntax Validation", await test_5_syntax_validation()))
    results.append(("Tilotma Validation", await test_6_tilotma_validation()))
    results.append(("Token Limits", await test_7_token_limits()))
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed ({(passed/total*100):.1f}%)")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Shubham V2 is ready for integration.")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Review errors above.")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    asyncio.run(main())
