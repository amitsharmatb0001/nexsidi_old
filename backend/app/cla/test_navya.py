import asyncio
import sys
import os
from uuid import uuid4

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, User, Project
from app.agents.navya import Navya
import json

# Database setup
DATABASE_URL = "postgresql://postgres:root@localhost/nexsidi"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

async def test_navya():
    """Test Navya - QA Specialist"""
    
    print("\n" + "="*70)
    print("  TESTING NAVYA - QA SPECIALIST")
    print("="*70 + "\n")
    
    # Check AI Router configuration first
    print("🔍 Checking AI Router configuration...")
    from app.services.ai_router import ai_router
    
    if not ai_router.claude_available and not ai_router.vertex_available and not ai_router.gemini_available:
        print("\n❌ ERROR: No AI providers configured!")
        print("\n📋 To fix:")
        print("   1. Open E:\\nexsidi\\backend\\.env")
        print("   2. Add these keys:")
        print("      ANTHROPIC_API_KEY=your-claude-key")
        print("      GOOGLE_API_KEY=your-gemini-key")
        print("      GOOGLE_APPLICATION_CREDENTIALS=path-to-service-account.json")
        print("      GOOGLE_CLOUD_PROJECT=your-project-id")
        print("\n⚠️ Skipping test - AI Router needs configuration\n")
        return
    
    print("✅ AI Router configured successfully\n")
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Create test user with proper UUID
        test_user_id = uuid4()
        test_user = User(
            id=test_user_id,
            email="test@nexsidi.com",
            name="Test User",
            hashed_password="dummy"
        )
        db.add(test_user)
        
        # Create test project with proper UUID
        test_project_id = uuid4()
        test_project = Project(
            id=test_project_id,
            user_id=test_user_id,
            name="E-commerce Platform",
            description="Full-stack e-commerce with React and FastAPI",
            status="in_progress"
        )
        db.add(test_project)
        db.commit()
        
        print(f"✅ Created test project: {test_project_id}")
        print(f"✅ Created test user: {test_user_id}\n")
        
        # Initialize Navya
        navya = Navya(
            db=db,
            project_id=test_project_id,
            user_id=test_user_id
        )
        
        # Sample code to review
        backend_code = """
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class User(BaseModel):
    username: str
    email: str

@app.post("/users")
async def create_user(user: User):
    # TODO: Validate email format
    # TODO: Check if username already exists
    return {"message": "User created", "user": user}
"""
        
        frontend_code = """
import React, { useState } from 'react';

function UserForm() {
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    
    const handleSubmit = async (e) => {
        e.preventDefault();
        // TODO: Add input validation
        // TODO: Add error handling
        const response = await fetch('/api/users', {
            method: 'POST',
            body: JSON.stringify({ username, email })
        });
        const data = await response.json();
        console.log(data);
    };
    
    return (
        <form onSubmit={handleSubmit}>
            <input value={username} onChange={(e) => setUsername(e.target.value)} />
            <input value={email} onChange={(e) => setEmail(e.target.value)} />
            <button type="submit">Create User</button>
        </form>
    );
}
"""
        
        print("🔍 Reviewing code...")
        print(f"   Backend files: 1")
        print(f"   Frontend files: 1")
        
        # Execute Navya's code review
        result = await navya.execute({
            "backend_files": [{"path": "app/main.py", "content": backend_code}],
            "frontend_files": [{"path": "src/UserForm.jsx", "content": frontend_code}],
            "review_type": "full"
        })
        
        print("\n" + "="*70)
        print("  REVIEW RESULTS")
        print("="*70 + "\n")
        
        # Display results
        print(f"📊 Overall Score: {result.get('overall_score', 'N/A')}/10")
        print(f"✅ Passed Checks: {result.get('passed_checks', 0)}")
        print(f"❌ Failed Checks: {result.get('failed_checks', 0)}")
        print(f"⚠️  Warnings: {result.get('warnings', 0)}")
        
        if result.get('critical_issues'):
            print("\n🔴 CRITICAL ISSUES:")
            for issue in result['critical_issues']:
                print(f"   - {issue}")
        
        if result.get('suggestions'):
            print("\n💡 SUGGESTIONS:")
            for suggestion in result['suggestions'][:3]:  # Show first 3
                print(f"   - {suggestion}")
        
        print(f"\n💰 Cost: ₹{result.get('cost_inr', 0):.4f}")
        print(f"🤖 Model: {result.get('model_used', 'N/A')}")
        print(f"📝 Tokens: {result.get('tokens_used', 0)}")
        
        print("\n✅ NAVYA TEST COMPLETED SUCCESSFULLY!\n")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        
    finally:
        # Cleanup
        try:
            db.query(Project).filter(Project.id == test_project_id).delete()
            db.query(User).filter(User.id == test_user_id).delete()
            db.commit()
            print("🧹 Cleaned up test data")
        except:
            pass
        db.close()

if __name__ == "__main__":
    asyncio.run(test_navya())