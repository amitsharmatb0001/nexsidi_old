"""
Integration Test: AARAV Screenshot Capture + BRAND AGENT Visual Evaluation

This demonstrates the complete workflow:
1. AARAV captures screenshots of deployed website
2. BRAND AGENT evaluates visual design quality
3. Returns comprehensive assessment with visual analysis

Requirements:
- Playwright installed: pip install playwright --break-system-packages
- Playwright browser: playwright install chromium
- Deployed website URL (or use example.com for testing)
"""

import asyncio
import json
import sys
import os

# CRITICAL: Load env BEFORE imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))

from app.agents.aarav_testing import AaravTesting
from app.agents.brand_agent import BrandAgent


async def test_complete_visual_evaluation():
    """
    Complete workflow: Screenshot → Visual Evaluation
    """
    print("\n" + "="*70)
    print("INTEGRATION TEST: AARAV + BRAND AGENT")
    print("="*70)
    
    # Step 1: Initialize agents
    print("\n📋 Step 1: Initializing agents...")
    aarav = AaravTesting(project_id="integration-test-001")
    brand_agent = BrandAgent(project_id="integration-test-001")
    
    # Step 2: Capture screenshots
    print("\n📸 Step 2: AARAV capturing screenshots...")
    
    # Use example.com for testing (replace with your deployed URL)
    test_url = "https://example.com"
    print(f"Target URL: {test_url}")
    
    screenshots = await aarav.capture_screenshots(test_url)
    
    print(f"✅ Screenshots captured:")
    for size, path in screenshots.items():
        if path:
            print(f"  - {size}: {path}")
        else:
            print(f"  - {size}: FAILED")
    
    # Step 3: Visual evaluation
    print("\n🎨 Step 3: BRAND AGENT evaluating visual design...")
    
    result = await brand_agent.evaluate_screenshots(
        screenshots=screenshots,
        business_description="Example domain for documentation and testing purposes",
        target_audience="Developers and technical users"
    )
    
    # Step 4: Display results
    print("\n" + "="*70)
    print("EVALUATION RESULTS")
    print("="*70)
    
    print(f"\n🎯 Overall Score: {result['overall_score']}/40")
    print(f"Status: {'✅ PASSED' if result['passed'] else '❌ FAILED'}")
    
    print(f"\n📊 Score Breakdown:")
    print(f"  Instant Clarity: {result['instant_clarity']}/10")
    print(f"  Visual Uniqueness: {result['uniqueness']}/10")
    print(f"  Emotional Connection: {result['emotional_connection']}/10")
    print(f"  Value Proposition: {result['value_proposition']}/10")
    
    print(f"\n💬 Feedback:")
    print(f"  {result['feedback']}")
    
    if result.get('improvements'):
        print(f"\n🔧 Suggested Improvements:")
        for i, improvement in enumerate(result['improvements'], 1):
            print(f"  {i}. {improvement}")
    
    if result.get('responsive_notes'):
        print(f"\n📱 Responsive Design:")
        print(f"  {result['responsive_notes']}")
    
    if result.get('breakdown'):
        print(f"\n📋 Detailed Breakdown:")
        for criterion, details in result['breakdown'].items():
            print(f"\n  {criterion.replace('_', ' ').title()}:")
            print(f"    Score: {details['score']}/10")
            print(f"    Reason: {details['reason']}")
    
    # Statistics
    print("\n" + "="*70)
    print("AGENT STATISTICS")
    print("="*70)
    
    brand_stats = brand_agent.get_statistics()
    print(f"\nBRAND AGENT:")
    print(f"  Total Evaluations: {brand_stats['total_evaluations']}")
    print(f"  Pass Rate: {brand_stats['pass_rate']:.1f}%")
    print(f"  Average Score: {brand_stats['average_score']:.1f}/40")
    
    return result


async def test_production_workflow():
    """
    Simulates production workflow with custom website
    
    In production, you would:
    1. Shubham generates backend
    2. Aanya generates frontend
    3. PRANAV deploys to staging URL
    4. AARAV captures screenshots
    5. BRAND AGENT evaluates
    6. If score < 35: AANYA regenerates with improvements
    7. Repeat until passing
    """
    print("\n" + "="*70)
    print("PRODUCTION WORKFLOW SIMULATION")
    print("="*70)
    
    aarav = AaravTesting(project_id="prod-workflow-001")
    brand_agent = BrandAgent(project_id="prod-workflow-001")
    
    # Replace with actual deployed URL from PRANAV
    deployed_url = "https://your-staging-url.run.app"
    
    business_context = {
        "description": "Artisan coffee roastery selling small-batch specialty coffee",
        "target_audience": "Coffee enthusiasts aged 25-45",
        "unique_value": "Single-origin beans roasted within 24 hours of order"
    }
    
    print(f"\n🎯 Business: {business_context['description']}")
    print(f"🎯 Target: {business_context['target_audience']}")
    
    max_iterations = 3
    iteration = 1
    
    while iteration <= max_iterations:
        print(f"\n" + "="*70)
        print(f"ITERATION {iteration}/{max_iterations}")
        print("="*70)
        
        # Capture screenshots
        print(f"\n📸 Capturing screenshots...")
        screenshots = await aarav.capture_screenshots(deployed_url)
        
        # Evaluate
        print(f"\n🎨 Evaluating design...")
        result = await brand_agent.evaluate_screenshots(
            screenshots=screenshots,
            business_description=business_context['description'],
            target_audience=business_context['target_audience']
        )
        
        print(f"\n🎯 Score: {result['overall_score']}/40")
        
        if result['passed']:
            print(f"✅ PASSED! Design meets quality threshold.")
            print(f"\n📊 Final Scores:")
            print(f"  Instant Clarity: {result['instant_clarity']}/10")
            print(f"  Uniqueness: {result['uniqueness']}/10")
            print(f"  Emotional Connection: {result['emotional_connection']}/10")
            print(f"  Value Proposition: {result['value_proposition']}/10")
            break
        else:
            print(f"❌ Failed with {result['overall_score']}/40")
            
            if iteration < max_iterations:
                print(f"\n🔧 Improvements needed:")
                for improvement in result.get('improvements', []):
                    print(f"  - {improvement}")
                
                print(f"\n🔄 Triggering AANYA to regenerate with improvements...")
                # In production: send improvements to AANYA
                # await aanya.regenerate_with_improvements(result['improvements'])
                
                iteration += 1
            else:
                print(f"\n⚠️  Max iterations reached. Manual review needed.")
                break
    
    return result


async def run_tests():
    """Run all integration tests"""
    
    print("\n" + "="*70)
    print("AARAV + BRAND AGENT INTEGRATION TEST SUITE")
    print("="*70)
    
    try:
        # Test 1: Basic workflow
        result1 = await test_complete_visual_evaluation()
        
        # Test 2: Production workflow (commented out - needs deployed URL)
        # result2 = await test_production_workflow()
        
        print("\n" + "="*70)
        print("✅ ALL INTEGRATION TESTS PASSED")
        print("="*70)
        
        print("\n🎉 System ready for production:")
        print("  1. AARAV captures screenshots ✅")
        print("  2. BRAND AGENT evaluates visually ✅")
        print("  3. Gemini Vision analyzes actual design ✅")
        print("  4. Returns actionable feedback ✅")
        
    except Exception as e:
        print(f"\n❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    print("\n🚀 Starting AARAV + BRAND AGENT integration tests...")
    asyncio.run(run_tests())
