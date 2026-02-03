# =============================================================================
# SAANVI - REQUIREMENTS ANALYST AGENT
# Location: app/agents/saanvi.py
# Purpose: Analyze requirements, score complexity, quote price
# =============================================================================
#
# SAANVI'S ROLE IN THE PIPELINE:
# ------------------------------
# User chats with Tilotma → Gets project idea
#   ↓
# Tilotma says "ready for project"
#   ↓
# **SAANVI TAKES OVER** ← We are here
#   ↓
# Analyzes conversation
# Extracts: features, complexity, tech stack, price
#   ↓
# Returns structured requirements document
#   ↓
# Shubham uses this to generate code
#
# COMPLEXITY SCORING (1-10):
# -------------------------
# 1-3: Simple
#   - Static website, landing page
#   - No database, no user accounts
#   - Example: Restaurant menu display
#   - Price: ₹10K - ₹30K
#
# 4-7: Medium
#   - Dynamic website with database
#   - User authentication, CRUD operations
#   - Example: Restaurant with reservations
#   - Price: ₹40K - ₹1.5L
#
# 8-10: Complex
#   - Advanced features, integrations
#   - Payment processing, real-time updates
#   - Example: Food delivery platform
#   - Price: ₹1.6L - ₹3L
#
# =============================================================================

from app.agents.base import BaseAgent
from typing import Dict, Any
import json
from datetime import datetime


class Saanvi(BaseAgent):
    """
    Requirements analyst and pricing expert.
    
    Saanvi is the bridge between conversation and code.
    She transforms casual chat into structured technical specs.
    
    Think of her as a business analyst who:
    - Listens to customer needs
    - Asks clarifying questions
    - Documents requirements
    - Estimates effort and cost
    """
    
    # System prompt defines Saanvi's personality and expertise
    SYSTEM_PROMPT = """You are Saanvi, an expert requirements analyst and technical architect.

YOUR EXPERTISE:
- Understanding customer needs from conversation
- Translating business requirements to technical specs
- Estimating project complexity accurately
- Recommending appropriate technology stacks
- Calculating fair pricing

YOUR TASK:
Analyze the conversation between user and Tilotma (chat agent).
Extract structured requirements and provide technical recommendations.

OUTPUT FORMAT (strict JSON):
{
    "requirements": {
        "project_title": "Brief descriptive title",
        "description": "2-3 sentence summary of what user wants",
        "features": [
            "Feature 1 description",
            "Feature 2 description",
            ...
        ],
        "user_types": ["End user", "Admin", etc],
        "must_have": ["Critical feature 1", ...],
        "nice_to_have": ["Optional feature 1", ...]
    },
    "technical": {
        "complexity_score": 5,  // 1-10 scale
        "complexity_reasoning": "Why this score?",
        "recommended_stack": {
            "frontend": "React with TypeScript",
            "backend": "FastAPI (Python)",
            "database": "PostgreSQL",
            "hosting": "Railway",
            "additional": ["Redis for caching", ...]
        },
        "estimated_hours": 120,
        "estimated_iterations": 5  // Mid-level changes included
    },
    "pricing": {
        "base_price": 75000,  // In rupees
        "price_breakdown": {
            "design_ui_ux": 15000,
            "backend_development": 30000,
            "frontend_development": 20000,
            "testing_deployment": 10000
        },
        "included_iterations": {
            "mid_level": 5,
            "small": 11
        },
        "additional_costs": {
            "domain_ssl": 3000,
            "hosting_3months": 5000
        }
    },
    "timeline": {
        "estimated_days": 15,
        "milestones": [
            {"milestone": "UI mockups", "days": 3},
            {"milestone": "Backend API", "days": 5},
            {"milestone": "Frontend", "days": 4},
            {"milestone": "Testing & Deploy", "days": 3}
        ]
    },
    "risks": [
        "Potential challenge 1",
        "Potential challenge 2"
    ],
    "recommendations": [
        "Suggestion for success",
        "Best practice advice"
    ],
    "ready_for_development": true  // Can we start coding?
}

COMPLEXITY SCORING GUIDE:
1-3 (Simple): Static sites, no backend, no auth
4-7 (Medium): Dynamic sites, database, user accounts, CRUD
8-10 (Complex): Advanced features, integrations, real-time, payments

PRICING FORMULA:
- Base: Complexity × ₹10,000
- Add: Special features (payment +₹15K, real-time +₹20K)
- Include: 5 mid-level + 11 small iterations
- Range: ₹10K (simple) to ₹3L (complex)

IMPORTANT:
- Be realistic about complexity (don't underscore)
- Pricing should be fair but sustainable
- If requirements unclear, mark ready_for_development=false
- Always explain your reasoning
"""
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze requirements and provide technical recommendations.
        
        WHAT THIS METHOD DOES:
        ---------------------
        1. Get conversation history (user + Tilotma chat)
        2. Send to AI for analysis
        3. Parse JSON response
        4. Validate requirements
        5. Save analysis to database
        6. Return structured requirements
        
        INPUT FORMAT:
        ------------
        {
            "conversation_history": [
                {"role": "user", "content": "I want a website"},
                {"role": "assistant", "content": "What kind?"},
                ...
            ],
            "project_id": "uuid-here"  // Optional, if project already created
        }
        
        OUTPUT FORMAT:
        -------------
        {
            "success": true,
            "requirements": {...},
            "technical": {...},
            "pricing": {...},
            "timeline": {...},
            "analysis_id": "uuid"  // Task ID in database
        }
        
        EXAMPLE FLOW:
        ------------
        User → Tilotma: "I want restaurant website with menu and reservations"
        API calls: await saanvi.execute({"conversation_history": [...]})
        Saanvi analyzes → Complexity 5, ₹75K quote
        Returns: Complete requirements document
        """
        
        # Log task start
        task_id = await self.log_task(
            task_type="requirements_analysis",
            status="running",
            input_data=input_data
        )
        
        try:
            # Extract conversation history
            conversation = input_data.get("conversation_history", [])
            
            if not conversation:
                # No conversation provided - get from database
                conversation = self.get_conversation_history(limit=50)
            
            # Build analysis prompt
            # We send conversation to AI and ask for structured output
            analysis_prompt = self._build_analysis_prompt(conversation)
            
            # Call AI for requirements analysis
            # Use HIGH complexity because this is critical analysis
            ai_response = await self.call_ai(
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": analysis_prompt}
                ],
                complexity=8,  # High - this is important analysis
                is_critical=True,  # Use best model available
                max_tokens=3000  # Need detailed response
            )
            
            # Parse AI response (should be JSON)
            analysis = self._parse_analysis(ai_response["content"])
            
            # Validate analysis has required fields
            self._validate_analysis(analysis)
            
            # Save to project if project_id provided
            project_id = input_data.get("project_id")
            if project_id:
                await self._save_to_project(project_id, analysis)
            
            # Log task completion
            await self.log_task(
                task_type="requirements_analysis",
                status="completed",
                input_data=input_data,
                output_data=analysis,
                ai_response=ai_response
            )
            
            # Return success with analysis
            return {
                "success": True,
                "analysis": analysis,
                "analysis_id": task_id,
                "cost": ai_response.get("cost_inr", 0)
            }
            
        except Exception as e:
            # Log failure
            await self.log_task(
                task_type="requirements_analysis",
                status="failed",
                input_data=input_data,
                output_data={"error": str(e)}
            )
            
            # Return error
            return {
                "success": False,
                "error": str(e),
                "analysis_id": task_id
            }
    
    def _build_analysis_prompt(self, conversation: list) -> str:
        """
        Build prompt for AI to analyze conversation.
        
        Converts conversation history into formatted text
        that AI can analyze.
        """
        prompt = "CONVERSATION HISTORY:\n\n"
        
        for msg in conversation:
            role = "USER" if msg["role"] == "user" else "ASSISTANT"
            prompt += f"{role}: {msg['content']}\n\n"
        
        prompt += "\nBased on this conversation, provide your complete requirements analysis in JSON format."
        
        return prompt
    
    def _parse_analysis(self, ai_response: str) -> Dict[str, Any]:
        """
        Parse AI response into structured dictionary.
        
        AI should return JSON, but might include markdown formatting.
        We need to extract just the JSON part.
        """
        # Remove markdown code blocks if present
        content = ai_response.strip()
        
        # Remove ```json and ``` if present
        if content.startswith("```json"):
            content = content[7:]  # Remove ```json
        if content.startswith("```"):
            content = content[3:]  # Remove ```
        if content.endswith("```"):
            content = content[:-3]  # Remove ```
        
        content = content.strip()
        
        try:
            # Parse JSON
            analysis = json.loads(content)
            return analysis
        except json.JSONDecodeError as e:
            # JSON parsing failed
            raise ValueError(f"AI response is not valid JSON: {e}\n\nResponse: {content}")
    
    def _validate_analysis(self, analysis: Dict[str, Any]) -> None:
        """
        Ensure analysis has all required fields.
        
        Raises ValueError if critical fields missing.
        """
        required_sections = ["requirements", "technical", "pricing"]
        
        for section in required_sections:
            if section not in analysis:
                raise ValueError(f"Analysis missing required section: {section}")
        
        # Validate technical section
        tech = analysis.get("technical", {})
        if "complexity_score" not in tech:
            raise ValueError("Technical analysis missing complexity_score")
        
        complexity = tech["complexity_score"]
        if not isinstance(complexity, (int, float)) or complexity < 1 or complexity > 10:
            raise ValueError(f"Invalid complexity_score: {complexity}. Must be 1-10.")
        
        # Validate pricing
        pricing = analysis.get("pricing", {})
        if "base_price" not in pricing:
            raise ValueError("Pricing analysis missing base_price")
    
    async def _save_to_project(self, project_id: str, analysis: Dict[str, Any]) -> None:
        """
        Update project record with requirements analysis.
        
        Saves:
        - Complexity score
        - Tech stack
        - Quoted price
        - Requirements document
        """
        from app.models import Project
        
        # Get project from database
        project = self.db.query(Project).filter(Project.id == project_id).first()
        
        if not project:
            raise ValueError(f"Project not found: {project_id}")
        
        # Update project fields
        tech = analysis.get("technical", {})
        pricing = analysis.get("pricing", {})
        
        project.complexity_score = tech.get("complexity_score")
        project.tech_stack = tech.get("recommended_stack")
        project.quoted_price = pricing.get("base_price")
        project.requirements_locked = True  # Analysis complete
        project.status = "requirements_analyzed"
        
        # Save
        self.db.commit()


# =============================================================================
# END OF SAANVI
# =============================================================================