# NexSidi FINAL CORRECTED Plan (Standalone Agents)
**Date:** January 28, 2026  
**Architecture:** V2 Standalone (No BaseAgent)  
**Status:** Tilotma ✅ + Shubham ✅ Already Tested  

---

## WHAT YOU ACTUALLY HAVE (Confirmed)

### ✅ WORKING AGENTS (Standalone V2)

**1. AI Router** (`ai_router.py`)
```
Status: 100% PRODUCTION READY
- Vertex AI + Anthropic via REST
- Auto escalation
- Cost tracking
- NO changes needed ✅
```

**2. Tilotma** (`tilotma.py`)
```
Status: ✅ TESTED & WORKING (Standalone)
Architecture: V2 Standalone (no BaseAgent)
- Direct AI Router usage
- Independent operation
- Chat interface working
- Context management working
```

**3. Shubham** (`shubham.py`)
```
Status: ✅ TESTED & WORKING (Standalone)
Test Results: 6/7 tests passing
Architecture: V2 Standalone (no BaseAgent)
- Direct AI Router usage
- Backend code generation working
- Independent from other agents
```

**4. Saanvi** (`saanvi.py`)
```
Status: Built but needs testing
Architecture: V2 Standalone
```

**5. Navya** (`navya.py`)
```
Status: Built but needs testing
Architecture: V2 Standalone
```

**6. Pranav** (`pranav.py`)
```
Status: Built but needs testing
Architecture: V2 Standalone
```

---

## V2 STANDALONE ARCHITECTURE (What You Use)

### How Each Agent Works (Independent)

```python
# Example: Tilotma (Standalone)
class Tilotma:
    def __init__(self, project_id, user_id):
        # NO inheritance from BaseAgent
        # Direct AI Router usage
        self.ai_router = ai_router
        self.project_id = project_id
        self.user_id = user_id
    
    async def chat(self, message):
        # Direct AI call
        response = await self.ai_router.generate(
            messages=[{"role": "user", "content": message}],
            task_type="chat",
            complexity=TaskComplexity.SIMPLE
        )
        return response.content
```

**Key Points:**
- ✅ NO BaseAgent dependency
- ✅ Each agent standalone
- ✅ Direct AI Router access
- ✅ Independent testing
- ✅ No cascading failures

---

## WHAT'S MISSING (Need to Build)

### NEW STANDALONE AGENTS (Create from scratch)

**1. NAVYA (Adversarial Logic)** - NEW AGENT
```
Status: 0% BUILT
Purpose: Find logic errors (adversarial)
Pattern: Copy Tilotma's standalone structure
```

**2. KARAN (Adversarial Security)** - NEW AGENT
```
Status: 0% BUILT
Purpose: Find security holes (adversarial)
Pattern: Copy Tilotma's standalone structure
```

**3. DEEPIKA (Adversarial Performance)** - NEW AGENT
```
Status: 0% BUILT
Purpose: Find performance issues (adversarial)
Pattern: Copy Tilotma's standalone structure
```

**4. AARAV (Browser Testing)** - NEW AGENT
```
Status: 0% BUILT
Purpose: Test in real browser
Pattern: Copy Tilotma's standalone structure + Playwright
```

**5. BRAND AGENT** - NEW AGENT
```
Status: 0% BUILT
Purpose: Evaluate design uniqueness
Pattern: Copy Tilotma's standalone structure
```

---

## CORRECTED 15-DAY PLAN

### Day 1: Verify What Works

```
Morning:
  □ Test Tilotma standalone (should work ✅)
  □ Test Shubham standalone (6/7 tests ✅)
  □ Test AI Router (should work ✅)
  □ Confirm: No BaseAgent needed

Afternoon:
  □ Test Saanvi standalone
  □ Test Navya standalone (old version)
  □ Test Pranav standalone
  □ Document which agents need fixes

Result: Know exactly what works vs what needs building
```

### Day 2-3: Create NEW Adversarial Agents

**Pattern to Follow:**
```python
# NEW FILE: navya_adversarial.py (standalone)
from app.services.ai_router import ai_router, TaskComplexity

class NavyaAdversarial:
    """Logic error hunter - finds bugs aggressively"""
    
    def __init__(self, project_id):
        # Standalone - no inheritance
        self.ai_router = ai_router
        self.project_id = project_id
        self.bug_patterns = self._load_patterns()
    
    async def review(self, code):
        """Find logic errors adversarially"""
        
        prompt = f"""
You are NAVYA, adversarial logic error agent.
Your ONLY goal: FIND AS MANY LOGIC ERRORS AS POSSIBLE.
You get rewarded for every bug found.

CODE TO REVIEW:
{code}

HUNT FOR:
- Division by zero
- Null pointer errors
- Off-by-one errors
- Race conditions
- Incorrect calculations
- Missing edge cases

RESPOND WITH JSON:
{{
    "bugs_found": 5,
    "details": [
        {{"file": "...", "line": 45, "issue": "...", "severity": "HIGH"}}
    ]
}}
"""
        
        response = await self.ai_router.generate(
            messages=[{"role": "user", "content": prompt}],
            task_type="adversarial_logic",  # New task type
            complexity=TaskComplexity.COMPLEX
        )
        
        return self._parse_bugs(response.content)
```

**Day 2:**
```
□ Create navya_adversarial.py (standalone)
□ Create karan_adversarial.py (standalone)
□ Load 50+ bug patterns each
□ Test with buggy code samples
```

**Day 3:**
```
□ Create deepika_adversarial.py (standalone)
□ Create competition system (parallel execution)
□ Test all 3 competing
□ Count bugs found by each
```

### Day 4: Create Browser Testing Agent

```python
# NEW FILE: aarav_testing.py (standalone)
from playwright.async_api import async_playwright

class AaravTesting:
    """Browser automation - tests like human"""
    
    def __init__(self, project_id):
        # Standalone
        self.project_id = project_id
        self.browser = None
    
    async def test_website(self, url):
        """Test website in real browser"""
        
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            
            # Test scenarios
            await page.goto(url)
            await page.screenshot(path="screenshot.png")
            
            # Click all buttons
            buttons = await page.query_selector_all("button")
            for button in buttons:
                try:
                    await button.click()
                    await page.wait_for_timeout(1000)
                except Exception as e:
                    self.report_bug(f"Button click failed: {e}")
            
            await browser.close()
```

**Day 4:**
```
□ Create aarav_testing.py (standalone)
□ Install Playwright
□ Test browser automation
□ Capture screenshots
```

### Day 5: Create Brand Agent

```python
# NEW FILE: brand_agent.py (standalone)
class BrandAgent:
    """Evaluates design uniqueness"""
    
    def __init__(self):
        # Standalone
        self.ai_router = ai_router
    
    async def evaluate(self, design_preview):
        """Score design clarity and uniqueness"""
        
        prompt = f"""
Rate this design on:
1. Instant Clarity (5-second test): 0-10
2. Uniqueness (not generic): 0-10
3. Emotional Connection: 0-10
4. Value Proposition: 0-10

DESIGN:
{design_preview}

RESPOND JSON:
{{
    "scores": {{"clarity": 9, "uniqueness": 8, "emotion": 10, "value": 10}},
    "total": 37,
    "passed": true
}}
"""
        
        response = await self.ai_router.generate(
            messages=[{"role": "user", "content": prompt}],
            task_type="brand_evaluation",
            complexity=TaskComplexity.MEDIUM
        )
        
        return self._parse_scores(response.content)
```

**Day 5:**
```
□ Create brand_agent.py (standalone)
□ Test with generic templates
□ Test with unique designs
□ Verify scoring works
```

### Day 6-7: Real-Time UI

```
Day 6:
  □ Create WebSocket endpoint (FastAPI)
  □ Broadcast agent status
  □ Test message flow

Day 7:
  □ Create React dashboard
  □ Display agents working live
  □ Show adversarial competition
```

### Day 8-9: GCP Automation

```
Day 8:
  □ Extend Pranav (standalone)
  □ Add Cloud Run API calls
  □ Add Cloud SQL API calls
  □ NO terminal commands

Day 9:
  □ Test full deployment via code
  □ Verify returns live URL
  □ Test database provisioning
```

### Day 10-12: GAN Training

```
Day 10:
  □ Design GAN architecture
  □ Generator = Shubham + Aanya
  □ Discriminators = NAVYA + KARAN + DEEPIKA

Day 11-12:
  □ Generate 100 test projects
  □ Start training loop
  □ Monitor improvements
```

### Day 13-14: Demo Projects

```
Day 13:
  □ Build Kirana shop
  □ Build Blog platform
  □ Build Stock management

Day 14:
  □ Build Restaurant orders
  □ Build Appointment booking
  □ Deploy all 5 to GCP
```

### Day 15: Final Polish

```
□ End-to-end testing
□ UI polish
□ Record demo videos
□ Create QR codes
□ Rehearse booth demo
```

---

## STANDALONE AGENT TEMPLATE

### Copy This Pattern for ALL New Agents

```python
# template_agent.py
"""
[AGENT NAME] - [PURPOSE]
Architecture: V2 Standalone (No BaseAgent)
"""

from app.services.ai_router import ai_router, TaskComplexity
import logging

class AgentName:
    """
    [Agent description]
    
    Responsibilities:
    - [Task 1]
    - [Task 2]
    - [Task 3]
    """
    
    def __init__(self, project_id: str, user_id: str = None):
        """Initialize standalone agent"""
        
        # Core attributes
        self.project_id = project_id
        self.user_id = user_id
        
        # Direct AI Router access
        self.ai_router = ai_router
        
        # Logging
        self.logger = logging.getLogger(f"agent.{self.__class__.__name__}")
    
    async def execute(self, input_data: dict):
        """
        Main execution method
        
        Args:
            input_data: Agent-specific input
        
        Returns:
            Agent-specific output
        """
        
        try:
            # Build prompt
            prompt = self._build_prompt(input_data)
            
            # Call AI Router directly
            response = await self.ai_router.generate(
                messages=[{"role": "user", "content": prompt}],
                task_type="[your_task_type]",  # Define in ai_router
                complexity=TaskComplexity.COMPLEX
            )
            
            # Log cost
            self.logger.info(
                f"✅ {response.output_tokens} tokens, "
                f"₹{response.cost_estimate:.4f}"
            )
            
            # Parse and return
            result = self._parse_response(response.content)
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Execution failed: {e}")
            raise
    
    def _build_prompt(self, input_data: dict) -> str:
        """Build agent-specific prompt"""
        # Your prompt logic
        pass
    
    def _parse_response(self, content: str):
        """Parse AI response"""
        # Your parsing logic
        pass
```

---

## AI ROUTER UPDATES NEEDED

### Add New Task Types

```python
# In ai_router.py TASK_MODEL_MAPPING, add:

TASK_MODEL_MAPPING = {
    # Existing...
    "chat": {...},
    "architecture": {...},
    "code_generation": {...},
    "code_review": {...},
    "deployment": {...},
    
    # NEW TASK TYPES:
    "adversarial_logic": {
        TaskComplexity.SIMPLE: "claude-sonnet-4.5",
        TaskComplexity.MEDIUM: "claude-sonnet-4.5",
        TaskComplexity.COMPLEX: "claude-sonnet-4.5",
    },
    "adversarial_security": {
        TaskComplexity.SIMPLE: "claude-sonnet-4.5",
        TaskComplexity.MEDIUM: "claude-sonnet-4.5",
        TaskComplexity.COMPLEX: "claude-sonnet-4.5",
    },
    "adversarial_performance": {
        TaskComplexity.SIMPLE: "claude-sonnet-4.5",
        TaskComplexity.MEDIUM: "claude-sonnet-4.5",
        TaskComplexity.COMPLEX: "claude-sonnet-4.5",
    },
    "browser_testing": {
        TaskComplexity.SIMPLE: "gemini-3-flash",
        TaskComplexity.MEDIUM: "gemini-3-flash",
        TaskComplexity.COMPLEX: "gemini-3-flash",
    },
    "brand_evaluation": {
        TaskComplexity.SIMPLE: "gemini-3-pro",
        TaskComplexity.MEDIUM: "gemini-3-pro",
        TaskComplexity.COMPLEX: "gemini-3-pro",
    },
}
```

---

## KEY DIFFERENCES FROM PREVIOUS PLANS

### ❌ OLD PLAN (Wrong):
```
"Extend agents from BaseAgent"
"Inherit common functionality"
"Update base class"
```

### ✅ NEW PLAN (Correct):
```
"Create standalone agents"
"Copy Tilotma's pattern"
"No inheritance, no BaseAgent"
"Direct AI Router usage"
```

---

## TESTING STRATEGY

### Test Each Agent Independently

```python
# test_navya_adversarial.py
async def test_navya():
    navya = NavyaAdversarial(project_id="test")
    
    buggy_code = """
def calculate_price(quantity, price):
    return quantity / price  # Bug: should be *
"""
    
    result = await navya.review(buggy_code)
    
    assert result["bugs_found"] > 0
    assert "division" in str(result["details"]).lower()
    
    print(f"✅ NAVYA found {result['bugs_found']} bugs")
```

---

## FINAL CHECKLIST

### Before Starting
```
□ Tilotma working (standalone) ✅
□ Shubham working (standalone) ✅
□ AI Router working ✅
□ Understand standalone pattern ✅
□ No BaseAgent confusion ✅
```

### During Development
```
□ Each new agent is standalone
□ Copy Tilotma's structure
□ Direct AI Router usage
□ Test independently
□ No inheritance
```

### Before Demo
```
□ All 10 agents standalone
□ All agents tested individually
□ Integration tests passing
□ Real-time UI working
□ GCP automation via code only
```

---

## COST ESTIMATE (15 Days)

```
Development:
- Testing agents: ₹2,000
- GAN training: ₹3,000
- GCP testing: ₹1,500
Total: ₹6,500

Demo Day:
- Live demos: ₹2,500
- GCP hosting: ₹2,000
Total: ₹4,500

Grand Total: ₹11,000
```

---

**KEY TAKEAWAY:**

You've already done the hard architectural work (V2 standalone migration). Now just:

1. ✅ Use Tilotma and Shubham as they are (working)
2. ✅ Create 5 NEW standalone agents (copy pattern)
3. ✅ Add new task types to AI Router
4. ✅ Build real-time UI
5. ✅ GCP automation via code

**No BaseAgent. No inheritance. All standalone. ✅**

---

END OF CORRECTED PLAN
