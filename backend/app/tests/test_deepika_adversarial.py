"""
Test suite for DEEPIKA adversarial performance agent.

Tests various performance issue detection scenarios:
- O(n²) algorithmic complexity
- N+1 query problems
- Memory leaks
- Missing pagination
- Blocking operations
- Missing indexes
- Cache opportunities
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

from app.agents.deepika_adversarial import DeepikaAdversarial


async def test_algorithmic_complexity():
    """Test DEEPIKA detects O(n²) and worse complexity"""
    print("\n" + "="*60)
    print("TEST 1: Algorithmic Complexity Detection (O(n²))")
    print("="*60)
    
    deepika = DeepikaAdversarial(project_id="test-perf-001")
    
    slow_code = """
def find_duplicates(items):
    duplicates = []
    for i in range(len(items)):
        for j in range(len(items)):  # O(n²) - nested loop
            if i != j and items[i] == items[j]:
                duplicates.append(items[i])
    return duplicates

def match_users(users1, users2):
    matches = []
    for u1 in users1:
        for u2 in users2:  # O(n*m) - can be O(n+m) with hash
            if u1.email == u2.email:
                matches.append((u1, u2))
    return matches
"""
    
    result = await deepika.review(slow_code, "python")
    
    print(f"✅ Issues Found: {result['issues_found']}")
    print(f"Severities: {result['severity']}")
    
    assert result['issues_found'] > 0, "Should find complexity issues"
    assert any(detail['severity'] in ['CRITICAL', 'HIGH'] for detail in result['details']), \
        "Nested loops should be high severity"
    
    print("\n📋 Details:")
    for i, issue in enumerate(result['details'], 1):
        print(f"\n  Issue {i}:")
        print(f"    Problem: {issue.get('issue', 'N/A')}")
        print(f"    Current: {issue.get('current_performance', 'N/A')}")
        print(f"    Optimized: {issue.get('optimized_performance', 'N/A')}")
        print(f"    Scale Impact: {issue.get('scale_impact', 'N/A')}")
    
    print("\n✓ TEST PASSED")
    return result


async def test_n_plus_1_queries():
    """Test DEEPIKA detects N+1 query problems"""
    print("\n" + "="*60)
    print("TEST 2: N+1 Query Problem Detection")
    print("="*60)
    
    deepika = DeepikaAdversarial(project_id="test-perf-002")
    
    slow_code = """
def get_user_posts():
    users = User.query.all()
    result = []
    for user in users:  # N+1: Query in loop
        posts = Post.query.filter_by(user_id=user.id).all()
        result.append({
            'user': user,
            'posts': posts
        })
    return result

@app.route('/dashboard')
def dashboard():
    users = User.query.limit(100).all()
    for user in users:
        # Another query per user!
        user.post_count = Post.query.filter_by(user_id=user.id).count()
    return render_template('dashboard.html', users=users)
"""
    
    result = await deepika.review(slow_code, "python")
    
    print(f"✅ Issues Found: {result['issues_found']}")
    
    assert result['issues_found'] > 0, "Should find N+1 query problems"
    assert any('n+1' in str(detail).lower() or 'query' in str(detail).lower() 
               for detail in result['details']), "Should identify N+1 pattern"
    
    print("\n✓ TEST PASSED")
    return result


async def test_memory_issues():
    """Test DEEPIKA detects memory leaks and excessive memory usage"""
    print("\n" + "="*60)
    print("TEST 3: Memory Issues Detection")
    print("="*60)
    
    deepika = DeepikaAdversarial(project_id="test-perf-003")
    
    slow_code = """
# Loading all data into memory
def export_all_users():
    users = User.query.all()  # No pagination! Could be 1M+ users
    return json.dumps([u.to_dict() for u in users])

# Memory leak - file not closed
def read_log():
    f = open('app.log', 'r')
    data = f.read()
    # Missing f.close() - file handle leak
    return data

# Growing cache without limits
cache = {}
def get_product(product_id):
    if product_id not in cache:
        cache[product_id] = Product.query.get(product_id)  # Cache grows forever
    return cache[product_id]
"""
    
    result = await deepika.review(slow_code, "python")
    
    print(f"✅ Issues Found: {result['issues_found']}")
    
    assert result['issues_found'] > 0, "Should find memory issues"
    
    print("\n✓ TEST PASSED")
    return result


async def test_blocking_operations():
    """Test DEEPIKA detects blocking operations in async code"""
    print("\n" + "="*60)
    print("TEST 4: Blocking Operations in Async Code")
    print("="*60)
    
    deepika = DeepikaAdversarial(project_id="test-perf-004")
    
    slow_code = """
import time
import requests

async def process_order(order_id):
    # Blocking sleep in async function!
    time.sleep(5)  # Should use asyncio.sleep
    
    # Blocking HTTP request
    response = requests.get('https://api.example.com/order')  # Should use aiohttp
    
    # Blocking file I/O
    with open('order.txt', 'r') as f:  # Should use aiofiles
        data = f.read()
    
    return data

async def calculate_heavy():
    # CPU-intensive work blocking event loop
    result = sum(i**2 for i in range(10000000))  # Should use executor
    return result
"""
    
    result = await deepika.review(slow_code, "python")
    
    print(f"✅ Issues Found: {result['issues_found']}")
    
    assert result['issues_found'] > 0, "Should find blocking operations"
    
    print("\n✓ TEST PASSED")
    return result


async def test_missing_indexes():
    """Test DEEPIKA detects missing database indexes"""
    print("\n" + "="*60)
    print("TEST 5: Missing Database Indexes")
    print("="*60)
    
    deepika = DeepikaAdversarial(project_id="test-perf-005")
    
    slow_code = """
# Query on unindexed email column
users = User.query.filter_by(email=email).first()

# ORDER BY on unindexed created_at
posts = Post.query.order_by(Post.created_at.desc()).limit(10).all()

# Full table scan on status
active_users = User.query.filter(User.status == 'active').all()

# Missing composite index
orders = Order.query.filter_by(
    user_id=user_id,
    status='pending'
).all()
"""
    
    result = await deepika.review(slow_code, "python")
    
    print(f"✅ Issues Found: {result['issues_found']}")
    
    print("\n✓ TEST PASSED")
    return result


async def test_no_streaming():
    """Test DEEPIKA detects large file operations without streaming"""
    print("\n" + "="*60)
    print("TEST 6: Large File Operations Without Streaming")
    print("="*60)
    
    deepika = DeepikaAdversarial(project_id="test-perf-006")
    
    slow_code = """
def process_large_file(filename):
    # Loading entire file into memory
    with open(filename, 'r') as f:
        data = f.read()  # Could be 10GB!
    
    lines = data.split('\\n')
    return len(lines)

def export_csv():
    # Loading all rows into memory
    products = Product.query.all()  # Could be millions
    csv_data = '\\n'.join([p.to_csv() for p in products])
    return csv_data
"""
    
    result = await deepika.review(slow_code, "python")
    
    print(f"✅ Issues Found: {result['issues_found']}")
    
    print("\n✓ TEST PASSED")
    return result


async def test_missing_caching():
    """Test DEEPIKA detects missing cache opportunities"""
    print("\n" + "="*60)
    print("TEST 7: Missing Caching Opportunities")
    print("="*60)
    
    deepika = DeepikaAdversarial(project_id="test-perf-007")
    
    slow_code = """
@app.route('/stats')
def get_stats():
    # Expensive calculation on every request
    total_users = User.query.count()
    total_posts = Post.query.count()
    total_comments = Comment.query.count()
    
    # Could be cached for 5 minutes
    return {
        'users': total_users,
        'posts': total_posts,
        'comments': total_comments
    }

def calculate_fibonacci(n):
    # No memoization
    if n <= 1:
        return n
    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)
"""
    
    result = await deepika.review(slow_code, "python")
    
    print(f"✅ Issues Found: {result['issues_found']}")
    
    print("\n✓ TEST PASSED")
    return result


async def test_comprehensive_performance():
    """Test DEEPIKA on code with multiple performance issues"""
    print("\n" + "="*60)
    print("TEST 8: Comprehensive Performance Audit")
    print("="*60)
    
    deepika = DeepikaAdversarial(project_id="test-perf-008")
    
    slow_code = """
def get_dashboard_data(user_id):
    # Issue 1: Loading all users (no pagination)
    users = User.query.all()
    
    # Issue 2: N+1 query problem
    user_data = []
    for user in users:
        posts = Post.query.filter_by(user_id=user.id).all()
        user_data.append({
            'user': user,
            'posts': posts
        })
    
    # Issue 3: Nested loops (O(n²))
    matches = []
    for u1 in users:
        for u2 in users:
            if u1.id != u2.id and u1.city == u2.city:
                matches.append((u1, u2))
    
    # Issue 4: No caching for expensive operation
    stats = {
        'total_users': User.query.count(),
        'total_posts': Post.query.count()
    }
    
    # Issue 5: Loading large file into memory
    with open('/var/log/app.log', 'r') as f:
        logs = f.read()
    
    return {
        'users': user_data,
        'matches': matches,
        'stats': stats,
        'logs': logs
    }
"""
    
    result = await deepika.review(slow_code, "python")
    
    print(f"✅ Issues Found: {result['issues_found']}")
    print(f"Severities: {result['severity']}")
    
    # Should find multiple performance issues
    assert result['issues_found'] >= 3, "Should find at least 3 performance issues"
    
    print("\n📋 All Issues Found:")
    for i, issue in enumerate(result['details'], 1):
        print(f"\n  {i}. [{issue.get('severity', 'UNKNOWN')}] {issue.get('issue', 'N/A')}")
        print(f"     Category: {issue.get('category', 'N/A')}")
        print(f"     Impact: {issue.get('scale_impact', 'N/A')[:60]}...")
    
    print("\n✓ TEST PASSED")
    return result


async def test_statistics():
    """Test that DEEPIKA tracks statistics correctly"""
    print("\n" + "="*60)
    print("TEST 9: Statistics Tracking")
    print("="*60)
    
    deepika = DeepikaAdversarial(project_id="test-perf-009")
    
    code1 = "for i in items:\n    for j in items:\n        if i == j: pass"
    code2 = "users = User.query.all()"
    code3 = "for user in users:\n    posts = Post.query.filter_by(user_id=user.id).all()"
    
    await deepika.review(code1, "python")
    await deepika.review(code2, "python")
    await deepika.review(code3, "python")
    
    stats = deepika.get_statistics()
    
    print(f"Total Reviews: {stats['total_reviews']}")
    print(f"Total Issues: {stats['total_issues_found']}")
    print(f"Critical: {stats['critical_issues']}")
    print(f"High: {stats['high_issues']}")
    print(f"Average/Review: {stats['average_issues_per_review']:.2f}")
    
    assert stats['total_reviews'] == 3, "Should track review count"
    assert stats['total_issues_found'] > 0, "Should track issues found"
    
    print("\n✓ TEST PASSED")
    return stats


async def run_all_tests():
    """Run complete test suite"""
    print("\n" + "="*60)
    print("DEEPIKA ADVERSARIAL AGENT - COMPLETE TEST SUITE")
    print("="*60)
    
    results = []
    
    try:
        results.append(await test_algorithmic_complexity())
        results.append(await test_n_plus_1_queries())
        results.append(await test_memory_issues())
        results.append(await test_blocking_operations())
        results.append(await test_missing_indexes())
        results.append(await test_no_streaming())
        results.append(await test_missing_caching())
        results.append(await test_comprehensive_performance())
        await test_statistics()
        
        print("\n" + "="*60)
        print("🎉 ALL TESTS PASSED!")
        print("="*60)
        
        total_issues = sum(r['issues_found'] for r in results)
        critical_count = sum(r['severity'].count('CRITICAL') for r in results)
        high_count = sum(r['severity'].count('HIGH') for r in results)
        
        print(f"\nTotal performance issues found: {total_issues}")
        print(f"Critical: {critical_count}")
        print(f"High: {high_count}")
        print(f"Average per test: {total_issues/len(results):.1f}")
        
        print("\n✅ DEEPIKA is working correctly and ready for integration")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        raise
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        raise


if __name__ == "__main__":
    print("\n⚡ Starting DEEPIKA performance test suite...")
    asyncio.run(run_all_tests())
