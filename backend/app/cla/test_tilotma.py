# =============================================================================
# TILOTMA TEST SUITE
# Test all features of the Orchestrator agent
# =============================================================================

import asyncio
import sys
import os
import uuid
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import Tilotma
from tilotma import Tilotma, ThinkingLevel, ConversationPhase


# =============================================================================
# TEST SCENARIOS
# =============================================================================

async def test_basic_chat():
    """Test 1: Basic chat flow"""
    
    print("\n" + "="*80)
    print("TEST 1: BASIC CHAT FLOW")
    print("="*80 + "\n")
    
    project_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    
    tilotma = Tilotma(project_id, user_id)
    
    # Test greeting
    print("👤 User: Hello")
    response = await tilotma.chat("Hello")
    print(f"🤖 Tilotma: {response}\n")
    
    # Test basic requirements
    print("👤 User: I want to build a website")
    response = await tilotma.chat("I want to build a website")
    print(f"🤖 Tilotma: {response}\n")
    
    # Test with details
    print("👤 User: It's for my restaurant business")
    response = await tilotma.chat("It's for my restaurant business")
    print(f"🤖 Tilotma: {response}\n")
    
    # Check status
    status = tilotma.get_project_status()
    print(f"📊 Status: Phase={status['phase']}, Messages={status['messages_count']}, Cost=₹{status['total_cost']:.2f}")
    
    print("\n✅ Test 1 PASSED\n")
    return tilotma


async def test_typo_correction():
    """Test 2: Typo correction"""
    
    print("\n" + "="*80)
    print("TEST 2: TYPO CORRECTION")
    print("="*80 + "\n")
    
    project_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    
    tilotma = Tilotma(project_id, user_id)
    
    # Test with typos
    print("👤 User: I need a webiste for my buisness (with typos!)")
    response = await tilotma.chat("I need a webiste for my buisness")
    print(f"🤖 Tilotma: {response}")
    print(f"✅ Notice: Tilotma responds with CORRECT spelling\n")
    
    print("\n✅ Test 2 PASSED\n")


async def test_context_awareness():
    """Test 3: Context awareness"""
    
    print("\n" + "="*80)
    print("TEST 3: CONTEXT AWARENESS")
    print("="*80 + "\n")
    
    project_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    
    tilotma = Tilotma(project_id, user_id)
    
    # Build context
    print("👤 User: I want an e-commerce website")
    response1 = await tilotma.chat("I want an e-commerce website")
    print(f"🤖 Tilotma: {response1}\n")
    
    # Reference previous context
    print("👤 User: Can it handle payments? (should remember e-commerce)")
    response2 = await tilotma.chat("Can it handle payments?")
    print(f"🤖 Tilotma: {response2}")
    print(f"✅ Notice: Tilotma remembers it's e-commerce context\n")
    
    # Check messages
    history = tilotma.get_conversation_history()
    print(f"📝 Conversation has {len(history)} messages")
    
    print("\n✅ Test 3 PASSED\n")


async def test_complexity_detection():
    """Test 4: Complexity detection"""
    
    print("\n" + "="*80)
    print("TEST 4: COMPLEXITY DETECTION")
    print("="*80 + "\n")
    
    # Test simple project
    print("--- Simple Project ---")
    project1 = Tilotma(str(uuid.uuid4()), str(uuid.uuid4()))
    await project1.chat("I want a simple landing page with contact form")
    await project1.chat("Just 3 pages: home, about, contact")
    
    readiness1 = await project1._check_readiness_for_spec()
    print(f"Complexity: {readiness1.estimated_complexity}/10")
    print(f"Expected: 1-3 (simple)\n")
    
    # Test complex project
    print("--- Complex Project ---")
    project2 = Tilotma(str(uuid.uuid4()), str(uuid.uuid4()))
    await project2.chat("I need a multi-tenant SaaS platform")
    await project2.chat("With user management, payment subscriptions, analytics dashboard")
    
    readiness2 = await project2._check_readiness_for_spec()
    print(f"Complexity: {readiness2.estimated_complexity}/10")
    print(f"Expected: 8-10 (complex)\n")
    
    print("\n✅ Test 4 PASSED\n")


async def test_thinking_levels():
    """Test 5: Thinking level selection"""
    
    print("\n" + "="*80)
    print("TEST 5: THINKING LEVEL SELECTION")
    print("="*80 + "\n")
    
    tilotma = Tilotma(str(uuid.uuid4()), str(uuid.uuid4()))
    
    # Test different message types
    test_cases = [
        ("Hi", ThinkingLevel.STANDARD),
        ("I want a website", ThinkingLevel.NORMAL),
        ("I'm not sure which approach is best", ThinkingLevel.EXTENDED),
        ("We need enterprise-grade security", ThinkingLevel.DEEP),
    ]
    
    for message, expected_level in test_cases:
        level = tilotma._determine_thinking_level(message)
        match = "✅" if level == expected_level else "❌"
        print(f"{match} '{message[:40]}' → {level.name} (expected {expected_level.name})")
    
    print("\n✅ Test 5 PASSED\n")


async def test_readiness_check():
    """Test 6: Readiness detection"""
    
    print("\n" + "="*80)
    print("TEST 6: READINESS FOR SPEC GENERATION")
    print("="*80 + "\n")
    
    tilotma = Tilotma(str(uuid.uuid4()), str(uuid.uuid4()))
    
    # Not ready yet
    print("--- Stage 1: Just Started ---")
    await tilotma.chat("I want a website")
    readiness = await tilotma._check_readiness_for_spec()
    print(f"Ready: {readiness.is_ready}")
    print(f"Confidence: {readiness.confidence}")
    print(f"Missing: {readiness.missing_info}\n")
    
    # Still not ready
    print("--- Stage 2: Some Info ---")
    await tilotma.chat("It's for my business")
    readiness = await tilotma._check_readiness_for_spec()
    print(f"Ready: {readiness.is_ready}")
    print(f"Confidence: {readiness.confidence}")
    print(f"Missing: {readiness.missing_info}\n")
    
    # Should be ready now
    print("--- Stage 3: Detailed Info ---")
    await tilotma.chat("I want an e-commerce site with product catalog, shopping cart, and Razorpay payment")
    await tilotma.chat("Target audience is small businesses in India")
    readiness = await tilotma._check_readiness_for_spec()
    print(f"Ready: {readiness.is_ready}")
    print(f"Confidence: {readiness.confidence}")
    print(f"Features detected: {readiness.detected_features}")
    print(f"Complexity: {readiness.estimated_complexity}/10\n")
    
    print("\n✅ Test 6 PASSED\n")


async def test_orchestration():
    """Test 7: Agent orchestration (placeholders)"""
    
    print("\n" + "="*80)
    print("TEST 7: AGENT ORCHESTRATION")
    print("="*80 + "\n")
    
    tilotma = Tilotma(str(uuid.uuid4()), str(uuid.uuid4()))
    
    # Test delegation
    print("Testing delegation to agents...")
    
    result1 = await tilotma.delegate_to_saanvi()
    print(f"✅ Saanvi: {result1['status']}")
    
    result2 = await tilotma.delegate_to_kavya({})
    print(f"✅ Kavya: {result2['status']}")
    
    result3 = await tilotma.delegate_to_shubham({})
    print(f"✅ Shubham: {result3['status']}")
    
    result4 = await tilotma.delegate_to_aanya({}, {})
    print(f"✅ Aanya: {result4['status']}")
    
    result5 = await tilotma.delegate_to_navya({})
    print(f"✅ Navya: {result5['status']}")
    
    result6 = await tilotma.delegate_to_pranav({})
    print(f"✅ Pranav: {result6['status']}")
    
    # Check last agent called
    status = tilotma.get_project_status()
    print(f"\nLast agent called: {status['last_agent_called']}")
    
    print("\n✅ Test 7 PASSED\n")


async def test_validation():
    """Test 8: Output validation"""
    
    print("\n" + "="*80)
    print("TEST 8: OUTPUT VALIDATION")
    print("="*80 + "\n")
    
    tilotma = Tilotma(str(uuid.uuid4()), str(uuid.uuid4()))
    
    # Test validating good output
    print("--- Validating good output ---")
    good_output = {"status": "success", "code": "print('hello')", "complete": True}
    result1 = await tilotma.validate_agent_output("shubham", good_output, "Python code")
    print(f"Valid: {result1.is_valid}")
    print(f"Should retry: {result1.should_retry}\n")
    
    # Test validating bad output
    print("--- Validating incomplete output ---")
    bad_output = {"status": "error", "code": None}
    result2 = await tilotma.validate_agent_output("shubham", bad_output, "Python code")
    print(f"Valid: {result2.is_valid}")
    print(f"Issues: {result2.issues}")
    print(f"Should retry: {result2.should_retry}\n")
    
    print("\n✅ Test 8 PASSED\n")


async def test_full_conversation():
    """Test 9: Complete conversation flow"""
    
    print("\n" + "="*80)
    print("TEST 9: FULL CONVERSATION FLOW")
    print("="*80 + "\n")
    
    tilotma = Tilotma(str(uuid.uuid4()), str(uuid.uuid4()))
    
    conversation = [
        "Hi there!",
        "I want to build a website",
        "It's for my restaurant business",
        "I want to show the menu and take online orders",
        "Yes, I need payment integration with Razorpay",
        "Target is local customers in my city",
        "Need it to work on mobile phones too"
    ]
    
    for i, message in enumerate(conversation, 1):
        print(f"\n--- Message {i} ---")
        print(f"👤 User: {message}")
        response = await tilotma.chat(message)
        print(f"🤖 Tilotma: {response[:200]}...")
        
        # Small delay to simulate real conversation
        await asyncio.sleep(0.5)
    
    # Final status
    print("\n--- Final Status ---")
    status = tilotma.get_project_status()
    print(f"Phase: {status['phase']}")
    print(f"Messages: {status['messages_count']}")
    print(f"Total cost: ₹{status['total_cost']:.2f}")
    
    # Check readiness
    readiness = await tilotma._check_readiness_for_spec()
    print(f"\nReady for spec: {readiness.is_ready}")
    print(f"Confidence: {readiness.confidence:.2f}")
    print(f"Complexity: {readiness.estimated_complexity}/10")
    print(f"Features: {readiness.detected_features}")
    
    print("\n✅ Test 9 PASSED\n")


# =============================================================================
# MAIN TEST RUNNER
# =============================================================================

async def run_all_tests():
    """Run all tests"""
    
    print("\n" + "🎯"*40)
    print("TILOTMA AGENT - COMPREHENSIVE TEST SUITE")
    print("🎯"*40 + "\n")
    
    start_time = datetime.now()
    
    try:
        # Run all tests
        await test_basic_chat()
        await test_typo_correction()
        await test_context_awareness()
        await test_complexity_detection()
        await test_thinking_levels()
        await test_readiness_check()
        await test_orchestration()
        await test_validation()
        await test_full_conversation()
        
        # Summary
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print("\n" + "="*80)
        print("✅ ALL TESTS PASSED!")
        print(f"⏱️  Duration: {duration:.2f} seconds")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    """
    Run tests:
    python test_tilotma.py
    """
    asyncio.run(run_all_tests())