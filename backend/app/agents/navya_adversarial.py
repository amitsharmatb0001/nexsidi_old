"""
NAVYA - Adversarial Logic Error Detection Agent

Purpose: Hunt for logic errors aggressively (adversarial training)
Training Objective: MAXIMIZE(logical_errors_found)
Reward Function: +1 per logic bug detected

Specializations:
- Division by zero vulnerabilities
- Null/None reference errors
- Off-by-one errors in loops and indexes
- Race conditions in async code
- Type mismatches and incorrect calculations
- Missing edge case handling
- Unreachable code detection

Model: Claude Sonnet 4.5 (always)
"""

from typing import Dict, Any, List
import json
import re
import logging

# AI Router integration
from app.services.ai_router import ai_router, TaskComplexity


class NavyaAdversarial:
    """
    Adversarial logic error agent.
    
    Follows standalone V2 architecture - no BaseAgent inheritance.
    Uses AI Router directly for all AI operations.
    
    Usage:
        navya = NavyaAdversarial(project_id="proj-123")
        result = await navya.review(code, file_type="python")
    """
    
    def __init__(self, project_id: str):
        """
        Initialize NAVYA agent.
        
        Args:
            project_id: Unique identifier for the project being reviewed
        """
        # Standalone - no inheritance
        self.project_id = project_id
        
        # Direct AI Router access
        self.ai_router = ai_router
        
        # Logging
        self.logger = logging.getLogger("agent.navya_adversarial")
        self.logger.setLevel(logging.INFO)
        
        # Statistics tracking
        self.total_reviews = 0
        self.total_bugs_found = 0
    
    async def review(self, code: str, file_type: str = "python") -> Dict[str, Any]:
        """
        Hunt for logic errors aggressively.
        
        This is the main execution method. It sends code to Claude Sonnet 4.5
        with an adversarial prompt designed to maximize bug detection.
        
        Args:
            code: Source code to review
            file_type: Type of code (python, javascript, typescript, etc.)
        
        Returns:
            Dict containing:
                - agent: "NAVYA"
                - bugs_found: int count of bugs
                - severity: List of severity levels
                - details: List of bug details with line numbers and fixes
        
        Example:
            {
                "agent": "NAVYA",
                "bugs_found": 3,
                "severity": ["CRITICAL", "HIGH", "MEDIUM"],
                "details": [...]
            }
        """
        try:
            self.total_reviews += 1
            self.logger.info(f"🔍 Starting review #{self.total_reviews} for {file_type} code")
            
            # Build adversarial prompt
            prompt = self._build_adversarial_prompt(code, file_type)
            
            # Call AI Router with adversarial_logic task type
            response = await self.ai_router.generate(
                messages=[{"role": "user", "content": prompt}],
                task_type="adversarial_logic",
                complexity=TaskComplexity.COMPLEX
            )
            
            # Log cost
            self.logger.info(
                f"✅ {response.output_tokens} tokens, "
                f"₹{response.cost_estimate:.4f}"
            )
            
            # Parse and validate response
            result = self._parse_response(response.content)
            
            # Update statistics
            bugs_found = result.get("bugs_found", 0)
            self.total_bugs_found += bugs_found
            
            self.logger.info(
                f"🎯 NAVYA found {bugs_found} logic errors "
                f"(total: {self.total_bugs_found} bugs across {self.total_reviews} reviews)"
            )
            
            return result
            
        except json.JSONDecodeError as e:
            self.logger.error(f"❌ Invalid JSON response: {e}")
            return self._error_response("Failed to parse AI response")
            
        except Exception as e:
            self.logger.error(f"❌ Review failed: {e}")
            raise
    
    def _build_adversarial_prompt(self, code: str, file_type: str) -> str:
        """
        Build aggressive adversarial prompt for bug hunting.
        
        The prompt is designed to maximize bug detection by:
        1. Setting up a reward system (gamification)
        2. Providing specific bug categories to hunt for
        3. Using aggressive language ("RUTHLESS", "HUNT", "FIND EVERY BUG")
        4. Requesting structured JSON output
        """
        return f"""You are NAVYA, an adversarial logic error detection agent.

YOUR ONLY GOAL: Find AS MANY logic errors as possible in this code.

REWARD SYSTEM:
- You get +1 point for EVERY bug found
- You get +2 points for CRITICAL bugs
- The more bugs you find, the better your score
- Your reputation depends on finding errors others miss
- Be RUTHLESS and THOROUGH

CODE TO ANALYZE:
```{file_type}
{code}
```

HUNT AGGRESSIVELY FOR:

1. **Division Operations** (CRITICAL)
   - Division by zero (check ALL / and % operations)
   - Division without zero checks
   - Integer division truncation issues

2. **Null/None References** (CRITICAL)
   - Accessing properties on None/null
   - Missing null checks before access
   - Optional chaining violations

3. **Array/List Access** (HIGH)
   - Index out of bounds
   - Negative index without validation
   - Empty list access
   - Off-by-one errors in loops

4. **Type Mismatches** (HIGH)
   - String concatenation with numbers
   - Implicit type conversions
   - Type inconsistencies in conditionals

5. **Logic Inversions** (MEDIUM)
   - Inverted conditionals (if x when should be if not x)
   - Negation errors
   - Boolean logic mistakes

6. **Race Conditions** (HIGH for async code)
   - Concurrent access to shared state
   - Missing locks/semaphores
   - Async/await misuse

7. **Edge Cases** (MEDIUM)
   - Empty input handling
   - Negative numbers
   - Zero values
   - Boundary conditions

8. **Unreachable Code** (LOW)
   - Code after return statements
   - Dead branches in conditionals

9. **Incorrect Calculations** (HIGH)
   - Wrong operators (* vs /)
   - Order of operations errors
   - Incorrect formulas

10. **Resource Management** (MEDIUM)
    - Unclosed files/connections
    - Memory leaks
    - Missing cleanup in error paths

BE PARANOID. ASSUME THE WORST. FIND EVERY BUG.

RESPOND IN VALID JSON (no markdown, no backticks):
{{
    "agent": "NAVYA",
    "bugs_found": 5,
    "severity": ["CRITICAL", "HIGH", "MEDIUM", "LOW", "LOW"],
    "details": [
        {{
            "file": "main.py",
            "line": 45,
            "code_snippet": "result = a / b",
            "issue": "Division by zero if b equals 0",
            "severity": "CRITICAL",
            "category": "division_by_zero",
            "fix_suggestion": "Add validation: if b == 0: raise ValueError('Division by zero')"
        }}
    ]
}}

IMPORTANT: Return ONLY valid JSON. No markdown formatting. No backticks."""

    def _parse_response(self, content: str) -> Dict[str, Any]:
        """
        Parse AI response into structured format.
        
        Handles multiple response formats:
        1. Direct JSON
        2. JSON wrapped in markdown code blocks
        3. Malformed responses (returns error format)
        
        Returns:
            Structured dict with bugs_found and details
        """
        try:
            # Try direct JSON parse first
            return json.loads(content)
            
        except json.JSONDecodeError:
            # Try extracting JSON from markdown code blocks
            json_match = re.search(r'```json\n(.*?)\n```', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            
            # Try without json marker
            json_match = re.search(r'```\n(.*?)\n```', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            
            # Last resort: try to find JSON object in text
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            
            raise ValueError(f"Could not parse response as JSON: {content[:200]}")
    
    def _error_response(self, error_message: str) -> Dict[str, Any]:
        """
        Return standardized error response.
        
        Args:
            error_message: Description of the error
            
        Returns:
            Dict in standard format with error indication
        """
        return {
            "agent": "NAVYA",
            "bugs_found": 0,
            "severity": [],
            "details": [],
            "error": error_message
        }
    

    
    def get_statistics(self) -> Dict[str, int]:
        """
        Get agent performance statistics.
        
        Returns:
            Dict with total_reviews and total_bugs_found
        """
        return {
            "total_reviews": self.total_reviews,
            "total_bugs_found": self.total_bugs_found,
            "average_bugs_per_review": (
                self.total_bugs_found / self.total_reviews 
                if self.total_reviews > 0 else 0
            )
        }


# Standalone execution for testing
if __name__ == "__main__":
    import asyncio
    
    async def test():
        navya = NavyaAdversarial(project_id="test-123")
        
        buggy_code = """
def calculate_total(quantity, price):
    return quantity / price  # Bug: division by zero if price=0
    
def get_user(user_id):
    users = []
    return users[user_id]  # Bug: index out of range

def process_data(data):
    result = data + 5  # Bug: type mismatch if data is string
    return result
"""
        
        result = await navya.review(buggy_code, "python")
        print(json.dumps(result, indent=2))
        print(f"\nStatistics: {navya.get_statistics()}")
    
    asyncio.run(test())
