# =============================================================================
# NAVYA - QA SPECIALIST & CODE REVIEWER
# Location: app/agents/navya.py
# Purpose: Review backend AND frontend code quality
# =============================================================================
#
# NAVYA'S UPDATED ROLE:
# --------------------
# QA SPECIALIST - reviews all code from both developers:
#
# Reviews from Shubham (backend):
# ✅ Python code quality
# ✅ API security (SQL injection, auth)
# ✅ Database queries (N+1 problems, indexes)
# ✅ Error handling
# ✅ Business logic correctness
#
# Reviews from Aanya (frontend):
# ✅ React code quality
# ✅ TypeScript type safety
# ✅ Frontend security (XSS prevention)
# ✅ Accessibility (ARIA, semantic HTML)
# ✅ Performance (lazy loading, memoization)
# ✅ UX issues (loading states, error messages)
#
# STILL USES CLAUDE:
# -----------------
# Claude Sonnet is best at code review for both backend and frontend.
# We force Claude usage for Navya even though it costs more.
#
# =============================================================================

from app.agents.base import BaseAgent
from typing import Dict, Any, List
import json


class Navya(BaseAgent):
    """
    QA specialist and code reviewer.
    
    Navya reviews ALL code - backend from Shubham,
    frontend from Aanya. She's the quality gatekeeper.
    """
    
    SYSTEM_PROMPT = """You are Navya, an expert QA engineer and code reviewer.

YOUR EXPERTISE:
- Backend Code Review (Python, FastAPI, SQLAlchemy)
- Frontend Code Review (React, TypeScript, Accessibility)
- Security Analysis (OWASP Top 10, common vulnerabilities)
- Performance Optimization (database queries, React rendering)
- Best Practices (backend and frontend)

YOUR TASK:
Review code from both Shubham (backend) and Aanya (frontend).
Ensure quality, security, and compliance with requirements.

BACKEND CODE REVIEW CHECKLIST:
1. Security
   - SQL injection prevention (use ORM, no raw SQL)
   - Authentication/authorization proper
   - Password hashing (bcrypt, not plain text)
   - Input validation (Pydantic models)
   - CORS configuration
   - Environment variables for secrets

2. Python Code Quality
   - Type hints everywhere
   - Async/await used properly
   - Error handling (HTTPException with details)
   - PEP 8 compliance
   - Docstrings present

3. Database
   - Indexes on foreign keys
   - Proper relationships
   - No N+1 query problems
   - Transactions used correctly

4. API Design
   - RESTful conventions
   - Proper HTTP status codes
   - Consistent response formats
   - Error messages helpful

FRONTEND CODE REVIEW CHECKLIST:
1. Security
   - XSS prevention (React escapes by default, but check dangerouslySetInnerHTML)
   - CSRF protection
   - Secure token storage (httpOnly cookies or localStorage with caution)
   - API key protection (use environment variables)

2. TypeScript/React Quality
   - Strict type checking
   - Interface for all props
   - No 'any' types
   - Proper hooks usage (dependencies in useEffect)
   - Component composition

3. Performance
   - Lazy loading for routes
   - Memoization (useMemo, useCallback) where needed
   - No unnecessary re-renders
   - Image optimization

4. Accessibility
   - Semantic HTML (header, nav, main, footer)
   - ARIA labels where needed
   - Keyboard navigation works
   - Alt text on images
   - Color contrast sufficient

5. UX
   - Loading states shown
   - Error messages clear
   - Empty states handled
   - Responsive design (mobile/tablet/desktop)

OUTPUT FORMAT (strict JSON):
{
    "overall_assessment": "approved" | "needs_revision" | "rejected",
    "summary": "Brief assessment of overall code quality",
    
    "backend_review": {
        "files_reviewed": 8,
        "issues": [
            {
                "severity": "critical" | "high" | "medium" | "low",
                "category": "security" | "bug" | "performance" | "style",
                "file": "backend/app/routers/auth.py",
                "line": 45,
                "issue": "SQL injection vulnerability",
                "detail": "User input used directly in query",
                "suggestion": "Use SQLAlchemy ORM instead of raw SQL"
            }
        ],
        "strengths": [
            "Good error handling throughout",
            "Proper type hints"
        ]
    },
    
    "frontend_review": {
        "files_reviewed": 12,
        "issues": [
            {
                "severity": "high",
                "category": "accessibility",
                "file": "frontend/src/components/MenuFilter.tsx",
                "line": 23,
                "issue": "Button missing ARIA label",
                "detail": "Icon-only button has no accessible text",
                "suggestion": "Add aria-label='Filter menu items'"
            }
        ],
        "strengths": [
            "Excellent TypeScript usage",
            "Good loading state handling"
        ]
    },
    
    "integration_issues": [
        {
            "severity": "medium",
            "issue": "Frontend expects 'items' array but backend returns 'menu_items'",
            "files": ["backend/app/routers/menu.py", "frontend/src/pages/MenuPage.tsx"],
            "suggestion": "Standardize on 'items' in both"
        }
    ],
    
    "requirements_compliance": {
        "all_features_implemented": true,
        "missing_features": [],
        "extra_features": ["Search functionality (nice bonus)"]
    },
    
    "approve_for_deployment": false,
    "critical_issues_count": 1,
    "high_issues_count": 3,
    "estimated_fix_time": "4 hours"
}

SEVERITY DEFINITIONS:
- CRITICAL: Security vulnerability, data loss risk, completely broken functionality
- HIGH: Major bug, poor architecture, significant performance issue
- MEDIUM: Code quality issue, minor bug, maintainability concern
- LOW: Style violation, minor optimization opportunity

REVIEW PRINCIPLES:
1. Be thorough but constructive
2. Explain WHY something is wrong
3. Provide specific fixes, not vague complaints
4. Acknowledge good code too
5. Focus on user impact (not just theoretical problems)
6. Check frontend-backend integration
"""
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Review all code (backend + frontend).
        
        INPUT:
        - backend_files: List of backend files from Shubham
        - frontend_files: List of frontend files from Aanya
        - requirements: Original requirements from Saanvi
        
        OUTPUT:
        - Comprehensive review of all code
        - Issues categorized by severity
        - Approval decision for deployment
        """
        
        task_id = await self.log_task(
            task_type="code_review",
            status="running",
            input_data={
                "backend_files": len(input_data.get("backend_files", [])),
                "frontend_files": len(input_data.get("frontend_files", []))
            }
        )
        
        try:
            backend_files = input_data.get("backend_files", [])
            frontend_files = input_data.get("frontend_files", [])
            requirements = input_data.get("requirements", {})
            
            if not backend_files and not frontend_files:
                raise ValueError("No files provided for review")
            
            # Prepare files for review
            backend_summary = self._prepare_files_summary(backend_files, "Backend")
            frontend_summary = self._prepare_files_summary(frontend_files, "Frontend")
            
            # Build comprehensive review prompt
            review_prompt = f"""
REQUIREMENTS:
{json.dumps(requirements, indent=2)}

{backend_summary}

{frontend_summary}

Please provide a comprehensive code review covering:
1. Backend code quality and security
2. Frontend code quality and accessibility
3. Frontend-backend integration
4. Requirements compliance

Check for security issues, bugs, performance problems, and best practice violations.
"""
            
            # Call AI (FORCE CLAUDE - best for code review)
            print("🔍 Navya reviewing all code with Claude Sonnet...")
            ai_response = await self.call_ai(
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": review_prompt}
                ],
                complexity=9,
                is_critical=True,  # Force Claude
                max_tokens=4000
            )
            
            # Parse review
            review = self._parse_json_response(ai_response["content"])
            
            # Count all issues
            backend_issues = review.get("backend_review", {}).get("issues", [])
            frontend_issues = review.get("frontend_review", {}).get("issues", [])
            integration_issues = review.get("integration_issues", [])
            
            all_issues = backend_issues + frontend_issues + integration_issues
            issue_counts = self._count_issues(all_issues)
            
            # Log completion
            await self.log_task(
                task_type="code_review",
                status="completed",
                output_data={
                    "assessment": review.get("overall_assessment"),
                    "total_issues": len(all_issues),
                    "critical": issue_counts["critical"],
                    "high": issue_counts["high"]
                },
                ai_response=ai_response
            )
            
            return {
                "success": True,
                "review": review,
                "total_issues": len(all_issues),
                "critical_issues": issue_counts["critical"],
                "high_issues": issue_counts["high"],
                "medium_issues": issue_counts["medium"],
                "low_issues": issue_counts["low"],
                "review_id": task_id,
                "cost": ai_response.get("cost_inr", 0)
            }
            
        except Exception as e:
            await self.log_task(
                task_type="code_review",
                status="failed",
                output_data={"error": str(e)}
            )
            
            return {
                "success": False,
                "error": str(e),
                "review_id": task_id
            }
    
    def _prepare_files_summary(self, files: List[Dict[str, Any]], section: str) -> str:
        """Prepare files for review (truncate if needed)."""
        if not files:
            return f"\n{section.upper()} FILES: None provided\n"
        
        summary = f"\n{'='*60}\n{section.upper()} FILES ({len(files)} files)\n{'='*60}\n"
        
        for file in files:
            summary += f"\nFILE: {file['path']}\n"
            summary += f"TYPE: {file['type']}\n"
            summary += f"{'-'*60}\n"
            
            content = file.get('content', '')
            
            # Truncate very long files
            if len(content) > 4000:
                summary += content[:2000]
                summary += "\n\n[... middle section truncated ...]\n\n"
                summary += content[-2000:]
            else:
                summary += content
            
            summary += "\n\n"
        
        return summary
    
    def _count_issues(self, issues: List[Dict[str, Any]]) -> Dict[str, int]:
        """Count issues by severity."""
        counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        
        for issue in issues:
            severity = issue.get("severity", "low").lower()
            if severity in counts:
                counts[severity] += 1
        
        return counts
    
    def _parse_json_response(self, ai_response: str) -> Dict[str, Any]:
        """Parse JSON from AI response."""
        content = ai_response.strip()
        
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        
        content = content.strip()
        
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {e}\n\n{content}")


# =============================================================================
# END OF NAVYA (UPDATED - REVIEWS BACKEND + FRONTEND)
# =============================================================================