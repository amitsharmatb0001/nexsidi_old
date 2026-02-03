"""
Simple AI Provider Connection Test
Quick test to verify Vertex AI and Claude AI are working
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from dotenv import load_dotenv
load_dotenv()

import asyncio


async def main():
    print("\n" + "="*70)
    print("  TESTING AI PROVIDER CONNECTIONS")
    print("="*70)
    
    # Import after loading env
    from app.agents.ai_router import AIRouter, TaskType, Complexity, ModelProvider, ModelTier
    
    router = AIRouter()
    
    # Show what's configured
    print("\n📋 Configuration Status:")
    print(f"   Vertex AI: {'✅ Configured' if router.has_vertex_ai else '❌ Not configured'}")
    print(f"   Claude AI: {'✅ Configured' if router.has_anthropic else '❌ Not configured'}")
    print(f"   Gemini AI Studio: {'✅ Configured' if router.has_gemini_ai_studio else '❌ Not configured'}")
    
    if router.has_vertex_ai:
        print(f"\n   Vertex AI Details:")
        print(f"   - Project: {router.google_cloud_project}")
        print(f"   - Location: {router.google_cloud_location}")
        print(f"   - Credentials: {router.google_application_credentials}")
    
    # Test Vertex AI
    if router.has_vertex_ai:
        print("\n" + "-"*70)
        print("Testing Vertex AI...")
        print("-"*70)
        try:
            response = await router.complete(
                messages=[{"role": "user", "content": "Reply with exactly: 'Vertex AI works!'"}],
                provider=ModelProvider.GEMINI_VERTEX,
                model="gemini-1.5-flash",
                task_type=TaskType.CHAT,
                complexity=Complexity.LOW,
                max_tokens=20
            )
            print(f"✅ SUCCESS!")
            print(f"   Model: {response.model_id}")
            print(f"   Response: {response.content}")
            print(f"   Tokens: {response.total_tokens}")
        except Exception as e:
            print(f"❌ FAILED: {e}")
    
    # Test Claude AI
    if router.has_anthropic:
        print("\n" + "-"*70)
        print("Testing Claude AI...")
        print("-"*70)
        try:
            response = await router.complete(
                messages=[{"role": "user", "content": "Reply with exactly: 'Claude works!'"}],
                provider=ModelProvider.CLAUDE,
                model=ModelTier.CLAUDE_FAST,
                task_type=TaskType.CHAT,
                complexity=Complexity.LOW,
                max_tokens=20
            )
            print(f"✅ SUCCESS!")
            print(f"   Model: {response.model_id}")
            print(f"   Response: {response.content}")
            print(f"   Tokens: {response.total_tokens}")
        except Exception as e:
            print(f"❌ FAILED: {e}")
    
    # Test Gemini AI Studio
    if router.has_gemini_ai_studio:
        print("\n" + "-"*70)
        print("Testing Gemini AI Studio...")
        print("-"*70)
        try:
            response = await router.complete(
                messages=[{"role": "user", "content": "Reply with exactly: 'Gemini works!'"}],
                provider=ModelProvider.GEMINI_AI_STUDIO,
                model=ModelTier.GEMINI_AI_STUDIO_FAST,
                task_type=TaskType.CHAT,
                complexity=Complexity.LOW,
                max_tokens=20
            )
            print(f"✅ SUCCESS!")
            print(f"   Model: {response.model_id}")
            print(f"   Response: {response.content}")
            print(f"   Tokens: {response.total_tokens}")
        except Exception as e:
            print(f"❌ FAILED: {e}")
    
    print("\n" + "="*70)
    print("  TEST COMPLETE")
    print("="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
