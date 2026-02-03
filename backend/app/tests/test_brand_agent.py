"""
Test suite for BRAND AGENT design uniqueness evaluator.

Tests design evaluation across different quality levels:
- Excellent unique designs
- Generic template designs
- Mixed quality designs
- Edge cases
"""

import asyncio
import json
import sys
import os

# CRITICAL: Load env BEFORE imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))

from app.agents.brand_agent import BrandAgent


async def test_excellent_design():
    """Test BRAND AGENT recognizes excellent, unique design"""
    print("\n" + "="*60)
    print("TEST 1: Excellent Unique Design (Should PASS)")
    print("="*60)
    
    brand_agent = BrandAgent(project_id="test-brand-001")
    
    excellent_html = """
<!DOCTYPE html>
<html>
<head>
    <title>Artisan Coffee Roasters - Small Batch Excellence</title>
    <style>
        body { 
            font-family: 'Merriweather', serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #2d3748;
        }
        .hero {
            background: url('/hero-roasting.jpg');
            padding: 80px 20px;
            text-align: center;
        }
        .guarantee {
            background: #f7fafc;
            padding: 40px;
            border-left: 5px solid #667eea;
        }
    </style>
</head>
<body>
    <div class="hero">
        <h1>Artisan Coffee Roasters</h1>
        <p>Small-Batch Specialty Coffee, Roasted Fresh Daily</p>
        <p>Founded by Maria Rodriguez, Master Roaster Since 2012</p>
    </div>
    
    <section>
        <h2>Why Choose Our Coffee?</h2>
        <ul>
            <li>✓ Single-origin beans from sustainable farms we visit personally</li>
            <li>✓ Roasted within 24 hours of your order</li>
            <li>✓ Free shipping + 30-day money-back guarantee</li>
        </ul>
        
        <div class="testimonials">
            <blockquote>
                "After 15 years of searching, this is THE coffee. The Ethiopian Yirgacheffe 
                changed my morning routine forever." - James K., verified customer
            </blockquote>
        </div>
        
        <div class="guarantee">
            <h3>Our Promise</h3>
            <p>If you don't taste the difference, we'll refund 100% - no questions asked.
            Over 5,000 satisfied customers. Average rating: 4.9/5 stars.</p>
        </div>
        
        <button style="background: #667eea; color: white; padding: 20px 40px; font-size: 18px;">
            Start Your Coffee Journey - First Bag 50% Off
        </button>
    </section>
</body>
</html>
"""
    
    result = await brand_agent.evaluate(
        design_html=excellent_html,
        business_description="Small-batch artisan coffee roastery specializing in single-origin beans",
        target_audience="Coffee enthusiasts seeking premium, freshly-roasted beans"
    )
    
    print(f"✅ Overall Score: {result['overall_score']}/40")
    print(f"Instant Clarity: {result['instant_clarity']}/10")
    print(f"Uniqueness: {result['uniqueness']}/10")
    print(f"Emotional Connection: {result['emotional_connection']}/10")
    print(f"Value Proposition: {result['value_proposition']}/10")
    print(f"Passed: {'✓ YES' if result['passed'] else '✗ NO'}")
    
    assert result['passed'], "Excellent design should pass"
    assert result['overall_score'] >= 35, "Score should be at least 35/40"
    
    print(f"\n📋 Feedback: {result['feedback']}")
    
    print("\n✓ TEST PASSED")
    return result


async def test_generic_template():
    """Test BRAND AGENT catches generic template design"""
    print("\n" + "="*60)
    print("TEST 2: Generic Template Design (Should FAIL)")
    print("="*60)
    
    brand_agent = BrandAgent(project_id="test-brand-002")
    
    generic_html = """
<!DOCTYPE html>
<html>
<head>
    <title>Business Name</title>
</head>
<body>
    <header>
        <h1>Welcome to Our Business</h1>
        <p>We provide quality services</p>
    </header>
    
    <section>
        <h2>About Us</h2>
        <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit.</p>
        
        <h2>Our Services</h2>
        <ul>
            <li>Service 1</li>
            <li>Service 2</li>
            <li>Service 3</li>
        </ul>
        
        <button>Contact Us</button>
    </section>
    
    <footer>
        <p>© 2024 Business Name. All rights reserved.</p>
    </footer>
</body>
</html>
"""
    
    result = await brand_agent.evaluate(
        design_html=generic_html,
        business_description="General business services",
        target_audience="General public"
    )
    
    print(f"✅ Overall Score: {result['overall_score']}/40")
    print(f"Passed: {'✓ YES' if result['passed'] else '✗ NO (Expected)'}")
    
    # Generic template should FAIL
    assert not result['passed'], "Generic template should fail"
    assert result['overall_score'] < 35, "Score should be below 35/40"
    
    print(f"\n📋 Feedback: {result['feedback']}")
    if result.get('improvements'):
        print("\n🔧 Improvements Suggested:")
        for improvement in result['improvements'][:3]:
            print(f"  - {improvement}")
    
    print("\n✓ TEST PASSED (Design correctly failed)")
    return result


async def test_borderline_design():
    """Test BRAND AGENT on borderline quality design"""
    print("\n" + "="*60)
    print("TEST 3: Borderline Quality Design")
    print("="*60)
    
    brand_agent = BrandAgent(project_id="test-brand-003")
    
    borderline_html = """
<!DOCTYPE html>
<html>
<head>
    <title>Downtown Dental Care</title>
</head>
<body>
    <header>
        <h1>Downtown Dental Care</h1>
        <p>Your Family Dentist in Austin</p>
    </header>
    
    <section>
        <h2>Comprehensive Dental Services</h2>
        <p>We offer general dentistry, cosmetic procedures, and emergency care.</p>
        
        <ul>
            <li>Same-day appointments available</li>
            <li>Accepting new patients</li>
            <li>Insurance accepted</li>
        </ul>
        
        <button>Book Appointment</button>
    </section>
</body>
</html>
"""
    
    result = await brand_agent.evaluate(
        design_html=borderline_html,
        business_description="Family dental practice in downtown Austin",
        target_audience="Families looking for a dentist"
    )
    
    print(f"✅ Overall Score: {result['overall_score']}/40")
    print(f"Passed: {'✓ YES' if result['passed'] else '✗ NO'}")
    
    # Borderline design could go either way
    print(f"\n📊 Score Breakdown:")
    if result.get('breakdown'):
        for criterion, details in result['breakdown'].items():
            print(f"  {criterion}: {details['score']}/10")
    
    print("\n✓ TEST PASSED")
    return result


async def test_strong_value_prop():
    """Test BRAND AGENT recognizes strong value proposition"""
    print("\n" + "="*60)
    print("TEST 4: Strong Value Proposition")
    print("="*60)
    
    brand_agent = BrandAgent(project_id="test-brand-004")
    
    strong_value_html = """
<!DOCTYPE html>
<html>
<head>
    <title>QuickBooks Integration in 24 Hours - Guaranteed</title>
</head>
<body>
    <header>
        <h1>QuickBooks Integration Specialists</h1>
        <p>24-Hour Setup Guarantee or Your Money Back</p>
    </header>
    
    <section>
        <h2>Why We're Different</h2>
        <ul>
            <li>✓ Setup completed in 24 hours (competitors take 2-4 weeks)</li>
            <li>✓ Fixed price: $1,999 (no hourly billing surprises)</li>
            <li>✓ Free training for your entire team</li>
            <li>✓ 90-day post-setup support included</li>
        </ul>
        
        <div class="proof">
            <h3>Track Record</h3>
            <p>847 successful integrations | 98.2% on-time delivery rate</p>
            <p>"Saved us $50K vs hiring a consultant" - CFO, TechCorp</p>
        </div>
        
        <button>Get Started Today - 24 Hour Guarantee</button>
    </section>
</body>
</html>
"""
    
    result = await brand_agent.evaluate(
        design_html=strong_value_html,
        business_description="QuickBooks integration service for businesses",
        target_audience="Small business owners and CFOs"
    )
    
    print(f"✅ Overall Score: {result['overall_score']}/40")
    print(f"Value Proposition Score: {result['value_proposition']}/10")
    
    # Should score high on value proposition
    assert result['value_proposition'] >= 8, "Strong value prop should score 8+/10"
    
    print("\n✓ TEST PASSED")
    return result


async def test_emotional_connection():
    """Test BRAND AGENT recognizes emotional connection"""
    print("\n" + "="*60)
    print("TEST 5: Emotional Connection & Trust")
    print("="*60)
    
    brand_agent = BrandAgent(project_id="test-brand-005")
    
    emotional_html = """
<!DOCTYPE html>
<html>
<head>
    <title>Sunrise Senior Care - Like Family</title>
</head>
<body>
    <header>
        <h1>Sunrise Senior Care</h1>
        <p>Founded by Sarah Johnson after caring for her mother with Alzheimer's</p>
    </header>
    
    <section>
        <h2>We Understand What You're Going Through</h2>
        <p>When my mom was diagnosed in 2015, I couldn't find care that treated her 
        with dignity and respect. So I started Sunrise - a place where I'd be 
        comfortable having my own mom.</p>
        
        <div class="testimonials">
            <blockquote>
                "Sarah and her team treated my father like family. They remembered 
                his stories, celebrated his birthday, and held my hand through the 
                hard days. I'll forever be grateful."
                <br>- Patricia R., daughter of resident
            </blockquote>
        </div>
        
        <ul>
            <li>✓ 24/7 licensed nursing staff (not just aides)</li>
            <li>✓ Memory care specialists on-site</li>
            <li>✓ Small community (max 16 residents) for personal attention</li>
            <li>✓ All meals prepared fresh by in-house chef</li>
        </ul>
        
        <p><strong>Schedule a visit. Stay for lunch. Meet our family.</strong></p>
        <button>Schedule Your Visit</button>
    </section>
</body>
</html>
"""
    
    result = await brand_agent.evaluate(
        design_html=emotional_html,
        business_description="Senior care facility specializing in Alzheimer's and dementia care",
        target_audience="Adult children looking for senior care for parents"
    )
    
    print(f"✅ Overall Score: {result['overall_score']}/40")
    print(f"Emotional Connection Score: {result['emotional_connection']}/10")
    
    # Should score high on emotional connection
    assert result['emotional_connection'] >= 8, "Strong emotional connection should score 8+/10"
    
    print("\n✓ TEST PASSED")
    return result


async def test_statistics():
    """Test that BRAND AGENT tracks statistics correctly"""
    print("\n" + "="*60)
    print("TEST 6: Statistics Tracking")
    print("="*60)
    
    brand_agent = BrandAgent(project_id="test-brand-006")
    
    # Run multiple evaluations
    html1 = "<html><body><h1>Test 1</h1></body></html>"
    html2 = "<html><body><h1>Test 2</h1></body></html>"
    html3 = "<html><body><h1>Test 3</h1></body></html>"
    
    await brand_agent.evaluate(html1, "Test business 1")
    await brand_agent.evaluate(html2, "Test business 2")
    await brand_agent.evaluate(html3, "Test business 3")
    
    stats = brand_agent.get_statistics()
    
    print(f"Total Evaluations: {stats['total_evaluations']}")
    print(f"Passed: {stats['total_passed']}")
    print(f"Failed: {stats['total_failed']}")
    print(f"Pass Rate: {stats['pass_rate']:.1f}%")
    print(f"Average Score: {stats['average_score']:.1f}/40")
    
    assert stats['total_evaluations'] == 3, "Should track evaluation count"
    
    print("\n✓ TEST PASSED")
    return stats


async def run_all_tests():
    """Run complete test suite"""
    print("\n" + "="*60)
    print("BRAND AGENT - COMPLETE TEST SUITE")
    print("="*60)
    
    results = []
    
    try:
        results.append(await test_excellent_design())
        results.append(await test_generic_template())
        results.append(await test_borderline_design())
        results.append(await test_strong_value_prop())
        results.append(await test_emotional_connection())
        await test_statistics()
        
        print("\n" + "="*60)
        print("🎉 ALL TESTS PASSED!")
        print("="*60)
        
        # Calculate overall statistics
        excellent_count = sum(1 for r in results if r['overall_score'] >= 35)
        average_score = sum(r['overall_score'] for r in results) / len(results)
        
        print(f"\nDesigns evaluated: {len(results)}")
        print(f"Designs passing (≥35/40): {excellent_count}")
        print(f"Average score: {average_score:.1f}/40")
        
        print("\n✅ BRAND AGENT is working correctly and ready for integration")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        raise
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        raise


if __name__ == "__main__":
    print("\n🎨 Starting BRAND AGENT test suite...")
    asyncio.run(run_all_tests())
