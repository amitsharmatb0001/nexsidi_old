"""
AGENT VERIFICATION SCRIPT
Location: backend/tests/verify_agents.py

Quick script to verify all 9 agents are properly configured.

Usage:
    python tests/verify_agents.py
"""

import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))


def verify_agents():
    """Verify all 9 agents can be imported and initialized"""
    
    print("="*80)
    print("AGENT VERIFICATION - ALL 9 AGENTS")
    print("="*80 + "\n")
    
    agents = []
    errors = []
    
    # 1. Tilotma
    try:
        from app.agents.tilotma import Tilotma
        tilotma = Tilotma(project_id="test-001", user_id="user-001")
        agents.append("✅ Tilotma (Orchestrator)")
    except Exception as e:
        errors.append(f"❌ Tilotma: {e}")
    
    # 2. Saanvi
    try:
        from app.agents.saanvi import Saanvi
        saanvi = Saanvi(project_id="test-001", user_id="user-001")
        agents.append("✅ Saanvi (Requirements Analyst)")
    except Exception as e:
        errors.append(f"❌ Saanvi: {e}")
    
    # 3. Shubham
    try:
        from app.agents.shubham import Shubham
        shubham = Shubham(project_id="test-001")
        agents.append("✅ Shubham (Backend Developer)")
    except Exception as e:
        errors.append(f"❌ Shubham: {e}")
    
    # 4. Aanya
    try:
        from app.agents.aanya import Aanya
        aanya = Aanya(project_id="test-001")
        agents.append("✅ Aanya (Frontend Developer)")
    except Exception as e:
        errors.append(f"❌ Aanya: {e}")
    
    # 5. Navya
    try:
        from app.agents.navya_adversarial import NavyaAdversarial
        navya = NavyaAdversarial(project_id="test-001")
        agents.append("✅ Navya (Logic Reviewer)")
    except Exception as e:
        errors.append(f"❌ Navya: {e}")
    
    # 6. Karan
    try:
        from app.agents.karan_adversarial import KaranAdversarial
        karan = KaranAdversarial(project_id="test-001")
        agents.append("✅ Karan (Security Reviewer)")
    except Exception as e:
        errors.append(f"❌ Karan: {e}")
    
    # 7. Deepika
    try:
        from app.agents.deepika_adversarial import DeepikaAdversarial
        deepika = DeepikaAdversarial(project_id="test-001")
        agents.append("✅ Deepika (Performance Reviewer)")
    except Exception as e:
        errors.append(f"❌ Deepika: {e}")
    
    # 8. Aarav
    try:
        from app.agents.aarav_testing import AaravTesting
        aarav = AaravTesting(project_id="test-001")
        agents.append("✅ Aarav (Browser Testing)")
    except Exception as e:
        errors.append(f"❌ Aarav: {e}")
    
    # 9. Pranav
    try:
        from app.agents.pranav import Pranav
        pranav = Pranav(project_id="test-001")
        agents.append("✅ Pranav (DevOps)")
    except Exception as e:
        errors.append(f"❌ Pranav: {e}")
    
    # Print results
    print("AGENT STATUS:\n")
    for agent in agents:
        print(f"  {agent}")
    
    if errors:
        print("\nERRORS:\n")
        for error in errors:
            print(f"  {error}")
    
    print("\n" + "="*80)
    print(f"SUMMARY: {len(agents)}/9 agents verified successfully")
    print("="*80 + "\n")
    
    # Return status
    if len(agents) == 9:
        print("✅ ALL AGENTS READY FOR INTEGRATION TESTING!\n")
        return 0
    else:
        print(f"⚠️  {9 - len(agents)} agent(s) need attention\n")
        return 1


if __name__ == "__main__":
    exit_code = verify_agents()
    sys.exit(exit_code)
