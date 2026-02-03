"""
API CONNECTION TEST SCRIPT
Test all AI providers: Claude, Gemini AI Studio, Vertex AI

Run this before starting development to verify what's working.
"""

import os
import sys
import asyncio
import httpx
from typing import Dict, List, Optional
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# =============================================================================
# MODEL CONFIGURATIONS
# =============================================================================

CLAUDE_MODELS = {
    "claude-opus-4.5": "claude-opus-4-5-20251101",
    "claude-sonnet-4.5": "claude-sonnet-4-5-20250929",
    "claude-haiku-4.5": "claude-haiku-4-5-20251001",
    "claude-opus-4.1": "claude-opus-4-1-20250514",
}

GEMINI_MODELS_AI_STUDIO = {
    "gemini-3-pro-preview": "gemini-3-pro-preview",
}

GEMINI_MODELS_VERTEX = {
    "gemini-3-pro-preview": "gemini-3-pro-preview",
    "gemini-3-flash-preview": "gemini-3-flash-preview",
    "gemini-2.5-pro": "gemini-2.5-pro",
    "gemini-2.5-flash": "gemini-2.5-flash",
    "gemini-2.5-flash-lite": "gemini-2.5-flash-lite",
}

# =============================================================================
# TEST RESULTS STORAGE
# =============================================================================

test_results = {
    "claude": {},
    "gemini_ai_studio": {},
    "vertex_ai": {},
    "summary": {}
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def print_header(text: str):
    """Print formatted header"""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80)

def print_test(provider: str, model: str, status: str, details: str = ""):
    """Print test result"""
    emoji = "✅" if status == "SUCCESS" else "❌" if status == "FAIL" else "⚠️"
    print(f"{emoji} {provider:20} | {model:30} | {status:10} {details}")

def print_summary():
    """Print final summary"""
    print_header("TEST SUMMARY")
    
    total_tests = 0
    passed = 0
    failed = 0
    
    for provider, results in test_results.items():
        if provider == "summary":
            continue
        for model, result in results.items():
            total_tests += 1
            if result.get("status") == "SUCCESS":
                passed += 1
            else:
                failed += 1
    
    print(f"\nTotal Tests: {total_tests}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"Success Rate: {(passed/total_tests*100) if total_tests > 0 else 0:.1f}%")
    
    # Environment check
    print("\n" + "-" * 80)
    print("ENVIRONMENT VARIABLES CHECK:")
    print(f"ANTHROPIC_API_KEY: {'✅ Set' if os.getenv('ANTHROPIC_API_KEY') else '❌ Missing'}")
    print(f"GOOGLE_API_KEY: {'✅ Set' if os.getenv('GOOGLE_API_KEY') else '❌ Missing'}")
    print(f"GOOGLE_CLOUD_PROJECT: {'✅ Set' if os.getenv('GOOGLE_CLOUD_PROJECT') else '❌ Missing'}")
    print(f"GOOGLE_APPLICATION_CREDENTIALS: {'✅ Set' if os.getenv('GOOGLE_APPLICATION_CREDENTIALS') else '❌ Missing'}")
    
    # Recommendations
    print("\n" + "-" * 80)
    print("RECOMMENDATIONS:")
    if failed == 0:
        print("✅ All providers working! You're ready to start development.")
    else:
        if not os.getenv('ANTHROPIC_API_KEY'):
            print("⚠️ Add ANTHROPIC_API_KEY to .env for Claude access")
        if not os.getenv('GOOGLE_API_KEY'):
            print("⚠️ Add GOOGLE_API_KEY to .env for Gemini AI Studio access")
        if not os.getenv('GOOGLE_CLOUD_PROJECT'):
            print("⚠️ Add GOOGLE_CLOUD_PROJECT to .env for Vertex AI access")
            print("   Get this from: https://console.cloud.google.com")
        if not os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
            print("⚠️ Add GOOGLE_APPLICATION_CREDENTIALS to .env for Vertex AI access")
            print("   Download service account JSON from GCP Console")

# =============================================================================
# CLAUDE API TESTS
# =============================================================================

async def test_claude_model(model_name: str, model_id: str) -> Dict:
    """Test single Claude model"""
    
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return {
            "status": "SKIP",
            "error": "ANTHROPIC_API_KEY not set",
            "model": model_id
        }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": model_id,
                    "max_tokens": 100,
                    "messages": [
                        {"role": "user", "content": "Say 'Hello from Claude!' in exactly 3 words."}
                    ]
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data.get("content", [{}])[0].get("text", "")
                usage = data.get("usage", {})
                
                return {
                    "status": "SUCCESS",
                    "model": model_id,
                    "response": content[:50],
                    "input_tokens": usage.get("input_tokens", 0),
                    "output_tokens": usage.get("output_tokens", 0)
                }
            else:
                return {
                    "status": "FAIL",
                    "error": f"HTTP {response.status_code}: {response.text[:200]}",
                    "model": model_id
                }
                
    except Exception as e:
        return {
            "status": "FAIL",
            "error": str(e)[:200],
            "model": model_id
        }

async def test_all_claude():
    """Test all Claude models"""
    print_header("TESTING CLAUDE API (Anthropic)")
    
    for model_name, model_id in CLAUDE_MODELS.items():
        result = await test_claude_model(model_name, model_id)
        test_results["claude"][model_name] = result
        
        if result["status"] == "SUCCESS":
            details = f"({result['input_tokens']}→{result['output_tokens']} tokens)"
            print_test("Claude", model_name, "SUCCESS", details)
        elif result["status"] == "SKIP":
            print_test("Claude", model_name, "SKIP", result["error"])
        else:
            print_test("Claude", model_name, "FAIL", result["error"][:50])

# =============================================================================
# GEMINI AI STUDIO TESTS
# =============================================================================

async def test_gemini_ai_studio_model(model_name: str, model_id: str) -> Dict:
    """Test single Gemini AI Studio model"""
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return {
            "status": "SKIP",
            "error": "GOOGLE_API_KEY not set",
            "model": model_id
        }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:generateContent?key={api_key}"
            
            response = await client.post(
                url,
                json={
                    "contents": [{
                        "role": "user",
                        "parts": [{"text": "Say 'Hello from Gemini!' in exactly 3 words."}]
                    }],
                    "generationConfig": {
                        "maxOutputTokens": 100,
                        "temperature": 0.7
                    }
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                content = ""
                if data.get("candidates"):
                    parts = data["candidates"][0].get("content", {}).get("parts", [])
                    content = parts[0].get("text", "") if parts else ""
                
                usage = data.get("usageMetadata", {})
                
                return {
                    "status": "SUCCESS",
                    "model": model_id,
                    "response": content[:50],
                    "input_tokens": usage.get("promptTokenCount", 0),
                    "output_tokens": usage.get("candidatesTokenCount", 0)
                }
            else:
                return {
                    "status": "FAIL",
                    "error": f"HTTP {response.status_code}: {response.text[:200]}",
                    "model": model_id
                }
                
    except Exception as e:
        return {
            "status": "FAIL",
            "error": str(e)[:200],
            "model": model_id
        }

async def test_all_gemini_ai_studio():
    """Test all Gemini AI Studio models"""
    print_header("TESTING GEMINI AI STUDIO (Google)")
    
    for model_name, model_id in GEMINI_MODELS_AI_STUDIO.items():
        result = await test_gemini_ai_studio_model(model_name, model_id)
        test_results["gemini_ai_studio"][model_name] = result
        
        if result["status"] == "SUCCESS":
            details = f"({result['input_tokens']}→{result['output_tokens']} tokens)"
            print_test("Gemini AI Studio", model_name, "SUCCESS", details)
        elif result["status"] == "SKIP":
            print_test("Gemini AI Studio", model_name, "SKIP", result["error"])
        else:
            print_test("Gemini AI Studio", model_name, "FAIL", result["error"][:50])

# =============================================================================
# VERTEX AI TESTS
# =============================================================================

async def test_vertex_ai_model(model_name: str, model_id: str) -> Dict:
    """Test single Vertex AI model"""
    
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    
    if not project_id:
        return {
            "status": "SKIP",
            "error": "GOOGLE_CLOUD_PROJECT not set",
            "model": model_id
        }
    
    if not credentials_path:
        return {
            "status": "SKIP",
            "error": "GOOGLE_APPLICATION_CREDENTIALS not set",
            "model": model_id
        }
    
    if not os.path.exists(credentials_path):
        return {
            "status": "SKIP",
            "error": f"Credentials file not found: {credentials_path}",
            "model": model_id
        }
    
    try:
        # Import here to avoid error if not installed
        import vertexai
        from vertexai.generative_models import GenerativeModel, Content, Part
        from google.oauth2 import service_account
        
        # Initialize Vertex AI
        credentials = service_account.Credentials.from_service_account_file(credentials_path)
        vertexai.init(
            project=project_id,
            location=os.getenv("GOOGLE_CLOUD_LOCATION", "global"),
            credentials=credentials
        )
        
        # Create model
        model = GenerativeModel(model_id)
        
        # Generate content
        response = model.generate_content(
            "Say 'Hello from Vertex!' in exactly 3 words.",
            generation_config={
                "max_output_tokens": 100,
                "temperature": 0.7
            }
        )
        
        return {
            "status": "SUCCESS",
            "model": model_id,
            "response": response.text[:50],
            "input_tokens": 0,  # Vertex doesn't always provide exact counts
            "output_tokens": 0
        }
        
    except ImportError as e:
        return {
            "status": "FAIL",
            "error": f"Missing dependency: {str(e)[:100]}. Run: pip install google-cloud-aiplatform",
            "model": model_id
        }
    except Exception as e:
        return {
            "status": "FAIL",
            "error": str(e)[:200],
            "model": model_id
        }

async def test_all_vertex_ai():
    """Test all Vertex AI models"""
    print_header("TESTING VERTEX AI (Google Cloud)")
    
    for model_name, model_id in GEMINI_MODELS_VERTEX.items():
        result = await test_vertex_ai_model(model_name, model_id)
        test_results["vertex_ai"][model_name] = result
        
        if result["status"] == "SUCCESS":
            print_test("Vertex AI", model_name, "SUCCESS", f"Response: {result['response']}")
        elif result["status"] == "SKIP":
            print_test("Vertex AI", model_name, "SKIP", result["error"])
        else:
            print_test("Vertex AI", model_name, "FAIL", result["error"][:50])

# =============================================================================
# MAIN TEST RUNNER
# =============================================================================

async def main():
    """Run all API tests"""
    
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "API CONNECTION TEST SUITE" + " " * 33 + "║")
    print("║" + " " * 78 + "║")
    print("║  Testing all AI providers: Claude, Gemini AI Studio, Vertex AI" + " " * 13 + "║")
    print("║  " + f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}" + " " * 53 + "║")
    print("╚" + "═" * 78 + "╝")
    
    # Test each provider
    await test_all_claude()
    await test_all_gemini_ai_studio()
    await test_all_vertex_ai()
    
    # Print summary
    print_summary()
    
    print("\n" + "=" * 80)
    print("Testing complete! Review results above.")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        sys.exit(1)