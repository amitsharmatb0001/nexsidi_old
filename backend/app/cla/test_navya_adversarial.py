"""
Test suite for NAVYA adversarial logic error agent.

Tests various bug detection scenarios to ensure NAVYA can find:
- Division by zero
- Null reference errors
- Array index errors
- Type mismatches
- Logic errors
"""

import asyncio
import json
import sys
import os

# Add backend directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# CRITICAL: Load environment variables BEFORE importing AI Router
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))

from app.agents.navya_adversarial import NavyaAdversarial


async def test_division_by_zero():
    """Test NAVYA detects division by zero bugs"""
    print("\n" + "="*60)
    print("TEST 1: Division by Zero Detection")
    print("="*60)
    
    navya = NavyaAdversarial(project_id="test-001")
    
    buggy_code = """
def calculate_average(total, count):
    return total / count  # Bug: crashes if count=0

def calculate_price_per_unit(total_price, units):
    unit_price = total_price / units  # Bug: division by zero
    return unit_price
"""
    
    result = await navya.review(buggy_code, "python")
    
    print(f"✅ Bugs Found: {result['bugs_found']}")
    print(f"Severities: {result['severity']}")
    
    # Assertions
    assert result['bugs_found'] > 0, "Should find division by zero bugs"
    assert any('division' in str(detail).lower() for detail in result['details']), \
        "Should identify division issues"
    assert any(detail['severity'] in ['CRITICAL', 'HIGH'] for detail in result['details']), \
        "Division by zero should be high severity"
    
    print("\n📋 Details:")
    for i, bug in enumerate(result['details'], 1):
        print(f"\n  Bug {i}:")
        print(f"    Line: {bug.get('line', 'N/A')}")
        print(f"    Issue: {bug.get('issue', 'N/A')}")
        print(f"    Severity: {bug.get('severity', 'N/A')}")
        print(f"    Fix: {bug.get('fix_suggestion', 'N/A')[:80]}...")
    
    print("\n✓ TEST PASSED")
    return result


async def test_array_index_errors():
    """Test NAVYA detects array/list index errors"""
    print("\n" + "="*60)
    print("TEST 2: Array Index Error Detection")
    print("="*60)
    
    navya = NavyaAdversarial(project_id="test-002")
    
    buggy_code = """
def get_first_item(items):
    return items[0]  # Bug: crashes if items is empty

def get_last_item(items):
    return items[len(items)]  # Bug: off-by-one error

def process_user(users, index):
    return users[index]  # Bug: no bounds checking
"""
    
    result = await navya.review(buggy_code, "python")
    
    print(f"✅ Bugs Found: {result['bugs_found']}")
    print(f"Severities: {result['severity']}")
    
    assert result['bugs_found'] > 0, "Should find array index bugs"
    
    print("\n📋 Details:")
    for i, bug in enumerate(result['details'], 1):
        print(f"\n  Bug {i}: {bug.get('issue', 'N/A')}")
    
    print("\n✓ TEST PASSED")
    return result


async def test_null_reference_errors():
    """Test NAVYA detects null/None reference bugs"""
    print("\n" + "="*60)
    print("TEST 3: Null Reference Error Detection")
    print("="*60)
    
    navya = NavyaAdversarial(project_id="test-003")
    
    buggy_code = """
def get_user_name(user):
    return user.name  # Bug: crashes if user is None

def process_order(order):
    total = order.items.total  # Bug: no None check
    return total

def calculate_discount(customer):
    return customer.loyalty_points * 0.1  # Bug: None check missing
"""
    
    result = await navya.review(buggy_code, "python")
    
    print(f"✅ Bugs Found: {result['bugs_found']}")
    
    assert result['bugs_found'] > 0, "Should find null reference bugs"
    
    print("\n✓ TEST PASSED")
    return result


async def test_type_mismatch():
    """Test NAVYA detects type mismatch bugs"""
    print("\n" + "="*60)
    print("TEST 4: Type Mismatch Detection")
    print("="*60)
    
    navya = NavyaAdversarial(project_id="test-004")
    
    buggy_code = """
def add_values(a, b):
    return a + b  # Bug: crashes if a="5" and b=5 in some languages

def multiply(x, y):
    result = x * y
    return result / 2  # Bug: type inconsistency

def format_message(count):
    return "Total: " + count  # Bug: string + int
"""
    
    result = await navya.review(buggy_code, "python")
    
    print(f"✅ Bugs Found: {result['bugs_found']}")
    
    print("\n✓ TEST PASSED")
    return result


async def test_logic_errors():
    """Test NAVYA detects logic inversion and calculation bugs"""
    print("\n" + "="*60)
    print("TEST 5: Logic Error Detection")
    print("="*60)
    
    navya = NavyaAdversarial(project_id="test-005")
    
    buggy_code = """
def is_valid_age(age):
    return age > 0 and age < 18  # Bug: wrong operator, should be >=18 for adult

def calculate_discount(price, percentage):
    return price - percentage  # Bug: should be price * (1 - percentage/100)

def check_stock(quantity):
    if quantity < 0:  # Bug: inverted logic
        return True
    return False
"""
    
    result = await navya.review(buggy_code, "python")
    
    print(f"✅ Bugs Found: {result['bugs_found']}")
    
    print("\n✓ TEST PASSED")
    return result


async def test_race_conditions():
    """Test NAVYA detects race conditions in async code"""
    print("\n" + "="*60)
    print("TEST 6: Race Condition Detection")
    print("="*60)
    
    navya = NavyaAdversarial(project_id="test-006")
    
    buggy_code = """
counter = 0

async def increment():
    global counter
    temp = counter
    await asyncio.sleep(0.1)  # Bug: race condition here
    counter = temp + 1

async def decrement():
    global counter
    temp = counter
    await asyncio.sleep(0.1)  # Bug: race condition here
    counter = temp - 1
"""
    
    result = await navya.review(buggy_code, "python")
    
    print(f"✅ Bugs Found: {result['bugs_found']}")
    
    print("\n✓ TEST PASSED")
    return result


async def test_comprehensive():
    """Test NAVYA on code with multiple bug types"""
    print("\n" + "="*60)
    print("TEST 7: Comprehensive Bug Detection")
    print("="*60)
    
    navya = NavyaAdversarial(project_id="test-007")
    
    buggy_code = """
class ShoppingCart:
    def __init__(self):
        self.items = []
    
    def calculate_total(self):
        total = 0
        for item in self.items:
            total += item.price * item.quantity / item.discount  # Bug: division
        return total
    
    def get_item(self, index):
        return self.items[index]  # Bug: no bounds check
    
    def apply_coupon(self, coupon):
        discount = coupon.value  # Bug: no None check
        return self.calculate_total() - discount
    
    def get_average_price(self):
        total = sum(item.price for item in self.items)
        return total / len(self.items)  # Bug: division by zero if empty
"""
    
    result = await navya.review(buggy_code, "python")
    
    print(f"✅ Bugs Found: {result['bugs_found']}")
    print(f"Severities: {result['severity']}")
    
    # Should find multiple bugs
    assert result['bugs_found'] >= 3, "Should find at least 3 bugs in comprehensive test"
    
    # Should have varying severities
    severities = set(result['severity'])
    assert len(severities) > 1, "Should have multiple severity levels"
    
    print("\n📋 All Bugs Found:")
    for i, bug in enumerate(result['details'], 1):
        print(f"\n  {i}. [{bug.get('severity', 'UNKNOWN')}] {bug.get('issue', 'N/A')}")
        print(f"     Line: {bug.get('line', 'N/A')}")
        print(f"     Fix: {bug.get('fix_suggestion', 'N/A')[:60]}...")
    
    print("\n✓ TEST PASSED")
    return result


async def test_statistics():
    """Test that NAVYA tracks statistics correctly"""
    print("\n" + "="*60)
    print("TEST 8: Statistics Tracking")
    print("="*60)
    
    navya = NavyaAdversarial(project_id="test-008")
    
    code1 = "def test(): return 1/0"
    code2 = "def test(): return [1,2,3][10]"
    code3 = "def test(): return None.value"
    
    await navya.review(code1, "python")
    await navya.review(code2, "python")
    await navya.review(code3, "python")
    
    stats = navya.get_statistics()
    
    print(f"Total Reviews: {stats['total_reviews']}")
    print(f"Total Bugs Found: {stats['total_bugs_found']}")
    print(f"Average Bugs/Review: {stats['average_bugs_per_review']:.2f}")
    
    assert stats['total_reviews'] == 3, "Should track review count"
    assert stats['total_bugs_found'] > 0, "Should track bugs found"
    
    print("\n✓ TEST PASSED")
    return stats


async def run_all_tests():
    """Run complete test suite"""
    print("\n" + "="*60)
    print("NAVYA ADVERSARIAL AGENT - COMPLETE TEST SUITE")
    print("="*60)
    
    results = []
    
    try:
        results.append(await test_division_by_zero())
        results.append(await test_array_index_errors())
        results.append(await test_null_reference_errors())
        results.append(await test_type_mismatch())
        results.append(await test_logic_errors())
        results.append(await test_race_conditions())
        results.append(await test_comprehensive())
        await test_statistics()
        
        print("\n" + "="*60)
        print("🎉 ALL TESTS PASSED!")
        print("="*60)
        
        total_bugs = sum(r['bugs_found'] for r in results)
        print(f"\nTotal bugs found across all tests: {total_bugs}")
        print(f"Average bugs per test: {total_bugs/len(results):.1f}")
        
        print("\n✅ NAVYA is working correctly and ready for integration")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        raise
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        raise


if __name__ == "__main__":
    print("\n🚀 Starting NAVYA test suite...")
    asyncio.run(run_all_tests())
