"""
KARAN - Adversarial Security Vulnerability Detection Agent

Purpose: Hunt for security vulnerabilities aggressively (adversarial training)
Training Objective: MAXIMIZE(security_holes_found)
Reward Function: +1 per vulnerability detected, +2 for CRITICAL

Specializations:
- SQL Injection vulnerabilities
- Cross-Site Scripting (XSS)
- CSRF attacks
- Insecure deserialization
- Hardcoded credentials
- Weak encryption
- Missing authentication/authorization
- Path traversal vulnerabilities
- Insecure file uploads
- Missing CORS configuration

Model: Claude Sonnet 4.5 (always)
"""

from typing import Dict, Any, List
import json
import re
import logging

# Adjust imports based on your project structure
from app.services.ai_router import ai_router, TaskComplexity


class KaranAdversarial:
    """
    Adversarial security vulnerability agent.
    
    Follows standalone V2 architecture - no BaseAgent inheritance.
    Uses AI Router directly for all AI operations.
    
    Usage:
        karan = KaranAdversarial(project_id="proj-123")
        result = await karan.review(code, file_type="python")
    """
    
    def __init__(self, project_id: str):
        """
        Initialize KARAN agent.
        
        Args:
            project_id: Unique identifier for the project being reviewed
        """
        # Standalone - no inheritance
        self.project_id = project_id
        
        # Direct AI Router access
        self.ai_router = ai_router
        
        # Logging
        self.logger = logging.getLogger("agent.karan_adversarial")
        self.logger.setLevel(logging.INFO)
        
        # Statistics tracking
        self.total_reviews = 0
        self.total_vulnerabilities_found = 0
        self.critical_count = 0
        self.high_count = 0
    
    async def review(self, code: str, file_type: str = "python") -> Dict[str, Any]:
        """
        Hunt for security vulnerabilities aggressively.
        
        This is the main execution method. It sends code to Claude Sonnet 4.5
        with an adversarial prompt designed to maximize vulnerability detection.
        
        Args:
            code: Source code to review
            file_type: Type of code (python, javascript, typescript, etc.)
        
        Returns:
            Dict containing:
                - agent: "KARAN"
                - vulnerabilities_found: int count of vulnerabilities
                - severity: List of severity levels
                - details: List of vulnerability details with CVE references
        
        Example:
            {
                "agent": "KARAN",
                "vulnerabilities_found": 4,
                "severity": ["CRITICAL", "CRITICAL", "HIGH", "MEDIUM"],
                "details": [...]
            }
        """
        try:
            self.total_reviews += 1
            self.logger.info(f"🔒 Starting security review #{self.total_reviews} for {file_type} code")
            
            # Build adversarial prompt
            prompt = self._build_adversarial_prompt(code, file_type)
            
            # Call AI Router
            # Uncomment when integrating
            response = await self.ai_router.generate(
                messages=[{"role": "user", "content": prompt}],
                task_type="adversarial_security",
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
            vulns_found = result.get("vulnerabilities_found", 0)
            self.total_vulnerabilities_found += vulns_found
            
            # Count critical and high severity
            for detail in result.get("details", []):
                if detail.get("severity") == "CRITICAL":
                    self.critical_count += 1
                elif detail.get("severity") == "HIGH":
                    self.high_count += 1
            
            self.logger.info(
                f"🎯 KARAN found {vulns_found} vulnerabilities "
                f"(total: {self.total_vulnerabilities_found}, "
                f"critical: {self.critical_count}, high: {self.high_count})"
            )
            
            return result
            
        except json.JSONDecodeError as e:
            self.logger.error(f"❌ Invalid JSON response: {e}")
            return self._error_response("Failed to parse AI response")
            
        except Exception as e:
            self.logger.error(f"❌ Security review failed: {e}")
            raise
    
    def _build_adversarial_prompt(self, code: str, file_type: str) -> str:
        """
        Build aggressive adversarial prompt for security vulnerability hunting.
        
        The prompt is designed to maximize vulnerability detection by:
        1. Setting up a reward system with higher rewards for critical vulns
        2. Providing comprehensive security checklist with CVE references
        3. Using aggressive security researcher mindset
        4. Requesting structured JSON output with exploit examples
        """
        return f"""You are KARAN, an adversarial security vulnerability detection agent.

YOUR ONLY GOAL: Find AS MANY security vulnerabilities as possible in this code.

REWARD SYSTEM:
- You get +2 points for EVERY CRITICAL vulnerability
- You get +1 point for HIGH vulnerabilities
- You get +0.5 points for MEDIUM vulnerabilities
- Your reputation as a security researcher depends on finding what others miss
- Think like a HACKER - how would you exploit this code?

CODE TO ANALYZE:
```{file_type}
{code}
```

HUNT AGGRESSIVELY FOR:

1. **SQL INJECTION (CWE-89)** [CRITICAL]
   - Raw SQL queries with user input
   - String concatenation in queries
   - Missing parameterization
   - ORM misuse allowing injection
   - Example exploit: `'; DROP TABLE users; --`

2. **CROSS-SITE SCRIPTING - XSS (CWE-79)** [CRITICAL]
   - Unescaped user input in HTML
   - innerHTML with user data
   - Missing Content Security Policy
   - Reflected XSS, Stored XSS, DOM XSS
   - Example exploit: `<script>alert(document.cookie)</script>`

3. **AUTHENTICATION BYPASS (CWE-287)** [CRITICAL]
   - Missing authentication checks
   - Weak password validation
   - Hardcoded credentials
   - Session fixation vulnerabilities
   - JWT token misuse

4. **AUTHORIZATION FLAWS (CWE-285)** [CRITICAL]
   - Missing permission checks
   - Insecure Direct Object References (IDOR)
   - Privilege escalation paths
   - Role-based access control failures

5. **CSRF - Cross-Site Request Forgery (CWE-352)** [HIGH]
   - Missing CSRF tokens
   - State-changing GET requests
   - Missing SameSite cookie attributes

6. **INSECURE DESERIALIZATION (CWE-502)** [CRITICAL]
   - Pickle usage with untrusted data (Python)
   - eval() or exec() with user input
   - YAML.load without safe_load
   - JSON parsing vulnerabilities

7. **PATH TRAVERSAL (CWE-22)** [HIGH]
   - File operations with user-controlled paths
   - Missing path sanitization
   - Directory traversal attacks
   - Example exploit: `../../etc/passwd`

8. **WEAK CRYPTOGRAPHY (CWE-327)** [HIGH]
   - MD5 or SHA1 for passwords
   - Hardcoded encryption keys
   - Missing salt in hashing
   - Weak random number generation

9. **SENSITIVE DATA EXPOSURE (CWE-200)** [HIGH]
   - Passwords in logs
   - API keys in code
   - Verbose error messages
   - Debug mode in production

10. **INSECURE FILE UPLOAD (CWE-434)** [CRITICAL]
    - No file type validation
    - Missing size limits
    - Executable files allowed
    - Path traversal in filenames

11. **XML EXTERNAL ENTITY - XXE (CWE-611)** [CRITICAL]
    - XML parsing without disabling external entities
    - SOAP/XML vulnerabilities

12. **SERVER-SIDE REQUEST FORGERY - SSRF (CWE-918)** [HIGH]
    - User-controlled URLs in requests
    - Missing URL validation
    - Internal network access

13. **MISSING RATE LIMITING (CWE-770)** [MEDIUM]
    - No rate limits on sensitive endpoints
    - Brute force vulnerabilities
    - Resource exhaustion

14. **CORS MISCONFIGURATION (CWE-942)** [MEDIUM]
    - Access-Control-Allow-Origin: *
    - Missing credential restrictions
    - Overly permissive CORS

15. **REGEX DENIAL OF SERVICE - ReDoS (CWE-1333)** [MEDIUM]
    - Catastrophic backtracking patterns
    - User input in regex

BE PARANOID. THINK LIKE AN ATTACKER. FIND EVERY VULNERABILITY.

For EACH vulnerability found, provide:
- CVE/CWE reference
- Real exploit example
- Impact assessment
- Specific fix with code example

RESPOND IN VALID JSON (no markdown, no backticks):
{{
    "agent": "KARAN",
    "vulnerabilities_found": 5,
    "severity": ["CRITICAL", "CRITICAL", "HIGH", "MEDIUM", "LOW"],
    "details": [
        {{
            "file": "routes/users.py",
            "line": 23,
            "code_snippet": "query = f'SELECT * FROM users WHERE email = {{email}}'",
            "issue": "SQL injection vulnerability via string interpolation",
            "cve_reference": "CWE-89",
            "severity": "CRITICAL",
            "category": "sql_injection",
            "exploit_example": "email='; DROP TABLE users; --",
            "impact": "Complete database compromise, data loss",
            "fix_suggestion": "Use parameterized queries: session.query(User).filter(User.email == email)",
            "fix_code": "# SECURE VERSION\\nfrom sqlalchemy import select\\nstmt = select(User).where(User.email == email)\\nresult = session.execute(stmt)"
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
        """Return standardized error response."""
        return {
            "agent": "KARAN",
            "vulnerabilities_found": 0,
            "severity": [],
            "details": [],
            "error": error_message
        }
    
    def _mock_response(self, code: str) -> str:
        """
        Generate mock response for testing without AI Router.
        Remove this method when integrating with actual backend.
        """
        vulns = []
        
        # SQL Injection detection
        if any(pattern in code.lower() for pattern in ['select', 'insert', 'update', 'delete', 'f"', "f'"]):
            vulns.append({
                "file": "code.py",
                "line": 1,
                "code_snippet": "SQL query with string formatting",
                "issue": "Potential SQL injection via string interpolation",
                "cve_reference": "CWE-89",
                "severity": "CRITICAL",
                "category": "sql_injection",
                "exploit_example": "'; DROP TABLE users; --",
                "impact": "Database compromise",
                "fix_suggestion": "Use parameterized queries"
            })
        
        # XSS detection
        if any(pattern in code.lower() for pattern in ['<script', 'innerhtml', 'dangerouslysetinnerhtml']):
            vulns.append({
                "file": "code.py",
                "line": 2,
                "code_snippet": "innerHTML with user input",
                "issue": "Cross-Site Scripting (XSS) vulnerability",
                "cve_reference": "CWE-79",
                "severity": "CRITICAL",
                "category": "xss",
                "exploit_example": "<script>alert(document.cookie)</script>",
                "impact": "Session hijacking, data theft",
                "fix_suggestion": "Use textContent or sanitize input"
            })
        
        # Hardcoded credentials
        if any(pattern in code.lower() for pattern in ['password', 'secret', 'api_key', 'token']):
            vulns.append({
                "file": "code.py",
                "line": 3,
                "code_snippet": "Hardcoded credential",
                "issue": "Hardcoded sensitive credential",
                "cve_reference": "CWE-798",
                "severity": "HIGH",
                "category": "hardcoded_credentials",
                "exploit_example": "N/A",
                "impact": "Credential exposure in source code",
                "fix_suggestion": "Use environment variables"
            })
        
        return json.dumps({
            "agent": "KARAN",
            "vulnerabilities_found": len(vulns),
            "severity": [v["severity"] for v in vulns],
            "details": vulns
        })
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get agent performance statistics."""
        return {
            "total_reviews": self.total_reviews,
            "total_vulnerabilities_found": self.total_vulnerabilities_found,
            "critical_vulnerabilities": self.critical_count,
            "high_vulnerabilities": self.high_count,
            "average_vulns_per_review": (
                self.total_vulnerabilities_found / self.total_reviews 
                if self.total_reviews > 0 else 0
            )
        }


# Standalone execution for testing
if __name__ == "__main__":
    import asyncio
    
    async def test():
        karan = KaranAdversarial(project_id="test-sec-001")
        
        vulnerable_code = """
# SQL Injection
def get_user(email):
    query = f"SELECT * FROM users WHERE email = '{email}'"
    return db.execute(query)

# XSS
def display_message(message):
    return f"<div>{message}</div>"

# Hardcoded credentials
API_KEY = "sk_live_12345abcde"
PASSWORD = "admin123"

# Path traversal
def read_file(filename):
    return open(f"/uploads/{filename}").read()

# Missing authentication
@app.route('/admin/delete')
def delete_user():
    user_id = request.args.get('id')
    User.query.filter_by(id=user_id).delete()
"""
        
        result = await karan.review(vulnerable_code, "python")
        print(json.dumps(result, indent=2))
        print(f"\nStatistics: {karan.get_statistics()}")
    
    asyncio.run(test())
