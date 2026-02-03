"""
Test Aanya (Frontend Developer)
Tests frontend-only code generation
"""

import asyncio
from app.database import SessionLocal
from app.agents.aanya import Aanya

async def test_aanya():
    print("\n" + "="*70)
    print("  TESTING AANYA - FRONTEND DEVELOPER")
    print("="*70)
    
    db = SessionLocal()
    
    try:
        # Mock architecture from Saanvi
        architecture = {
            "frontend_architecture": {
                "pages": [
                    {"route": "/", "component": "HomePage", "purpose": "Landing page"},
                    {"route": "/menu", "component": "MenuPage", "purpose": "Menu display"},
                    {"route": "/reservations", "component": "ReservationsPage", "purpose": "Reservations"}
                ],
                "component_structure": {
                    "menu": ["MenuItem", "MenuCategory"],
                    "reservation": ["ReservationForm", "ReservationCard"]
                }
            },
            "api_architecture": {
                "base_url": "/api/v1",
                "endpoints": [
                    {"path": "/menu", "method": "GET"},
                    {"path": "/reservations", "method": "POST"}
                ]
            }
        }
        
        # Create Aanya
        aanya = Aanya(db=db, project_id="test-project-123")
        
        print("\n📝 Generating frontend code...")
        print(f"   Pages: {len(architecture['frontend_architecture']['pages'])}")
        
        # Execute frontend generation
        result = await aanya.execute({
            "architecture": architecture,
            "project_id": "test-project-123"
        })
        
        if result["success"]:
            print("\n✅ Frontend Generation Complete!")
            print(f"   Files Generated: {result['frontend_files']}")
            
            print("\n📁 FRONTEND FILE MANIFEST:")
            for file in result["file_manifest"][:10]:
                print(f"   {file['path']} ({file['lines']} lines)")
            
            if len(result["file_manifest"]) > 10:
                print(f"   ... and {len(result['file_manifest']) - 10} more files")
            
        else:
            print(f"\n❌ Frontend Generation Failed: {result.get('error')}")
        
    finally:
        db.close()
    
    print("\n" + "="*70)

if __name__ == "__main__":
    asyncio.run(test_aanya())