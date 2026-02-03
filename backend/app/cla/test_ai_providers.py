"""
Test AI Provider Connections
Tests connectivity to Vertex AI (GCP) and Claude AI (Anthropic)
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from dotenv import load_dotenv
load_dotenv()

import asyncio
from app.agents.ai_router import AIRouter, TaskType, Complexity


async def test_vertex_ai():
    """Test Vertex AI connection to GCP"""
    print("\n" + "="*70)
    print("  TESTING VERTEX AI (GCP) CONNECTION")
    print("="*70)
    
    router = AIRouter()
    
    # Check if Vertex AI is configured
    if not router.has_vertex_ai:
        print("\n❌ Vertex AI NOT configured")
        print("   Missing environment variables:")
        if not router.google_cloud_project:
            print("   - GOOGLE_CLOUD_PROJECT")
        if not router.google_cloud_location:
            print("   - GOOGLE_CLOUD_LOCATION (optional, defaults to us-central1)")
        if not router.google_application_credentials:
            print("   - GOOGLE_APPLICATION_CREDENTIALS")
        return False
    
    print(f"\n✅ Vertex AI configured")
    print(f"   Project: {router.google_cloud_project}")
    print(f"   Location: {router.google_cloud_location}")
    print(f"   Credentials: {router.google_application_credentials}")
    
    # Test actual API call
    print("\n📡 Testing Vertex AI API call...")
    try:
        from app.agents.ai_router import ModelProvider, ModelTier
        
        response = await router.complete(
            messages=[{"role": "user", "content": "Say 'Hello from Vertex AI!' and nothing else."}],
            provider=ModelProvider.GEMINI_VERTEX,
            model=ModelTier.GEMINI_VERTEX_FAST,
            task_type=TaskType.CHAT,
            complexity=Complexity.LOW,
            max_tokens=50
        )
        
        print(f"\n✅ Vertex AI API call successful!")
        print(f"   Model: {response.model_id}")
        print(f"   Response: {response.content}")
        print(f"   Tokens: {response.total_tokens}")
        print(f"   Latency: {response.latency_ms:.0f}ms")
        return True
        
    except Exception as e:
        print(f"\n❌ Vertex AI API call failed!")
        print(f"   Error: {e}")
        return False


async def test_claude_ai():
    """Test Claude AI (Anthropic) connection"""
    print("\n" + "="*70)
    print("  TESTING CLAUDE AI (ANTHROPIC) CONNECTION")
    print("="*70)
    
    router = AIRouter()
    
    # Check if Claude is configured
    if not router.has_anthropic:
        print("\n❌ Claude AI NOT configured")
        print("   Missing environment variable:")
        print("   - ANTHROPIC_API_KEY")
        return False
    
    print(f"\n✅ Claude AI configured")
    print(f"   API Key: {router.anthropic_api_key[:20]}...{router.anthropic_api_key[-4:]}")
    
    # Test actual API call
    print("\n📡 Testing Claude AI API call...")
    try:
        from app.agents.ai_router import ModelProvider, ModelTier
        
        response = await router.complete(
            messages=[{"role": "user", "content": "Say 'Hello from Claude!' and nothing else."}],
            provider=ModelProvider.CLAUDE,
            model=ModelTier.CLAUDE_FAST,
            task_type=TaskType.CHAT,
            complexity=Complexity.LOW,
            max_tokens=50
        )
        
        print(f"\n✅ Claude AI API call successful!")
        print(f"   Model: {response.model_id}")
        print(f"   Response: {response.content}")
        print(f"   Tokens: {response.total_tokens}")
        print(f"   Latency: {response.latency_ms:.0f}ms")
        return True
        
    except Exception as e:
        print(f"\n❌ Claude AI API call failed!")
        print(f"   Error: {e}")
        return False


async def test_gemini_ai_studio():
    """Test Gemini AI Studio connection"""
    print("\n" + "="*70)
    print("  TESTING GEMINI AI STUDIO CONNECTION")
    print("="*70)
    
    router = AIRouter()
    
    # Check if Gemini AI Studio is configured
    if not router.has_gemini_ai_studio:
        print("\n❌ Gemini AI Studio NOT configured")
        print("   Missing environment variable:")
        print("   - GOOGLE_API_KEY")
        return False
    
    print(f"\n✅ Gemini AI Studio configured")
    print(f"   API Key: {router.google_ai_studio_key[:20]}...{router.google_ai_studio_key[-4:]}")
    
    # Test actual API call
    print("\n📡 Testing Gemini AI Studio API call...")
    try:
        from app.agents.ai_router import ModelProvider, ModelTier
        
        response = await router.complete(
            messages=[{"role": "user", "content": "Say 'Hello from Gemini!' and nothing else."}],
            provider=ModelProvider.GEMINI_AI_STUDIO,
            model=ModelTier.GEMINI_AI_STUDIO_FAST,
            task_type=TaskType.CHAT,
            complexity=Complexity.LOW,
            max_tokens=50
        )
        
        print(f"\n✅ Gemini AI Studio API call successful!")
        print(f"   Model: {response.model_id}")
        print(f"   Response: {response.content}")
        print(f"   Tokens: {response.total_tokens}")
        print(f"   Latency: {response.latency_ms:.0f}ms")
        return True
        
    except Exception as e:
        print(f"\n❌ Gemini AI Studio API call failed!")
        print(f"   Error: {e}")
        return False


async def main():
    """Run all AI provider tests"""
    print("\n" + "="*70)
    print("  AI PROVIDER CONNECTION TESTS")
    print("="*70)
    
    results = {
        "Vertex AI (GCP)": await test_vertex_ai(),
        "Claude AI (Anthropic)": await test_claude_ai(),
        "Gemini AI Studio": await test_gemini_ai_studio()
    }
    
    # Summary
    print("\n" + "="*70)
    print("  TEST SUMMARY")
    print("="*70)
    
    for provider, success in results.items():
        status = "✅ WORKING" if success else "❌ FAILED"
        print(f"{status}: {provider}")
    
    # Overall result
    working_count = sum(results.values())
    total_count = len(results)
    
    print(f"\n📊 {working_count}/{total_count} providers working")
    
    if working_count == 0:
        print("\n⚠️  WARNING: No AI providers are working!")
        print("   Please check your .env file and API keys.")
    elif working_count < total_count:
        print("\n⚠️  Some providers are not working.")
        print("   The system will use fallback providers when needed.")
    else:
        print("\n🎉 All AI providers are working correctly!")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    asyncio.run(main())
