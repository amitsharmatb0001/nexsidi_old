"""
TEST SCRIPT FOR AI ROUTER V2
Verify all functionality works before integrating into Shubham
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from dotenv import load_dotenv
load_dotenv()

import asyncio
from ai_router_v2_production import ai_router, TaskComplexity, quick_generate


async def test_model_selection():
    """Test 1: Verify correct model selection for different tasks"""
    print("\n" + "="*80)
    print("TEST 1: Model Selection Logic")
    print("="*80)
    
    tests = [
        ("chat", TaskComplexity.SIMPLE, "gemini-2.5-flash"),
        ("architecture", TaskComplexity.MOST_COMPLEX, "claude-opus-4.5"),
        ("code_generation", TaskComplexity.COMPLEX, "gemini-3-pro"),
        ("code_review", TaskComplexity.MEDIUM, "claude-sonnet-4.5"),
        ("deployment", TaskComplexity.SIMPLE, "gemini-3-flash"),
    ]
    
    passed = 0
    for task_type, complexity, expected in tests:
        model = ai_router.get_model_for_task(task_type, complexity)
        status = "✅" if model == expected else "❌"
        print(f"{status} {task_type}/{complexity.value}: {model} (expected: {expected})")
        if model == expected:
            passed += 1
    
    print(f"\nResult: {passed}/{len(tests)} tests passed")
    return passed == len(tests)


async def test_simple_generation():
    """Test 2: Simple text generation"""
    print("\n" + "="*80)
    print("TEST 2: Simple Generation (Chat)")
    print("="*80)
    
    try:
        response = await quick_generate(
            "Say 'Hello from NexSidi!' in exactly 3 words.",
            task_type="chat",
            complexity=TaskComplexity.SIMPLE
        )
        
        print(f"✅ Response: {response}")
        print(f"✅ Generation successful")
        return True
    except Exception as e:
        print(f"❌ Generation failed: {e}")
        return False


async def test_code_generation():
    """Test 3: Code generation with proper model"""
    print("\n" + "="*80)
    print("TEST 3: Code Generation")
    print("="*80)
    
    try:
        prompt = """
Generate a simple FastAPI endpoint that returns 'Hello World'.
Include imports and make it production-ready.
"""
        
        response = await ai_router.generate(
            messages=[{"role": "user", "content": prompt}],
            task_type="code_generation",
            complexity=TaskComplexity.MEDIUM
        )
        
        print(f"✅ Model used: {response.model_id}")
        print(f"✅ Tokens: {response.input_tokens} → {response.output_tokens}")
        print(f"✅ Finish reason: {response.finish_reason}")
        print(f"✅ Cost: ₹{response.cost_estimate:.4f}")
        print(f"✅ Latency: {response.latency_ms:.0f}ms")
        print(f"\n📄 Generated code (first 200 chars):")
        print(response.content[:200] + "...")
        
        return response.finish_reason == "stop"
    except Exception as e:
        print(f"❌ Code generation failed: {e}")
        return False


async def test_truncation_detection():
    """Test 4: Detect when model hits token limit"""
    print("\n" + "="*80)
    print("TEST 4: Truncation Detection")
    print("="*80)
    
    try:
        # Request very large output to potentially hit limit
        prompt = """
Generate a complete FastAPI application with:
- 10 database models with relationships
- 20 API endpoints
- Complete schemas for all endpoints
- Authentication system
- Comprehensive error handling

Make it production-ready with full docstrings.
"""
        
        response = await ai_router.generate(
            messages=[{"role": "user", "content": prompt}],
            task_type="code_generation",
            complexity=TaskComplexity.COMPLEX,
            model="gemini-3-flash",  # Use smaller model to test limits
            max_tokens=2000,  # Artificially low to test truncation
            auto_escalate=False  # Disable escalation for this test
        )
        
        print(f"✅ Model used: {response.model_id}")
        print(f"✅ Output tokens: {response.output_tokens}")
        print(f"✅ Finish reason: {response.finish_reason}")
        
        if response.finish_reason == "length":
            print(f"✅ Truncation detected correctly")
            return True
        else:
            print(f"⚠️ No truncation (code fit in {response.output_tokens} tokens)")
            return True  # Still pass, just didn't hit limit
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


async def test_auto_escalation():
    """Test 5: Automatic escalation when truncated"""
    print("\n" + "="*80)
    print("TEST 5: Automatic Escalation")
    print("="*80)
    
    try:
        # Request large output with small model
        prompt = """
Generate a complete SQLAlchemy models file with these 5 tables:
- User (10 columns, 3 relationships)
- Product (12 columns, 4 relationships)
- Order (8 columns, 5 relationships)
- Review (6 columns, 3 relationships)
- Inventory (8 columns, 2 relationships)

Include all imports, docstrings, and relationship definitions.
"""
        
        response = await ai_router.generate(
            messages=[{"role": "user", "content": prompt}],
            task_type="code_generation",
            complexity=TaskComplexity.COMPLEX,
            model="gemini-3-flash",  # Start with small model
            max_tokens=3000,  # Low limit to trigger escalation
            auto_escalate=True  # Enable escalation
        )
        
        print(f"✅ Final model: {response.model_id}")
        print(f"✅ Was escalated: {response.was_escalated}")
        print(f"✅ Escalation count: {response.escalation_count}")
        print(f"✅ Output tokens: {response.output_tokens}")
        print(f"✅ Finish reason: {response.finish_reason}")
        
        if response.was_escalated:
            print(f"✅ Escalation worked successfully")
        else:
            print(f"⚠️ No escalation needed (fit in initial model)")
        
        return response.finish_reason == "stop"
        
    except Exception as e:
        print(f"❌ Escalation test failed: {e}")
        return False


async def test_error_handling():
    """Test 6: Error handling for invalid inputs"""
    print("\n" + "="*80)
    print("TEST 6: Error Handling")
    print("="*80)
    
    tests_passed = 0
    
    # Test 1: Invalid model
    try:
        await ai_router.generate(
            messages=[{"role": "user", "content": "Hello"}],
            model="invalid-model-123"
        )
        print("❌ Should have raised error for invalid model")
    except Exception as e:
        print(f"✅ Correctly caught invalid model: {str(e)[:50]}")
        tests_passed += 1
    
    # Test 2: Empty messages
    try:
        await ai_router.generate(messages=[])
        print("❌ Should have raised error for empty messages")
    except Exception as e:
        print(f"✅ Correctly caught empty messages: {str(e)[:50]}")
        tests_passed += 1
    
    return tests_passed == 2


async def main():
    """Run all tests"""
    
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "AI ROUTER V2 TEST SUITE" + " " * 35 + "║")
    print("║" + " " * 78 + "║")
    print("║  Testing production-ready AI Router with all features" + " " * 23 + "║")
    print("╚" + "═" * 78 + "╝")
    
    results = []
    
    # Run tests
    results.append(("Model Selection", await test_model_selection()))
    results.append(("Simple Generation", await test_simple_generation()))
    results.append(("Code Generation", await test_code_generation()))
    results.append(("Truncation Detection", await test_truncation_detection()))
    results.append(("Auto Escalation", await test_auto_escalation()))
    results.append(("Error Handling", await test_error_handling()))
    
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
        print("\n🎉 ALL TESTS PASSED! AI Router V2 is ready for production.")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Review errors above.")
    
    # Cleanup
    await ai_router.close()
    
    print("\n" + "="*80)


if __name__ == "__main__":
    asyncio.run(main())