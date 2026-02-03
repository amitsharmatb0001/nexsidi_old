"""
NexSidi Diagnostic Tool
Checks if everything is configured correctly for running tests
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

print("\n" + "="*70)
print("  NEXSIDI DIAGNOSTIC TOOL")
print("="*70 + "\n")

# ============================================================================
# CHECK 1: .ENV FILE
# ============================================================================
print("🔍 CHECK 1: .env File Configuration")
print("-" * 70)

from dotenv import load_dotenv
load_dotenv()

required_keys = {
    "ANTHROPIC_API_KEY": "Claude API",
    "GOOGLE_API_KEY": "Gemini API",
    "GOOGLE_APPLICATION_CREDENTIALS": "Vertex AI credentials",
    "GOOGLE_CLOUD_PROJECT": "GCP Project ID"
}

env_issues = []
for key, description in required_keys.items():
    value = os.getenv(key)
    if value:
        # Show first 20 chars for verification
        display = value[:20] + "..." if len(value) > 20 else value
        print(f"  ✅ {description:30} {display}")
    else:
        print(f"  ❌ {description:30} MISSING!")
        env_issues.append(key)

if env_issues:
    print(f"\n⚠️  Missing keys: {', '.join(env_issues)}")
    print(f"   Fix: Add these to E:\\nexsidi\\backend\\.env")
else:
    print(f"\n✅ All API keys configured!")

# ============================================================================
# CHECK 2: SERVICE ACCOUNT FILE
# ============================================================================
print("\n🔍 CHECK 2: GCP Service Account File")
print("-" * 70)

sa_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
if sa_path:
    if os.path.exists(sa_path):
        print(f"  ✅ File exists: {sa_path}")
        import json
        try:
            with open(sa_path) as f:
                sa_data = json.load(f)
            print(f"  ✅ Valid JSON format")
            print(f"  ✅ Project: {sa_data.get('project_id', 'N/A')}")
            print(f"  ✅ Client email: {sa_data.get('client_email', 'N/A')}")
        except Exception as e:
            print(f"  ❌ Error reading file: {e}")
    else:
        print(f"  ❌ File not found: {sa_path}")
        print(f"     Create file or update path in .env")
else:
    print(f"  ❌ GOOGLE_APPLICATION_CREDENTIALS not set in .env")

# ============================================================================
# CHECK 3: AI ROUTER
# ============================================================================
print("\n🔍 CHECK 3: AI Router Initialization")
print("-" * 70)

try:
    from services.ai_router import ai_router
    
    providers = []
    if ai_router.claude_available:
        providers.append("Claude (Anthropic)")
        print(f"  ✅ Claude API: Available")
    else:
        print(f"  ❌ Claude API: Not available")
    
    if ai_router.vertex_available:
        providers.append("Vertex AI (GCP)")
        print(f"  ✅ Vertex AI: Available")
    else:
        print(f"  ❌ Vertex AI: Not available")
    
    if ai_router.gemini_available:
        providers.append("Gemini AI Studio")
        print(f"  ✅ Gemini API: Available")
    else:
        print(f"  ❌ Gemini API: Not available")
    
    if providers:
        print(f"\n  ✅ AI Router has {len(providers)} provider(s): {', '.join(providers)}")
    else:
        print(f"\n  ❌ NO PROVIDERS AVAILABLE! Check your .env file and API keys")
        
except Exception as e:
    print(f"  ❌ Error importing AI Router: {e}")

# ============================================================================
# CHECK 4: DATABASE
# ============================================================================
print("\n🔍 CHECK 4: Database Connection")
print("-" * 70)

try:
    from database import engine
    connection = engine.connect()
    print(f"  ✅ PostgreSQL connection: Working")
    
    # Test query
    result = connection.execute("SELECT version();")
    version = result.fetchone()[0]
    print(f"  ✅ PostgreSQL version: {version.split(',')[0]}")
    
    connection.close()
    
except Exception as e:
    print(f"  ❌ Database connection failed: {e}")
    print(f"     Check: DATABASE_URL in .env")
    print(f"     Check: PostgreSQL is running")

# ============================================================================
# CHECK 5: IMPORTS
# ============================================================================
print("\n🔍 CHECK 5: Critical Imports")
print("-" * 70)

imports_to_check = [
    ("agents.base", "BaseAgent"),
    ("agents.tilotma", "Tilotma"),
    ("agents.navya", "Navya"),
    ("agents.shubham", "Shubham"),
    ("models", "User, Project"),
]

import_issues = []
for module, items in imports_to_check:
    try:
        __import__(module)
        print(f"  ✅ {module:30} OK")
    except Exception as e:
        print(f"  ❌ {module:30} FAILED: {str(e)[:40]}")
        import_issues.append(module)

if import_issues:
    print(f"\n  ⚠️  Import issues: {', '.join(import_issues)}")
else:
    print(f"\n  ✅ All critical imports working!")

# ============================================================================
# CHECK 6: UUID GENERATION
# ============================================================================
print("\n🔍 CHECK 6: UUID Generation")
print("-" * 70)

try:
    from uuid import uuid4
    test_uuid = uuid4()
    print(f"  ✅ UUID generation: {test_uuid}")
    print(f"  ✅ Type: {type(test_uuid)}")
except Exception as e:
    print(f"  ❌ UUID generation failed: {e}")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "="*70)
print("  DIAGNOSTIC SUMMARY")
print("="*70 + "\n")

issues = []

if env_issues:
    issues.append(f".env missing: {', '.join(env_issues)}")

if not os.path.exists(os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")):
    issues.append("Service account file not found")

try:
    from app.services.ai_router import ai_router
    if not (ai_router.claude_available or ai_router.vertex_available or ai_router.gemini_available):
        issues.append("No AI providers available")
except:
    issues.append("AI Router import failed")

if import_issues:
    issues.append(f"Import errors: {len(import_issues)} module(s)")

if issues:
    print("❌ ISSUES FOUND:")
    for i, issue in enumerate(issues, 1):
        print(f"   {i}. {issue}")
    print("\n📋 FIX THESE ISSUES BEFORE RUNNING TESTS!")
else:
    print("✅ ALL CHECKS PASSED!")
    print("\n🎉 You're ready to run tests!")
    print("\n   Run: python test_navya.py")

print("\n" + "="*70 + "\n")
