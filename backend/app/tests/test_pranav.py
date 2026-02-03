"""
Test Pranav (DevOps Engineer)
Tests deployment configuration generation
"""
import os 
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import asyncio
from app.database import SessionLocal
from app.agents.pranav import Pranav

async def test_pranav():
    print("\n" + "="*70)
    print("  TESTING PRANAV - DEVOPS ENGINEER")
    print("="*70)
    
    db = SessionLocal()
    
    try:
        # Mock architecture
        architecture = {
            "technical_decisions": {
                "deployment": {
                    "backend": "Railway",
                    "frontend": "Vercel",
                    "database": "Railway PostgreSQL"
                }
            }
        }
        
        # Create Pranav
        pranav = Pranav(db=db, project_id="test-project-123")
        
        print("\n📦 Generating deployment configurations...")
        print("   Target: Railway (backend) + Vercel (frontend)")
        
        # Execute deployment
        result = await pranav.execute({
            "architecture": architecture,
            "project_id": "test-project-123"
        })
        
        if result["success"]:
            print("\n✅ Deployment Complete!")
            
            deployment = result["deployment"]
            
            print("\n🚂 BACKEND DEPLOYMENT (Railway):")
            backend = deployment["backend"]
            print(f"   Status: {backend['status']}")
            print(f"   URL: {backend['url']}")
            
            print("\n▲ FRONTEND DEPLOYMENT (Vercel):")
            frontend = deployment["frontend"]
            print(f"   Status: {frontend['status']}")
            print(f"   URL: {frontend['url']}")
            
            print("\n📝 CONFIG FILES GENERATED:")
            for file in result["config_files"]:
                print(f"   {file['path']}")
            
        else:
            print(f"\n❌ Deployment Failed: {result.get('error')}")
        
    finally:
        db.close()
    
    print("\n" + "="*70)

if __name__ == "__main__":
    asyncio.run(test_pranav())