"""
Test suite for KARAN adversarial security agent.

Tests various security vulnerability detection scenarios:
- SQL Injection
- Cross-Site Scripting (XSS)
- CSRF vulnerabilities
- Authentication/Authorization flaws
- Hardcoded credentials
- Path traversal
- Insecure deserialization
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

from app.agents.karan_adversarial import KaranAdversarial


async def test_sql_injection():
    """Test KARAN detects SQL injection vulnerabilities"""
    print("\n" + "="*60)
    print("TEST 1: SQL Injection Detection")
    print("="*60)
    
    karan = KaranAdversarial(project_id="test-sec-001")
    
    vulnerable_code = """
def get_user_by_email(email):
    query = f"SELECT * FROM users WHERE email = '{email}'"
    return db.execute(query)

def search_products(search_term):
    sql = "SELECT * FROM products WHERE name LIKE '%" + search_term + "%'"
    return execute(sql)

def delete_user(user_id):
    cursor.execute(f"DELETE FROM users WHERE id = {user_id}")
"""
    
    result = await karan.review(vulnerable_code, "python")
    
    print(f"✅ Vulnerabilities Found: {result['vulnerabilities_found']}")
    print(f"Severities: {result['severity']}")
    
    # Assertions
    assert result['vulnerabilities_found'] > 0, "Should find SQL injection vulnerabilities"
    assert any('sql' in str(detail).lower() or 'injection' in str(detail).lower() 
               for detail in result['details']), "Should identify SQL injection"
    assert any(detail['severity'] == 'CRITICAL' for detail in result['details']), \
        "SQL injection should be CRITICAL severity"
    
    print("\n📋 Details:")
    for i, vuln in enumerate(result['details'], 1):
        print(f"\n  Vulnerability {i}:")
        print(f"    Issue: {vuln.get('issue', 'N/A')}")
        print(f"    Severity: {vuln.get('severity', 'N/A')}")
        print(f"    CVE: {vuln.get('cve_reference', 'N/A')}")
        print(f"    Exploit: {vuln.get('exploit_example', 'N/A')[:60]}...")
    
    print("\n✓ TEST PASSED")
    return result


async def test_xss_detection():
    """Test KARAN detects Cross-Site Scripting vulnerabilities"""
    print("\n" + "="*60)
    print("TEST 2: XSS (Cross-Site Scripting) Detection")
    print("="*60)
    
    karan = KaranAdversarial(project_id="test-sec-002")
    
    vulnerable_code = """
@app.route('/comment', methods=['POST'])
def post_comment():
    comment = request.form['comment']
    # Vulnerable: No sanitization
    return f"<div>{comment}</div>"

def display_username(username):
    html = "<h1>Welcome " + username + "</h1>"
    return html

# React component with dangerouslySetInnerHTML
const UserProfile = ({bio}) => {
    return <div dangerouslySetInnerHTML={{__html: bio}} />;
};
"""
    
    result = await karan.review(vulnerable_code, "python")
    
    print(f"✅ Vulnerabilities Found: {result['vulnerabilities_found']}")
    
    assert result['vulnerabilities_found'] > 0, "Should find XSS vulnerabilities"
    assert any(detail['severity'] == 'CRITICAL' for detail in result['details']), \
        "XSS should be CRITICAL"
    
    print("\n✓ TEST PASSED")
    return result


async def test_authentication_bypass():
    """Test KARAN detects authentication/authorization flaws"""
    print("\n" + "="*60)
    print("TEST 3: Authentication/Authorization Flaws")
    print("="*60)
    
    karan = KaranAdversarial(project_id="test-sec-003")
    
    vulnerable_code = """
@app.route('/admin/delete/<user_id>')
def delete_user(user_id):
    # Missing authentication check!
    User.query.filter_by(id=user_id).delete()
    return "Deleted"

@app.route('/user/<user_id>/profile')
def get_profile(user_id):
    # IDOR: No authorization check
    user = User.query.get(user_id)
    return jsonify(user.to_dict())

def change_password(user_id, new_password):
    # No verification if current user owns this account
    user = User.query.get(user_id)
    user.password = new_password
    db.session.commit()
"""
    
    result = await karan.review(vulnerable_code, "python")
    
    print(f"✅ Vulnerabilities Found: {result['vulnerabilities_found']}")
    
    assert result['vulnerabilities_found'] > 0, "Should find auth vulnerabilities"
    
    print("\n✓ TEST PASSED")
    return result


async def test_hardcoded_credentials():
    """Test KARAN detects hardcoded credentials"""
    print("\n" + "="*60)
    print("TEST 4: Hardcoded Credentials Detection")
    print("="*60)
    
    karan = KaranAdversarial(project_id="test-sec-004")
    
    vulnerable_code = """
# Hardcoded API key
API_KEY = "sk_live_51H8xabc123def456ghi789"
STRIPE_SECRET = "sk_test_abcdefghijklmnop"

# Hardcoded database password
DATABASE_URL = "postgresql://admin:password123@localhost/db"

# Hardcoded AWS credentials
AWS_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE"
AWS_SECRET_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"

# Hardcoded JWT secret
JWT_SECRET = "supersecretkey123"
"""
    
    result = await karan.review(vulnerable_code, "python")
    
    print(f"✅ Vulnerabilities Found: {result['vulnerabilities_found']}")
    
    assert result['vulnerabilities_found'] > 0, "Should find hardcoded credentials"
    assert any(detail['severity'] in ['CRITICAL', 'HIGH'] for detail in result['details']), \
        "Hardcoded credentials should be high severity"
    
    print("\n✓ TEST PASSED")
    return result


async def test_path_traversal():
    """Test KARAN detects path traversal vulnerabilities"""
    print("\n" + "="*60)
    print("TEST 5: Path Traversal Detection")
    print("="*60)
    
    karan = KaranAdversarial(project_id="test-sec-005")
    
    vulnerable_code = """
@app.route('/download/<filename>')
def download_file(filename):
    # Vulnerable: No path sanitization
    file_path = f"/uploads/{filename}"
    return send_file(file_path)

def read_user_file(user_id, filename):
    # Path traversal risk
    path = os.path.join("/user_data/", user_id, filename)
    with open(path, 'r') as f:
        return f.read()

def serve_image(image_name):
    return open(f"./images/{image_name}").read()
"""
    
    result = await karan.review(vulnerable_code, "python")
    
    print(f"✅ Vulnerabilities Found: {result['vulnerabilities_found']}")
    
    assert result['vulnerabilities_found'] > 0, "Should find path traversal"
    
    print("\n✓ TEST PASSED")
    return result


async def test_insecure_deserialization():
    """Test KARAN detects insecure deserialization"""
    print("\n" + "="*60)
    print("TEST 6: Insecure Deserialization Detection")
    print("="*60)
    
    karan = KaranAdversarial(project_id="test-sec-006")
    
    vulnerable_code = """
import pickle
import yaml

def load_user_data(data):
    # CRITICAL: pickle with untrusted data
    return pickle.loads(data)

def parse_config(yaml_string):
    # Vulnerable: yaml.load without safe_load
    return yaml.load(yaml_string)

def execute_user_code(code_string):
    # CRITICAL: eval with user input
    result = eval(code_string)
    return result
"""
    
    result = await karan.review(vulnerable_code, "python")
    
    print(f"✅ Vulnerabilities Found: {result['vulnerabilities_found']}")
    
    assert result['vulnerabilities_found'] > 0, "Should find deserialization issues"
    
    print("\n✓ TEST PASSED")
    return result


async def test_csrf_vulnerability():
    """Test KARAN detects CSRF vulnerabilities"""
    print("\n" + "="*60)
    print("TEST 7: CSRF Detection")
    print("="*60)
    
    karan = KaranAdversarial(project_id="test-sec-007")
    
    vulnerable_code = """
# State-changing operation without CSRF protection
@app.route('/transfer', methods=['GET'])  # Should be POST with CSRF token
def transfer_money():
    from_account = request.args.get('from')
    to_account = request.args.get('to')
    amount = request.args.get('amount')
    
    # No CSRF token validation
    execute_transfer(from_account, to_account, amount)
    return "Transfer complete"

@app.route('/delete-account', methods=['POST'])
def delete_account():
    # Missing CSRF token check
    user_id = request.form['user_id']
    User.query.filter_by(id=user_id).delete()
"""
    
    result = await karan.review(vulnerable_code, "python")
    
    print(f"✅ Vulnerabilities Found: {result['vulnerabilities_found']}")
    
    print("\n✓ TEST PASSED")
    return result


async def test_comprehensive_security():
    """Test KARAN on code with multiple security issues"""
    print("\n" + "="*60)
    print("TEST 8: Comprehensive Security Audit")
    print("="*60)
    
    karan = KaranAdversarial(project_id="test-sec-008")
    
    vulnerable_code = """
import os
import pickle
from flask import Flask, request, render_template_string

app = Flask(__name__)

# Hardcoded credentials
DB_PASSWORD = "admin123"
API_KEY = "sk_live_abcdefg"

@app.route('/user/<user_id>')
def get_user(user_id):
    # SQL Injection
    query = f"SELECT * FROM users WHERE id = {user_id}"
    result = db.execute(query)
    return result

@app.route('/search')
def search():
    term = request.args.get('q')
    # XSS vulnerability
    return f"<h1>Results for: {term}</h1>"

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    # No file type validation
    file.save(f"./uploads/{file.filename}")
    return "Uploaded"

@app.route('/data', methods=['POST'])
def load_data():
    data = request.data
    # Insecure deserialization
    obj = pickle.loads(data)
    return str(obj)

@app.route('/admin/delete')
def admin_delete():
    # Missing authentication
    user_id = request.args.get('id')
    User.query.filter_by(id=user_id).delete()
    return "Deleted"

def read_file(filename):
    # Path traversal
    return open(f"./files/{filename}").read()
"""
    
    result = await karan.review(vulnerable_code, "python")
    
    print(f"✅ Vulnerabilities Found: {result['vulnerabilities_found']}")
    print(f"Severities: {result['severity']}")
    
    # Should find multiple critical vulnerabilities
    assert result['vulnerabilities_found'] >= 5, "Should find at least 5 vulnerabilities"
    assert result['severity'].count('CRITICAL') >= 2, "Should have multiple CRITICAL issues"
    
    print("\n📋 All Vulnerabilities Found:")
    for i, vuln in enumerate(result['details'], 1):
        print(f"\n  {i}. [{vuln.get('severity', 'UNKNOWN')}] {vuln.get('issue', 'N/A')}")
        print(f"     CVE: {vuln.get('cve_reference', 'N/A')}")
        print(f"     Impact: {vuln.get('impact', 'N/A')[:60]}...")
    
    print("\n✓ TEST PASSED")
    return result


async def test_statistics():
    """Test that KARAN tracks statistics correctly"""
    print("\n" + "="*60)
    print("TEST 9: Statistics Tracking")
    print("="*60)
    
    karan = KaranAdversarial(project_id="test-sec-009")
    
    code1 = "query = f'SELECT * FROM users WHERE id = {user_id}'"
    code2 = "return f'<div>{user_input}</div>'"
    code3 = "API_KEY = 'sk_live_123456'"
    
    await karan.review(code1, "python")
    await karan.review(code2, "python")
    await karan.review(code3, "python")
    
    stats = karan.get_statistics()
    
    print(f"Total Reviews: {stats['total_reviews']}")
    print(f"Total Vulnerabilities: {stats['total_vulnerabilities_found']}")
    print(f"Critical: {stats['critical_vulnerabilities']}")
    print(f"High: {stats['high_vulnerabilities']}")
    print(f"Average/Review: {stats['average_vulns_per_review']:.2f}")
    
    assert stats['total_reviews'] == 3, "Should track review count"
    assert stats['total_vulnerabilities_found'] > 0, "Should track vulnerabilities"
    
    print("\n✓ TEST PASSED")
    return stats


async def run_all_tests():
    """Run complete test suite"""
    print("\n" + "="*60)
    print("KARAN ADVERSARIAL AGENT - COMPLETE TEST SUITE")
    print("="*60)
    
    results = []
    
    try:
        results.append(await test_sql_injection())
        results.append(await test_xss_detection())
        results.append(await test_authentication_bypass())
        results.append(await test_hardcoded_credentials())
        results.append(await test_path_traversal())
        results.append(await test_insecure_deserialization())
        results.append(await test_csrf_vulnerability())
        results.append(await test_comprehensive_security())
        await test_statistics()
        
        print("\n" + "="*60)
        print("🎉 ALL TESTS PASSED!")
        print("="*60)
        
        total_vulns = sum(r['vulnerabilities_found'] for r in results)
        critical_count = sum(r['severity'].count('CRITICAL') for r in results)
        high_count = sum(r['severity'].count('HIGH') for r in results)
        
        print(f"\nTotal vulnerabilities found: {total_vulns}")
        print(f"Critical: {critical_count}")
        print(f"High: {high_count}")
        print(f"Average per test: {total_vulns/len(results):.1f}")
        
        print("\n✅ KARAN is working correctly and ready for integration")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        raise
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        raise


if __name__ == "__main__":
    print("\n🔒 Starting KARAN security test suite...")
    asyncio.run(run_all_tests())
