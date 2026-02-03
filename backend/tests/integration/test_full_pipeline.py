"""
END-TO-END INTEGRATION TEST - ALL 9 AGENTS
Location: backend/tests/integration/test_full_pipeline.py

Tests the complete NexSidi pipeline from user conversation to deployment:
1. Tilotma (Orchestrator) - Handles user conversation
2. Saanvi (Architect) - Analyzes requirements
3. Shubham (Backend Dev) - Generates backend code
4. Aanya (Frontend Dev) - Generates frontend code
5. Navya (Logic Review) - Reviews for logic errors
6. Karan (Security Review) - Reviews for vulnerabilities
7. Deepika (Performance Review) - Reviews for performance issues
8. Aarav (Browser Testing) - Tests UI/UX
9. Pranav (DevOps) - Deploys to production

Usage:
    pytest tests/integration/test_full_pipeline.py -v -s
"""

import pytest
import asyncio
import json
from typing import Dict, Any
from uuid import uuid4
from datetime import datetime


# =============================================================================
# TEST FIXTURES
# =============================================================================

@pytest.fixture
def project_id():
    """Generate unique project ID for test"""
    return f"test-{uuid4()}"


@pytest.fixture
def user_id():
    """Generate unique user ID for test"""
    return f"user-{uuid4()}"


@pytest.fixture
def sample_conversation():
    """Sample user conversation for requirements gathering"""
    return [
        "Hi, I need a simple todo list application",
        "It should have user authentication",
        "Users should be able to create, edit, and delete tasks",
        "Each task should have a title, description, and due date",
        "I want it deployed to the cloud"
    ]


@pytest.fixture
def expected_architecture():
    """Expected architecture from Saanvi"""
    return {
        "project_type": "web_application",
        "complexity_score": 5,
        "backend": {
            "framework": "FastAPI",
            "database": "PostgreSQL",
            "authentication": "JWT"
        },
        "frontend": {
            "framework": "React",
            "styling": "Tailwind CSS"
        },
        "features": [
            "User authentication",
            "CRUD operations for tasks",
            "Task management"
        ]
    }


# =============================================================================
# INDIVIDUAL AGENT TESTS
# =============================================================================

class TestIndividualAgents:
    """Test each agent in isolation"""
    
    @pytest.mark.asyncio
    async def test_tilotma_conversation(self, project_id, user_id, sample_conversation):
        """Test Tilotma handles conversation correctly"""
        from app.agents.tilotma import Tilotma
        
        tilotma = Tilotma(project_id=project_id, user_id=user_id)
        
        # Simulate conversation
        for message in sample_conversation:
            response = await tilotma.chat(message)
            
            assert response is not None
            assert len(response) > 0
            assert isinstance(response, str)
        
        # Check conversation state
        status = tilotma.get_project_status()
        assert status["messages_count"] >= len(sample_conversation) * 2  # User + Assistant
        assert status["total_cost"] > 0
        
        print(f"✅ Tilotma: {status['messages_count']} messages, ₹{status['total_cost']:.2f}")
    
    @pytest.mark.asyncio
    async def test_saanvi_requirements_analysis(self, project_id, user_id, sample_conversation):
        """Test Saanvi analyzes requirements correctly"""
        from app.agents.saanvi import Saanvi
        
        saanvi = Saanvi(project_id=project_id, user_id=user_id)
        
        # Analyze requirements
        spec = await saanvi.analyze_requirements(
            conversation=sample_conversation,
            project_name="Todo List App"
        )
        
        assert spec is not None
        assert hasattr(spec, 'pricing')
        assert spec.pricing.complexity_score > 0
        assert spec.pricing.total_price > 0
        
        print(f"✅ Saanvi: Complexity {spec.pricing.complexity_score}/10, ₹{spec.pricing.total_price}")
    
    @pytest.mark.asyncio
    async def test_shubham_backend_generation(self, project_id, expected_architecture):
        """Test Shubham generates backend code correctly"""
        from app.agents.shubham import Shubham
        
        shubham = Shubham(project_id=project_id)
        
        # Generate backend
        result = await shubham.execute({
            "architecture": expected_architecture,
            "project_name": "Todo List App"
        })
        
        assert result["status"] == "success"
        assert "files" in result
        assert len(result["files"]) > 0
        assert result["total_files"] > 0
        
        print(f"✅ Shubham: {result['total_files']} files, ₹{result['cost']:.2f}")
    
    @pytest.mark.asyncio
    async def test_aanya_frontend_generation(self, project_id, expected_architecture):
        """Test Aanya generates frontend code correctly"""
        from app.agents.aanya import Aanya
        
        aanya = Aanya(project_id=project_id)
        
        # Generate frontend
        result = await aanya.execute({
            "frontend_architecture": expected_architecture["frontend"],
            "api_architecture": expected_architecture["backend"],
            "business_requirements": expected_architecture
        })
        
        assert result["status"] == "success"
        assert "files" in result
        assert len(result["files"]) > 0
        assert result["total_files"] > 0
        
        print(f"✅ Aanya: {result['total_files']} files, ₹{result['cost']:.2f}")
    
    @pytest.mark.asyncio
    async def test_navya_logic_review(self, project_id):
        """Test Navya reviews code for logic errors"""
        from app.agents.navya_adversarial import NavyaAdversarial
        
        navya = NavyaAdversarial(project_id=project_id)
        
        # Sample code to review
        sample_code = {
            "main.py": "def add(a, b): return a + b"
        }
        
        result = await navya.review(sample_code, file_type="python")
        
        assert "bugs_found" in result
        assert isinstance(result["bugs_found"], int)
        
        print(f"✅ Navya: {result['bugs_found']} logic issues found")
    
    @pytest.mark.asyncio
    async def test_karan_security_review(self, project_id):
        """Test Karan reviews code for security vulnerabilities"""
        from app.agents.karan_adversarial import KaranAdversarial
        
        karan = KaranAdversarial(project_id=project_id)
        
        # Sample code to review
        sample_code = {
            "auth.py": "def login(username, password): return True"
        }
        
        result = await karan.review(sample_code, file_type="python")
        
        assert "vulnerabilities_found" in result
        assert isinstance(result["vulnerabilities_found"], int)
        
        print(f"✅ Karan: {result['vulnerabilities_found']} security issues found")
    
    @pytest.mark.asyncio
    async def test_deepika_performance_review(self, project_id):
        """Test Deepika reviews code for performance issues"""
        from app.agents.deepika_adversarial import DeepikaAdversarial
        
        deepika = DeepikaAdversarial(project_id=project_id)
        
        # Sample code to review
        sample_code = {
            "utils.py": "def process(data): return [x*2 for x in data]"
        }
        
        result = await deepika.review(sample_code, file_type="python")
        
        assert "issues_found" in result
        assert isinstance(result["issues_found"], int)
        
        print(f"✅ Deepika: {result['issues_found']} performance issues found")
    
    @pytest.mark.asyncio
    async def test_aarav_browser_testing(self, project_id):
        """Test Aarav performs browser testing"""
        from app.agents.aarav_testing import AaravTesting
        
        aarav = AaravTesting(project_id=project_id)
        
        # Sample test scenario
        test_scenario = {
            "url": "http://localhost:3000",
            "tests": ["login", "create_task", "delete_task"]
        }
        
        result = await aarav.execute(test_scenario)
        
        assert result["status"] == "success"
        assert "tests_passed" in result
        
        print(f"✅ Aarav: {result.get('tests_passed', 0)} tests passed")
    
    @pytest.mark.asyncio
    async def test_pranav_deployment(self, project_id, expected_architecture):
        """Test Pranav deploys application correctly"""
        from app.agents.pranav import Pranav
        
        pranav = Pranav(project_id=project_id)
        
        # Deploy
        result = await pranav.execute({
            "architecture": expected_architecture,
            "backend_files": [],
            "frontend_files": []
        })
        
        assert result["success"] == True
        assert "deployment" in result
        assert "urls" in result
        assert result["urls"]["backend"] is not None
        assert result["urls"]["frontend"] is not None
        
        print(f"✅ Pranav: Backend={result['urls']['backend']}, Frontend={result['urls']['frontend']}")


# =============================================================================
# FULL PIPELINE INTEGRATION TEST
# =============================================================================

class TestFullPipeline:
    """Test complete end-to-end pipeline with all 9 agents"""
    
    @pytest.mark.asyncio
    async def test_complete_pipeline(self, project_id, user_id, sample_conversation):
        """
        Test the complete pipeline from conversation to deployment.
        
        Flow:
        1. Tilotma handles conversation
        2. Tilotma delegates to Saanvi for requirements
        3. Saanvi analyzes and returns specification
        4. Tilotma delegates to Shubham for backend
        5. Tilotma delegates to Aanya for frontend
        6. Tilotma delegates to Navya/Karan/Deepika for review
        7. Tilotma delegates to Aarav for testing
        8. Tilotma delegates to Pranav for deployment
        9. Return final result to user
        """
        from app.agents.tilotma import Tilotma
        
        print("\n" + "="*80)
        print("FULL PIPELINE TEST - ALL 9 AGENTS")
        print("="*80)
        
        # Initialize orchestrator
        tilotma = Tilotma(project_id=project_id, user_id=user_id)
        
        # Phase 1: Conversation (Tilotma)
        print("\n[1/9] 💬 Tilotma - Handling conversation...")
        for i, message in enumerate(sample_conversation, 1):
            response = await tilotma.chat(message)
            print(f"  Message {i}/{len(sample_conversation)}: {len(response)} chars")
        
        # Phase 2: Requirements Analysis (Saanvi via Tilotma)
        print("\n[2/9] 📋 Saanvi - Analyzing requirements...")
        saanvi_result = await tilotma.delegate_to_saanvi()
        assert saanvi_result["status"] == "success"
        print(f"  Complexity: {saanvi_result.get('complexity', 'N/A')}/10")
        print(f"  Price: ₹{saanvi_result.get('price', 0)}")
        
        # Phase 3: Backend Development (Shubham via Tilotma)
        print("\n[3/9] 💻 Shubham - Generating backend...")
        shubham_result = await tilotma.delegate_to_shubham(
            requirements=saanvi_result
        )
        assert shubham_result["status"] == "success"
        print(f"  Files generated: {shubham_result.get('files_generated', 0)}")
        
        # Phase 4: Frontend Development (Aanya via Tilotma)
        print("\n[4/9] 🌐 Aanya - Generating frontend...")
        aanya_result = await tilotma.delegate_to_aanya(
            requirements=saanvi_result,
            design={}
        )
        assert aanya_result["status"] == "success"
        print(f"  Files generated: {aanya_result.get('files_generated', 0)}")
        
        # Phase 5-7: Adversarial Review (Navya, Karan, Deepika via Tilotma)
        print("\n[5-7/9] ✅ Adversarial Review - Navya, Karan, Deepika...")
        code_bundle = {
            "backend": shubham_result.get("code", {}),
            "frontend": aanya_result.get("code", {})
        }
        review_result = await tilotma.delegate_to_navya(code_bundle)
        
        if review_result["status"] == "success":
            print(f"  Total issues found: {review_result.get('total_bugs', 0)}")
            print(f"  Navya (logic): {review_result.get('navya', {}).get('bugs_found', 0)}")
            print(f"  Karan (security): {review_result.get('karan', {}).get('vulnerabilities_found', 0)}")
            print(f"  Deepika (performance): {review_result.get('deepika', {}).get('issues_found', 0)}")
        
        # Phase 8: Browser Testing (Aarav)
        print("\n[8/9] 🧪 Aarav - Browser testing...")
        # Note: Aarav testing would require deployed app, so we'll mark as deferred
        print("  Status: Deferred (requires deployed app)")
        
        # Phase 9: Deployment (Pranav via Tilotma)
        print("\n[9/9] 🚀 Pranav - Deploying to production...")
        deployment_result = await tilotma.delegate_to_pranav(code_bundle)
        
        if deployment_result["status"] == "success":
            print(f"  Backend URL: {deployment_result.get('url', 'N/A')}")
            print(f"  Platform: {deployment_result.get('platform', 'N/A')}")
        
        # Final Summary
        print("\n" + "="*80)
        print("PIPELINE COMPLETE - SUMMARY")
        print("="*80)
        
        project_status = tilotma.get_project_status()
        print(f"Total Messages: {project_status['messages_count']}")
        print(f"Total Cost: ₹{project_status['total_cost']:.2f}")
        print(f"Complexity: {project_status['complexity_estimate']}/10")
        print(f"Last Agent: {project_status['last_agent_called']}")
        
        # Assertions
        assert saanvi_result["status"] == "success"
        assert shubham_result["status"] == "success"
        assert aanya_result["status"] == "success"
        assert deployment_result["status"] == "success"
        assert project_status["total_cost"] > 0
        
        print("\n✅ ALL AGENTS TESTED SUCCESSFULLY!")
        print("="*80 + "\n")


# =============================================================================
# ERROR HANDLING TESTS
# =============================================================================

class TestErrorHandling:
    """Test error handling and recovery mechanisms"""
    
    @pytest.mark.asyncio
    async def test_agent_failure_recovery(self, project_id, user_id):
        """Test that pipeline handles agent failures gracefully"""
        from app.agents.tilotma import Tilotma
        
        tilotma = Tilotma(project_id=project_id, user_id=user_id)
        
        # Try to delegate with invalid data
        result = await tilotma.delegate_to_saanvi()
        
        # Should handle error gracefully
        assert result is not None
        assert "status" in result
    
    @pytest.mark.asyncio
    async def test_retry_mechanism(self, project_id, user_id):
        """Test that agents retry on failure"""
        from app.agents.tilotma import Tilotma
        
        tilotma = Tilotma(project_id=project_id, user_id=user_id)
        
        # Simulate retry scenario
        retry_result = await tilotma.retry_agent_with_feedback(
            agent_name="saanvi",
            feedback="Please provide more detail",
            original_input={}
        )
        
        assert retry_result is not None
        assert "status" in retry_result


# =============================================================================
# PERFORMANCE TESTS
# =============================================================================

class TestPerformance:
    """Test performance and cost optimization"""
    
    @pytest.mark.asyncio
    async def test_cost_tracking(self, project_id, user_id, sample_conversation):
        """Test that costs are tracked accurately"""
        from app.agents.tilotma import Tilotma
        
        tilotma = Tilotma(project_id=project_id, user_id=user_id)
        
        # Run conversation
        for message in sample_conversation:
            await tilotma.chat(message)
        
        status = tilotma.get_project_status()
        
        assert status["total_cost"] > 0
        assert status["total_cost"] < 100  # Sanity check
        
        print(f"Total cost for {len(sample_conversation)} messages: ₹{status['total_cost']:.2f}")


# =============================================================================
# MAIN TEST RUNNER
# =============================================================================

if __name__ == "__main__":
    """
    Run tests directly:
        python tests/integration/test_full_pipeline.py
    """
    pytest.main([__file__, "-v", "-s", "--tb=short"])
