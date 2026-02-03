"""
Test Shubham (Backend Developer)
Tests backend-only code generation
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from dotenv import load_dotenv
load_dotenv()

import asyncio
from uuid import uuid4
from datetime import datetime
from app.database import SessionLocal
from app.agents.shubham import Shubham
from app.models import Project, User

async def test_shubham():
    print("\n" + "="*70)
    print("  TESTING SHUBHAM - BACKEND DEVELOPER")
    print("="*70)
    
    db = SessionLocal()
    
    try:
        # Step 1: Create unique test user (with timestamp to avoid duplicates)
        test_user_id = uuid4()
        test_email = f"test_shubham_{int(datetime.now().timestamp())}@test.com"  # ← Unique email
        
        test_user = User(
            id=test_user_id,
            email=test_email,
            hashed_password="dummy_hash",
            full_name="Test User"
        )
        db.add(test_user)
        db.commit()
        print(f"\n✅ Created test user: {test_user_id}")
        print(f"   Email: {test_email}")
        
        # Step 2: Create test project
        test_project_id = uuid4()
        test_project = Project(
            id=test_project_id,
            user_id=test_user_id,
            title="Test Restaurant Website",
            description="Test project for Shubham",
            status="requirements_gathered"
        )
        db.add(test_project)
        db.commit()
        print(f"✅ Created test project: {test_project_id}")
        
        # Step 3: Mock architecture from Saanvi
        architecture = {
            "database_architecture": {
                "tables": [
                    {
                        "name": "users",
                        "columns": [
                            {"name": "id", "type": "UUID", "constraints": ["PRIMARY KEY"]},
                            {"name": "email", "type": "VARCHAR(255)", "constraints": ["UNIQUE", "NOT NULL"]},
                            {"name": "password_hash", "type": "VARCHAR(255)", "constraints": ["NOT NULL"]},
                            {"name": "role", "type": "VARCHAR(50)", "constraints": ["DEFAULT 'customer'"]}
                        ],
                        "indexes": [{"columns": ["email"], "type": "UNIQUE"}],
                        "relationships": []
                    },
                    {
                        "name": "menu_items",
                        "columns": [
                            {"name": "id", "type": "UUID", "constraints": ["PRIMARY KEY"]},
                            {"name": "name", "type": "VARCHAR(255)", "constraints": ["NOT NULL"]},
                            {"name": "price", "type": "DECIMAL(10,2)", "constraints": ["NOT NULL"]},
                            {"name": "category", "type": "VARCHAR(100)", "constraints": []}
                        ],
                        "indexes": [],
                        "relationships": []
                    },
                    {
                        "name": "reservations",
                        "columns": [
                            {"name": "id", "type": "UUID", "constraints": ["PRIMARY KEY"]},
                            {"name": "user_id", "type": "UUID", "constraints": ["NOT NULL"]},
                            {"name": "reservation_date", "type": "DATE", "constraints": ["NOT NULL"]},
                            {"name": "num_guests", "type": "INTEGER", "constraints": ["NOT NULL"]}
                        ],
                        "indexes": [],
                        "relationships": [
                            {"from_column": "user_id", "to_table": "users", "to_column": "id"}
                        ]
                    }
                ]
            },
            "api_architecture": {
                "base_url": "/api/v1",
                "endpoints": [
                    {"path": "/auth/signup", "method": "POST", "purpose": "Create account"},
                    {"path": "/auth/login", "method": "POST", "purpose": "Login"},
                    {"path": "/menu", "method": "GET", "purpose": "Get menu items"},
                    {"path": "/reservations", "method": "POST", "purpose": "Create reservation"},
                    {"path": "/reservations", "method": "GET", "purpose": "Get user reservations"}
                ]
            }
        }
        
        # Step 4: Create Shubham
        shubham = Shubham(db=db, project_id=str(test_project_id))
        
        print(f"\n📝 Generating backend code...")
        print(f"   Project ID: {test_project_id}")
        print(f"   Tables: {len(architecture['database_architecture']['tables'])}")
        print(f"   Endpoints: {len(architecture['api_architecture']['endpoints'])}")
        
        # Step 5: Execute backend generation
        result = await shubham.execute({
            "architecture": architecture,
            "project_id": str(test_project_id)
        })
        
        if result["success"]:
            print("\n✅ Backend Generation Complete!")
            print(f"   Files Generated: {result['backend_files']}")
            
            print("\n📁 BACKEND FILE MANIFEST:")
            for file in result["file_manifest"][:10]:
                print(f"   {file['path']} ({file['lines']} lines)")
            
            if len(result["file_manifest"]) > 10:
                print(f"   ... and {len(result['file_manifest']) - 10} more files")
            
        else:
            print(f"\n❌ Backend Generation Failed: {result.get('error')}")
        
        # Step 6: Cleanup
        print("\n🧹 Cleaning up test data...")
        db.query(Project).filter(Project.id == test_project_id).delete()
        db.query(User).filter(User.id == test_user_id).delete()
        db.commit()
        print("✅ Cleanup complete")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        # Cleanup on error
        try:
            db.rollback()
        except:
            pass
        
    finally:
        db.close()
    
    print("\n" + "="*70)

if __name__ == "__main__":
    asyncio.run(test_shubham())