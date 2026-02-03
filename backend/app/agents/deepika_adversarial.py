"""
DEEPIKA - Adversarial Performance Issue Detection Agent

Purpose: Hunt for performance bottlenecks aggressively (adversarial training)
Training Objective: MAXIMIZE(performance_issues_found)
Reward Function: +1 per performance issue, +2 for HIGH impact

Specializations:
- O(n²) or worse algorithmic complexity
- N+1 query problems
- Memory leaks
- Synchronous blocking in async code
- Missing database indexes
- Large file operations without streaming
- Excessive API calls
- Missing caching opportunities
- Inefficient loops and iterations
- Resource exhaustion vulnerabilities

Model: Claude Sonnet 4.5 (always)
"""

from typing import Dict, Any, List
import json
import re
import logging

# Adjust imports based on your project structure
from app.services.ai_router import ai_router, TaskComplexity


class DeepikaAdversarial:
    """
    Adversarial performance issue agent.
    
    Follows standalone V2 architecture - no BaseAgent inheritance.
    Uses AI Router directly for all AI operations.
    
    Usage:
        deepika = DeepikaAdversarial(project_id="proj-123")
        result = await deepika.review(code, file_type="python")
    """
    
    def __init__(self, project_id: str):
        """
        Initialize DEEPIKA agent.
        
        Args:
            project_id: Unique identifier for the project being reviewed
        """
        # Standalone - no inheritance
        self.project_id = project_id
        
        # Direct AI Router access
        # Uncomment when integrating with your backend
        self.ai_router = ai_router
        
        # Logging
        self.logger = logging.getLogger("agent.deepika_adversarial")
        self.logger.setLevel(logging.INFO)
        
        # Statistics tracking
        self.total_reviews = 0
        self.total_issues_found = 0
        self.high_impact_count = 0
        self.critical_impact_count = 0
    
    async def review(self, code: str, file_type: str = "python") -> Dict[str, Any]:
        """
        Hunt for performance issues aggressively.
        
        Args:
            code: Source code to review
            file_type: Type of code (python, javascript, typescript, etc.)
        
        Returns:
            Dict containing performance issues found
        """
        try:
            self.total_reviews += 1
            self.logger.info(f"⚡ Starting performance review #{self.total_reviews} for {file_type} code")
            
            # Build adversarial prompt
            prompt = self._build_adversarial_prompt(code, file_type)
            
            # Call AI Router
            # Uncomment when integrating
            response = await self.ai_router.generate(
                 messages=[{"role": "user", "content": prompt}],
                 task_type="adversarial_performance",
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
            issues_found = result.get("issues_found", 0)
            self.total_issues_found += issues_found
            
            # Count high and critical impact
            for detail in result.get("details", []):
                severity = detail.get("severity", "")
                if severity == "CRITICAL":
                    self.critical_impact_count += 1
                elif severity == "HIGH":
                    self.high_impact_count += 1
            
            self.logger.info(
                f"🎯 DEEPIKA found {issues_found} performance issues "
                f"(total: {self.total_issues_found}, "
                f"high: {self.high_impact_count}, critical: {self.critical_impact_count})"
            )
            
            return result
            
        except json.JSONDecodeError as e:
            self.logger.error(f"❌ Invalid JSON response: {e}")
            return self._error_response("Failed to parse AI response")
            
        except Exception as e:
            self.logger.error(f"❌ Performance review failed: {e}")
            raise
    
    def _build_adversarial_prompt(self, code: str, file_type: str) -> str:
        """Build aggressive adversarial prompt for performance issue hunting."""
        return f"""You are DEEPIKA, an adversarial performance issue detection agent.

YOUR ONLY GOAL: Find AS MANY performance bottlenecks as possible in this code.

REWARD SYSTEM:
- You get +2 points for CRITICAL issues (>500ms latency or >50% memory)
- You get +1 point for HIGH impact issues (>100ms latency or >20% memory)
- You get +0.5 points for MEDIUM issues
- Your reputation as a performance engineer depends on finding what others miss
- Think like a LOAD TESTER - how would this code fail at scale?

CODE TO ANALYZE:
```{file_type}
{code}
```

HUNT AGGRESSIVELY FOR:

1. **ALGORITHMIC COMPLEXITY (Big-O)** [CRITICAL]
   - O(n²) or worse when O(n log n) or O(n) is possible
   - Nested loops that can be optimized
   - Recursive algorithms without memoization
   - Example: Nested loops over same dataset
   - Benchmark: 1000 items = 1,000,000 operations

2. **N+1 QUERY PROBLEM** [CRITICAL]
   - Database query inside a loop
   - Missing eager loading / joins
   - Repeated identical queries
   - Example: for user in users: user.posts (queries in loop)
   - Impact: 100 users = 101 queries instead of 2

3. **MEMORY LEAKS** [CRITICAL]
   - Unclosed connections/files
   - Growing arrays never cleared
   - Event listeners not removed
   - Circular references
   - Cache without size limits

4. **BLOCKING OPERATIONS IN ASYNC** [HIGH]
   - Synchronous I/O in async functions
   - CPU-heavy operations blocking event loop
   - Missing await keywords
   - Blocking database calls
   - Impact: Entire server freezes

5. **MISSING DATABASE INDEXES** [HIGH]
   - Queries on unindexed columns
   - Full table scans
   - Missing composite indexes
   - Slow ORDER BY without index
   - Impact: 10ms → 5000ms with 1M rows

6. **NO STREAMING FOR LARGE DATA** [HIGH]
   - Loading entire file into memory
   - Reading all database rows at once
   - No pagination
   - Example: loading 10GB file with file.read()
   - Impact: Server OOM crash

7. **EXCESSIVE API CALLS** [MEDIUM]
   - API calls in loops
   - Missing batch operations
   - No request pooling
   - Redundant external requests
   - Impact: 100 calls instead of 1 batch

8. **MISSING CACHING** [MEDIUM]
   - Repeated expensive calculations
   - Static data fetched every request
   - Missing Redis/Memcached
   - No memoization
   - Impact: 500ms calculation on every request

9. **INEFFICIENT LOOPS** [MEDIUM]
   - Multiple passes over same data
   - Unnecessary operations in loop
   - String concatenation in loop (use join)
   - Recalculating invariants
   - Impact: 10x slower than optimized version

10. **RESOURCE EXHAUSTION** [HIGH]
    - Unbounded recursion
    - No rate limiting
    - No connection pooling
    - Thread/process leaks
    - Impact: Server crash under load

11. **INEFFICIENT DATA STRUCTURES** [MEDIUM]
    - Using list for lookups (use dict/set)
    - Unnecessary data copying
    - Wrong collection types
    - Impact: O(n) lookup vs O(1)

12. **MISSING LAZY LOADING** [LOW]
    - Eager loading unused data
    - Full object loading when only ID needed
    - Unnecessary JOIN operations

For EACH issue found, provide:
- Current performance (estimated)
- Optimized performance (estimated)
- Memory impact
- Scale impact (10x, 100x, 1000x data)
- Specific optimization with code

BE AGGRESSIVE. BENCHMARK EVERYTHING. FIND EVERY BOTTLENECK.

RESPOND IN VALID JSON (no markdown, no backticks):
{{
    "agent": "DEEPIKA",
    "issues_found": 5,
    "severity": ["CRITICAL", "HIGH", "HIGH", "MEDIUM", "LOW"],
    "details": [
        {{
            "file": "services/products.py",
            "line": 67,
            "code_snippet": "products = Product.query.all()",
            "issue": "Loading all products into memory - O(n) space complexity",
            "category": "memory_usage",
            "severity": "HIGH",
            "current_performance": "2.5s with 10,000 products",
            "optimized_performance": "0.1s with pagination",
            "memory_impact": "500MB RAM for 10,000 products",
            "scale_impact": "At 100,000 products: 5GB RAM, 25s load time → OOM crash",
            "fix_suggestion": "Use pagination with limit/offset or cursor-based pagination",
            "fix_code": "# OPTIMIZED VERSION\\nfrom sqlalchemy import select\\nproducts = session.query(Product).limit(100).offset(page*100).all()"
        }}
    ]
}}

IMPORTANT: Return ONLY valid JSON. No markdown formatting. No backticks."""

    def _parse_response(self, content: str) -> Dict[str, Any]:
        """Parse AI response into structured format."""
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # Try extracting JSON from markdown
            json_match = re.search(r'```json\n(.*?)\n```', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            json_match = re.search(r'```\n(.*?)\n```', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            raise ValueError(f"Could not parse response: {content[:200]}")
    
    def _error_response(self, error_message: str) -> Dict[str, Any]:
        """Return standardized error response."""
        return {
            "agent": "DEEPIKA",
            "issues_found": 0,
            "severity": [],
            "details": [],
            "error": error_message
        }
    
    def _mock_response(self, code: str) -> str:
        """Mock response for testing. Remove when integrating."""
        issues = []
        
        # Nested loops detection
        if code.count('for ') >= 2:
            issues.append({
                "file": "code.py",
                "line": 1,
                "code_snippet": "nested for loops",
                "issue": "O(n²) algorithmic complexity - nested loops",
                "category": "algorithmic_complexity",
                "severity": "CRITICAL",
                "current_performance": "1000 items = 1,000,000 operations",
                "optimized_performance": "1000 items = 1,000 operations",
                "memory_impact": "Minimal",
                "scale_impact": "10x data = 100x slower",
                "fix_suggestion": "Use hash map or set for O(1) lookups"
            })
        
        # Query in loop detection  
        if 'for ' in code and 'query' in code.lower():
            issues.append({
                "file": "code.py",
                "line": 2,
                "code_snippet": "query in loop",
                "issue": "N+1 query problem - database query in loop",
                "category": "n_plus_1",
                "severity": "CRITICAL",
                "current_performance": "100 users = 101 queries",
                "optimized_performance": "100 users = 2 queries",
                "memory_impact": "Moderate",
                "scale_impact": "Linear increase in DB load",
                "fix_suggestion": "Use eager loading or JOIN"
            })
        
        # All() without limit
        if '.all()' in code:
            issues.append({
                "file": "code.py",
                "line": 3,
                "code_snippet": ".all()",
                "issue": "Loading all rows without pagination",
                "category": "memory_usage",
                "severity": "HIGH",
                "current_performance": "2.5s for 10,000 rows",
                "optimized_performance": "0.1s with pagination",
                "memory_impact": "500MB for 10,000 rows",
                "scale_impact": "At 100,000 rows: OOM crash",
                "fix_suggestion": "Add pagination with limit/offset"
            })
        
        return json.dumps({
            "agent": "DEEPIKA",
            "issues_found": len(issues),
            "severity": [i["severity"] for i in issues],
            "details": issues
        })
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get agent performance statistics."""
        return {
            "total_reviews": self.total_reviews,
            "total_issues_found": self.total_issues_found,
            "critical_issues": self.critical_impact_count,
            "high_issues": self.high_impact_count,
            "average_issues_per_review": (
                self.total_issues_found / self.total_reviews 
                if self.total_reviews > 0 else 0
            )
        }


if __name__ == "__main__":
    import asyncio
    
    async def test():
        deepika = DeepikaAdversarial(project_id="test-perf-001")
        
        slow_code = """
def get_all_user_posts():
    users = User.query.all()  # No pagination
    result = []
    for user in users:
        posts = Post.query.filter_by(user_id=user.id).all()  # N+1 query
        for post in posts:
            # Nested loop - O(n²)
            comments = Comment.query.filter_by(post_id=post.id).all()
            result.append({
                'user': user,
                'post': post,
                'comments': comments
            })
    return result
"""
        
        result = await deepika.review(slow_code, "python")
        print(json.dumps(result, indent=2))
        print(f"\nStatistics: {deepika.get_statistics()}")
    
    asyncio.run(test())
