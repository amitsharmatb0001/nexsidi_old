"""
Test Saanvi (System Architect)
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from dotenv import load_dotenv
load_dotenv()

import asyncio
from app.database import SessionLocal
from app.agents.saanvi import Saanvi

async def test_saanvi():
    print("\n" + "="*70)
    print("  TESTING SAANVI - SYSTEM ARCHITECT")
    print("="*70)
    
    db = SessionLocal()
    
    try:
        # Sample conversation
        conversation = [
            {"role": "user", "content": "I want to create a website for my restaurant"},
            {"role": "assistant", "content": "That sounds great! What features do you need?"},
            {"role": "user", "content": "It's an Italian restaurant called Pasta Paradise in Mumbai"},
            {"role": "assistant", "content": "Lovely name! What specific features?"},
            {"role": "user", "content": "Customers should view the menu and make reservations"},
            {"role": "assistant", "content": "Perfect! Anything else?"},
            {"role": "user", "content": "Maybe online ordering in future, but not now"},
        ]
        
        # Create Saanvi
        saanvi = Saanvi(db=db, user_id="test-user-123")
        
        print("\n🏗️ Designing complete system architecture...")
        print(f"   Conversation: {len(conversation)} messages")
        
        # Execute architecture design
        result = await saanvi.execute({
            "conversation_history": conversation
        })
        
        # ⭐ DEBUG: Print what we actually got ⭐
        print("\n🔍 DEBUG - Result keys:", list(result.keys()))
        print("🔍 DEBUG - Full result:")
        import json
        print(json.dumps(result, indent=2, default=str))
        
        if result["success"]:
            print("\n✅ Architecture Design Complete!")
            print(f"   Cost: ₹{result.get('cost', 0)}")
            
            # Check if architecture exists
            if "architecture" not in result:
                print("\n⚠️ WARNING: 'architecture' key missing from result!")
                print("Available keys:", list(result.keys()))
                return
            
            arch = result["architecture"]
            
            # Display overview
            print("\n📋 PROJECT OVERVIEW:")
            overview = arch.get("project_overview", {})
            print(f"   Title: {overview.get('project_title')}")
            print(f"   Complexity: {overview.get('complexity_score')}/10")
            print(f"   Reasoning: {overview.get('complexity_reasoning', '')[:80]}...")
            
            # Display database architecture
            print("\n🗄️ DATABASE ARCHITECTURE:")
            db_arch = arch.get("database_architecture", {})
            tables = db_arch.get("tables", [])
            print(f"   Tables designed: {len(tables)}")
            for table in tables[:3]:  # Show first 3
                print(f"   - {table['name']} ({len(table.get('columns', []))} columns)")
            
            # Display API architecture
            print("\n🔌 API ARCHITECTURE:")
            api_arch = arch.get("api_architecture", {})
            endpoints = api_arch.get("endpoints", [])
            print(f"   Endpoints designed: {len(endpoints)}")
            for endpoint in endpoints[:3]:  # Show first 3
                print(f"   - {endpoint['method']} {endpoint['path']}")
            
            # Display frontend architecture
            print("\n🎨 FRONTEND ARCHITECTURE:")
            fe_arch = arch.get("frontend_architecture", {})
            pages = fe_arch.get("pages", [])
            print(f"   Pages designed: {len(pages)}")
            for page in pages:
                print(f"   - {page['route']} ({page['component']})")
            
            # Display pricing
            print("\n💰 PRICING:")
            pricing = arch.get("pricing", {})
            print(f"   Base Price: ₹{pricing.get('base_price', 0):,}")
            
            timeline = arch.get("timeline", {})
            print(f"   Timeline: {timeline.get('total_days', 0)} days")
            
        else:
            print(f"\n❌ Architecture Design Failed: {result.get('error')}")
        
    finally:
        db.close()
    
    print("\n" + "="*70)

if __name__ == "__main__":
    asyncio.run(test_saanvi())