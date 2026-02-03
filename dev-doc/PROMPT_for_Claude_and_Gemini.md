# Master Prompt for Building NexSidi Agents
**Use this with Claude OR Gemini to build agents in parallel**

---

## CONTEXT

I'm building **NexSidi** - an AI software development platform where multiple AI agents work together to build, test, and deploy complete web applications.

**Current Status:**
- ✅ AI Router working (routes tasks to best AI model)
- ✅ Tilotma agent working (chat orchestrator)
- ✅ Shubham agent working (backend code generation)
- ✅ Database + Auth system working
- ✅ Using standalone V2 architecture (no BaseAgent inheritance)

**What I Need to Build:**
5 new standalone agents following the same pattern as Tilotma.

---

## ARCHITECTURE: STANDALONE V2

**Key Point:** Each agent is INDEPENDENT. No inheritance, no BaseAgent.

**Pattern (from existing Tilotma agent):**

```python
from app.services.ai_router import ai_router, TaskComplexity
import logging

class Tilotma:
    """Chat interface and orchestrator"""
    
    def __init__(self, project_id: str, user_id: str):
        # Standalone - no inheritance
        self.project_id = project_id
        self.user_id = user_id
        self.ai_router = ai_router
        self.logger = logging.getLogger("agent.tilotma")
    
    async def chat(self, message: str):
        """Main execution method"""
        try:
            response = await self.ai_router.generate(
                messages=[{"role": "user", "content": message}],
                task_type="chat",
                complexity=TaskComplexity.SIMPLE
            )
            
            self.logger.info(
                f"✅ {response.output_tokens} tokens, "
                f"₹{response.cost_estimate:.4f}"
            )
            
            return response.content
            
        except Exception as e:
            self.logger.error(f"❌ Chat failed: {e}")
            raise
```

---

## YOUR TASK

Build 5 new standalone agents using the EXACT same pattern as Tilotma above.

### Agent 1: NAVYA (Adversarial Logic Error Hunter)

**File:** `backend/app/agents/navya_adversarial.py`

**Purpose:** Find logic errors aggressively (adversarial training)

**Objective:** MAXIMIZE bugs found (gets rewarded for finding errors)

**Method signature:**
```python
async def review(self, code: str, file_type: str) -> dict
```

**What it hunts for:**
- Division by zero
- Null pointer errors
- Off-by-one errors
- Race conditions
- Incorrect calculations
- Missing edge case handling
- Type mismatches
- Unreachable code

**Response format:**
```json
{
    "agent": "NAVYA",
    "bugs_found": 5,
    "severity": ["CRITICAL", "HIGH", "MEDIUM", "LOW", "LOW"],
    "details": [
        {
            "file": "routes/products.py",
            "line": 45,
            "issue": "Division by zero if quantity is 0",
            "severity": "CRITICAL",
            "fix_suggestion": "Add validation: if quantity == 0: raise ValueError"
        }
    ]
}
```

**AI Router task_type:** `"adversarial_logic"`  
**Model:** Claude Sonnet 4.5 (always)  
**Complexity:** COMPLEX

---

### Agent 2: KARAN (Adversarial Security Hunter)

**File:** `backend/app/agents/karan_adversarial.py`

**Purpose:** Find security vulnerabilities aggressively

**Objective:** MAXIMIZE security holes found

**Method signature:**
```python
async def review(self, code: str, file_type: str) -> dict
```

**What it hunts for:**
- SQL injection (raw queries with user input)
- XSS (Cross-site scripting)
- CSRF attacks
- Insecure deserialization
- Hardcoded credentials
- Weak encryption
- Missing authentication
- Path traversal vulnerabilities
- Insecure file uploads
- Missing CORS configuration

**Response format:**
```json
{
    "agent": "KARAN",
    "vulnerabilities_found": 3,
    "severity": ["CRITICAL", "HIGH", "MEDIUM"],
    "details": [
        {
            "file": "routes/users.py",
            "line": 23,
            "issue": "SQL injection via raw query",
            "cve_reference": "CWE-89",
            "severity": "CRITICAL",
            "exploit_example": "email='; DROP TABLE users; --",
            "fix_suggestion": "Use parameterized queries with SQLAlchemy"
        }
    ]
}
```

**AI Router task_type:** `"adversarial_security"`  
**Model:** Claude Sonnet 4.5 (always)  
**Complexity:** COMPLEX

---

### Agent 3: DEEPIKA (Adversarial Performance Hunter)

**File:** `backend/app/agents/deepika_adversarial.py`

**Purpose:** Find performance issues aggressively

**Objective:** MAXIMIZE performance problems found

**Method signature:**
```python
async def review(self, code: str, file_type: str) -> dict
```

**What it hunts for:**
- O(n²) or worse algorithms
- N+1 query problems
- Memory leaks
- Synchronous blocking in async code
- Missing database indexes
- Large file operations without streaming
- Excessive API calls
- Missing caching
- Inefficient loops
- Resource exhaustion risks

**Response format:**
```json
{
    "agent": "DEEPIKA",
    "issues_found": 2,
    "severity": ["HIGH", "MEDIUM"],
    "details": [
        {
            "file": "services/products.py",
            "line": 67,
            "issue": "Loading all products into memory (O(n) space)",
            "impact": "With 10,000 products = 500MB RAM",
            "severity": "HIGH",
            "benchmark": "Current: 2.5s, Optimal: 0.1s",
            "fix_suggestion": "Use pagination with limit/offset"
        }
    ]
}
```

**AI Router task_type:** `"adversarial_performance"`  
**Model:** Claude Sonnet 4.5 (always)  
**Complexity:** COMPLEX

---

### Agent 4: AARAV (Browser Testing Agent)

**File:** `backend/app/agents/aarav_testing.py`

**Purpose:** Test websites in real browser like a human would

**Technology:** Playwright (browser automation)

**Method signature:**
```python
async def test_website(self, url: str) -> dict
```

**What it tests:**
- Click all buttons
- Fill all forms
- Test navigation
- Test on multiple screen sizes (320px, 768px, 1920px)
- Capture screenshots
- Check for broken links
- Test error handling
- Verify responsive design

**Response format:**
```json
{
    "agent": "AARAV",
    "tests_run": 45,
    "tests_passed": 42,
    "tests_failed": 3,
    "failures": [
        {
            "test": "Mobile menu close button",
            "issue": "Button doesn't close menu on click",
            "screenshot": "screenshot_mobile_menu.png"
        }
    ]
}
```

**Implementation:**
```python
from playwright.async_api import async_playwright

async def test_website(self, url: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        await page.goto(url)
        
        # Test scenarios
        # Click all buttons
        # Fill forms
        # Test mobile responsive
        
        await page.screenshot(path="test_result.png")
        await browser.close()
```

**AI Router task_type:** `"browser_testing"`  
**Model:** Gemini 3 Flash  
**Complexity:** MEDIUM

---

### Agent 5: BRAND AGENT (Design Uniqueness Evaluator)

**File:** `backend/app/agents/brand_agent.py`

**Purpose:** Ensure designs are unique and clear (not generic templates)

**Method signature:**
```python
async def evaluate(self, design_html: str, business_description: str) -> dict
```

**Evaluation criteria:**

1. **Instant Clarity (5-second test):** Score 0-10
   - Can visitor understand business in 5 seconds?
   
2. **Uniqueness (not generic):** Score 0-10
   - Does it look like template?
   - Does it tell business story?
   
3. **Emotional Connection:** Score 0-10
   - Does it create trust?
   - Does it show personality?
   
4. **Value Proposition:** Score 0-10
   - Is unique value clear?
   - Would customer choose this?

**Minimum pass score:** 35/40

**Response format:**
```json
{
    "agent": "BRAND_AGENT",
    "overall_score": 37,
    "instant_clarity": 9,
    "uniqueness": 8,
    "emotional_connection": 10,
    "value_proposition": 10,
    "passed": true,
    "feedback": "Strong brand identity. Clear value prop: 'Fresh groceries in 30 min since 1985'",
    "improvements": [
        "Add more visual storytelling",
        "Enhance color contrast for readability"
    ]
}
```

**AI Router task_type:** `"brand_evaluation"`  
**Model:** Gemini 3 Pro  
**Complexity:** MEDIUM

---

## AI ROUTER INTERFACE

Your agents will call this to interact with AI models:

```python
# Available via: from app.services.ai_router import ai_router, TaskComplexity

# Generate AI response
response = await ai_router.generate(
    messages=[{"role": "user", "content": "your prompt"}],
    task_type="adversarial_logic",  # or other task type
    complexity=TaskComplexity.COMPLEX,
    max_tokens=2000  # optional
)

# Response object has:
response.content           # AI's response text
response.model_id          # Which model was used
response.input_tokens      # Tokens used for input
response.output_tokens     # Tokens used for output
response.cost_estimate     # Cost in ₹
response.finish_reason     # "stop" or "length"
```

**TaskComplexity options:**
- `TaskComplexity.SIMPLE`
- `TaskComplexity.MEDIUM`
- `TaskComplexity.COMPLEX`
- `TaskComplexity.MOST_COMPLEX`

---

## REQUIREMENTS FOR ALL AGENTS

### 1. Follow Tilotma's Pattern EXACTLY

```python
class YourAgent:
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.ai_router = ai_router
        self.logger = logging.getLogger(f"agent.{self.__class__.__name__}")
    
    async def main_method(self, input_data):
        try:
            # Build prompt
            prompt = self._build_prompt(input_data)
            
            # Call AI Router
            response = await self.ai_router.generate(
                messages=[{"role": "user", "content": prompt}],
                task_type="your_task_type",
                complexity=TaskComplexity.COMPLEX
            )
            
            # Log cost
            self.logger.info(
                f"✅ {response.output_tokens} tokens, "
                f"₹{response.cost_estimate:.4f}"
            )
            
            # Parse and return
            return self._parse_response(response.content)
            
        except Exception as e:
            self.logger.error(f"❌ Failed: {e}")
            raise
```

### 2. Comprehensive Docstrings

```python
class NavyaAdversarial:
    """
    Adversarial logic error agent.
    
    Purpose: Hunt for logic errors aggressively
    Training Objective: MAXIMIZE(logical_errors_found)
    Reward Function: +1 per logic bug detected
    
    Specializations:
    - Type inconsistencies
    - Null reference errors
    - Off-by-one errors
    - Race conditions
    - Incorrect calculations
    
    Usage:
        navya = NavyaAdversarial(project_id="123")
        result = await navya.review(code, file_type="python")
    """
```

### 3. Proper Error Handling

```python
try:
    response = await self.ai_router.generate(...)
    return self._parse_response(response.content)
except json.JSONDecodeError as e:
    self.logger.error(f"❌ Invalid JSON response: {e}")
    # Return default response or retry
except Exception as e:
    self.logger.error(f"❌ Unexpected error: {e}")
    raise
```

### 4. Response Parsing

```python
def _parse_response(self, content: str) -> dict:
    """Parse AI response into structured format"""
    try:
        # Try JSON first
        return json.loads(content)
    except:
        # Fallback: Extract JSON from markdown
        import re
        json_match = re.search(r'```json\n(.*?)\n```', content, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(1))
        raise ValueError("Could not parse response")
```

### 5. Logging Standards

```python
self.logger.info(f"✅ Success message")
self.logger.warning(f"⚠️ Warning message")
self.logger.error(f"❌ Error message")
```

---

## TESTING EACH AGENT

Create test file for each agent:

```python
# backend/app/tests/test_navya_adversarial.py

import asyncio
from app.agents.navya_adversarial import NavyaAdversarial

async def test_navya():
    """Test NAVYA finds logic errors"""
    
    navya = NavyaAdversarial(project_id="test-123")
    
    # Buggy code sample
    buggy_code = """
def calculate_total(quantity, price):
    return quantity / price  # Bug: should be *
    
def get_user(user_id):
    users = []
    return users[user_id]  # Bug: index out of range
"""
    
    # Test review
    result = await navya.review(buggy_code, "python")
    
    # Assertions
    assert result["bugs_found"] > 0, "Should find bugs"
    assert "division" in str(result).lower() or "multiply" in str(result).lower()
    
    print(f"✅ NAVYA found {result['bugs_found']} bugs")
    print(f"Details: {result['details']}")

if __name__ == "__main__":
    asyncio.run(test_navya())
```

---

## ADVERSARIAL PROMPTS (Critical!)

The adversarial agents need AGGRESSIVE prompts:

### Example for NAVYA:

```python
prompt = f"""You are NAVYA, an adversarial logic error detection agent.

YOUR ONLY GOAL: Find AS MANY logic errors as possible in this code.

REWARD SYSTEM:
- You get +1 point for EVERY bug found
- The more bugs you find, the better your score
- Your reputation depends on finding errors others miss

CODE TO ANALYZE:
```{file_type}
{code}
```

HUNT AGGRESSIVELY FOR:
1. Division by zero (check all / operations)
2. Null/None reference errors (accessing properties on None)
3. Index out of bounds (array/list access)
4. Type mismatches (string + int, etc.)
5. Off-by-one errors (loops, ranges)
6. Race conditions (concurrent access)
7. Logic inversions (if x when should be if not x)
8. Missing edge cases (empty input, negative numbers, etc.)

BE RUTHLESS. BE THOROUGH. FIND EVERY BUG.

RESPOND IN JSON:
{{
    "bugs_found": 5,
    "severity": ["CRITICAL", "HIGH", "MEDIUM", "LOW", "LOW"],
    "details": [
        {{
            "file": "filename.py",
            "line": 45,
            "issue": "Clear description of the bug",
            "severity": "CRITICAL",
            "fix_suggestion": "Specific fix"
        }}
    ]
}}
"""
```

---

## COMPETITION SYSTEM (Bonus Task)

After building all 3 adversarial agents, create competition system:

```python
# backend/app/services/adversarial_competition.py

class AdversarialCompetition:
    """Run 3 adversarial agents in competition"""
    
    async def compete(self, code: str, file_type: str):
        """Run all 3 agents in parallel, determine winner"""
        
        # Run in parallel
        navya_task = navya.review(code, file_type)
        karan_task = karan.review(code, file_type)
        deepika_task = deepika.review(code, file_type)
        
        navya_result, karan_result, deepika_result = await asyncio.gather(
            navya_task, karan_task, deepika_task
        )
        
        # Count bugs
        navya_bugs = navya_result["bugs_found"]
        karan_bugs = karan_result["vulnerabilities_found"]
        deepika_bugs = deepika_result["issues_found"]
        
        # Determine winner
        scores = {
            "NAVYA": navya_bugs,
            "KARAN": karan_bugs,
            "DEEPIKA": deepika_bugs
        }
        winner = max(scores, key=scores.get)
        
        return {
            "winner": winner,
            "scores": scores,
            "total_bugs": navya_bugs + karan_bugs + deepika_bugs,
            "navya_details": navya_result,
            "karan_details": karan_result,
            "deepika_details": deepika_result
        }
```

---

## DELIVERABLES

For each agent, provide:

1. **Complete agent file** (navya_adversarial.py, etc.)
2. **Test file** (test_navya_adversarial.py)
3. **Brief explanation** of key design decisions

---

## SUCCESS CRITERIA

Your agents should:

✅ Follow Tilotma's standalone pattern exactly
✅ Use AI Router for all AI calls
✅ Return structured JSON responses
✅ Have comprehensive error handling
✅ Include detailed logging
✅ Pass basic tests
✅ Be production-ready (not just proof-of-concept)

---

## COMPARISON METRICS

I'll compare Claude vs Gemini versions on:

1. **Code Quality**
   - Structure and organization
   - Error handling
   - Documentation quality

2. **Bug Detection Accuracy**
   - Do adversarial agents find real bugs?
   - False positive rate
   - Severity assessment accuracy

3. **Prompt Effectiveness**
   - Do aggressive prompts work?
   - JSON response consistency
   - Handling edge cases

4. **Performance**
   - Token usage
   - Response time
   - Cost efficiency

---

## ADDITIONAL CONTEXT

**Project Structure:**
```
backend/
├── app/
│   ├── agents/
│   │   ├── tilotma.py              (✅ existing)
│   │   ├── shubham.py              (✅ existing)
│   │   ├── navya_adversarial.py    (❌ build this)
│   │   ├── karan_adversarial.py    (❌ build this)
│   │   ├── deepika_adversarial.py  (❌ build this)
│   │   ├── aarav_testing.py        (❌ build this)
│   │   └── brand_agent.py          (❌ build this)
│   ├── services/
│   │   └── ai_router.py            (✅ existing)
│   └── tests/
│       └── test_*.py               (❌ build tests)
```

**Target Demo:** India AI Summit (Feb 11-15, 2026)
**Timeline:** 15 days
**Budget:** ₹11K total

---

## START HERE

Begin with **Agent 1 (NAVYA)** - it's the most critical for demonstrating adversarial competition.

Once NAVYA works, the other adversarial agents (KARAN, DEEPIKA) follow the same pattern.

Good luck! 🚀

---

**Questions? Ask me and I'll clarify any part of the requirements.**
