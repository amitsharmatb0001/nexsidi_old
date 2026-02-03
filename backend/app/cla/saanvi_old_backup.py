from app.agents.base import BaseAgent
from typing import Dict, Any
import json


class Saanvi(BaseAgent):
    """System Architect and Requirements Analyst"""
    
    SYSTEM_PROMPT = """You are Saanvi, a system architect.

Design software systems from requirements.

CRITICAL: Generate MINIMAL but COMPLETE JSON. Keep everything SHORT.

OUTPUT (strict JSON):
{
    "project_overview": {
        "title": "Project Name",
        "description": "One sentence",
        "user_types": ["Type1", "Type2"],
        "complexity_score": 6,
        "complexity_reasoning": "One sentence"
    },
    "requirements": {
        "functional": [
            {"id": "F1", "feature": "Name", "description": "Short", "priority": "must_have"}
        ],
        "non_functional": [
            {"category": "performance", "requirement": "Short"}
        ]
    },
    "database_architecture": {
        "tables": [
            {
                "name": "users",
                "columns": [
                    {"name": "id", "type": "UUID", "constraints": ["PRIMARY KEY"]},
                    {"name": "email", "type": "VARCHAR(255)", "constraints": ["UNIQUE"]}
                ],
                "indexes": [],
                "relationships": []
            }
        ]
    },
    "api_architecture": {
        "base_url": "/api/v1",
        "authentication": "JWT",
        "endpoints": [
            {"path": "/auth/signup", "method": "POST", "purpose": "Create account"}
        ]
    },
    "frontend_architecture": {
        "framework": "React",
        "pages": [
            {"route": "/", "component": "HomePage", "purpose": "Landing"}
        ],
        "component_structure": {
            "layout": ["Header", "Footer"]
        }
    },
    "technical_decisions": {
        "backend_framework": "FastAPI",
        "database": "PostgreSQL",
        "frontend_framework": "React"
    },
    "pricing": {
        "base_price": 75000,
        "timeline": {"total_days": 10}
    },
    "ready_for_development": true
}

RULES:
- Maximum 5 functional requirements
- Maximum 3 non-functional requirements
- Maximum 5 tables
- Maximum 8 endpoints
- Maximum 5 pages
- ALL descriptions must be ONE sentence
- NO nested objects except where shown above
- Generate COMPLETE valid JSON only
"""
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Complete system architecture design"""
        
        task_id = await self.log_task(
            task_type="system_architecture",
            status="running",
            input_data=input_data
        )
        
        try:
            conversation = input_data.get("conversation_history", [])
            
            if not conversation:
                conversation = self.get_conversation_history(limit=50)
            
            architecture_prompt = self._build_architecture_prompt(conversation)
            
            print("🏗️ Saanvi designing system architecture...")
            ai_response = await self.call_ai(
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": architecture_prompt}
                ],
                complexity=9,
                is_critical=True,
                max_tokens=6000  # Reduced from 8000
            )
            
            # Parse with better error handling
            try:
                architecture = self._parse_json_response(ai_response["content"])
            except ValueError as e:
                # Save the raw response for debugging
                print(f"\n⚠️ JSON Parse Error. Saving raw response...")
                with open("saanvi_debug_response.json", "w") as f:
                    f.write(ai_response["content"])
                print(f"   Saved to: saanvi_debug_response.json")
                raise e
            
            self._validate_architecture(architecture)
            
            project_id = input_data.get("project_id")
            if project_id:
                await self._save_to_project(project_id, architecture)
            
            await self.log_task(
                task_type="system_architecture",
                status="completed",
                output_data={
                    "complexity": architecture.get("project_overview", {}).get("complexity_score"),
                    "tables": len(architecture.get("database_architecture", {}).get("tables", [])),
                    "endpoints": len(architecture.get("api_architecture", {}).get("endpoints", [])),
                    "pages": len(architecture.get("frontend_architecture", {}).get("pages", []))
                },
                ai_response=ai_response
            )
            
            return {
                "success": True,
                "architecture": architecture,
                "architecture_id": task_id,
                "cost": ai_response.get("cost_inr", 0)
            }
            
        except Exception as e:
            await self.log_task(
                task_type="system_architecture",
                status="failed",
                output_data={"error": str(e)}
            )
            
            return {
                "success": False,
                "error": str(e),
                "architecture_id": task_id
            }
    
    def _build_architecture_prompt(self, conversation: list) -> str:
        """Build minimal prompt"""
        prompt = "CONVERSATION:\n\n"
        
        for msg in conversation[-10:]:  # Only last 10 messages to reduce tokens
            role = "USER" if msg["role"] == "user" else "ASSISTANT"
            prompt += f"{role}: {msg['content']}\n\n"
        
        prompt += """
Design MINIMAL but COMPLETE system architecture.

STRICT LIMITS:
- Max 5 functional requirements
- Max 3 non-functional requirements  
- Max 5 database tables
- Max 8 API endpoints
- Max 5 frontend pages
- ALL descriptions ONE sentence only

Return valid JSON only. No extra text.
"""
        return prompt
    
    def _parse_json_response(self, ai_response: str) -> Dict[str, Any]:
        """Parse JSON with robust handling"""
        content = ai_response.strip()
        
        # Remove markdown
        if content.startswith("```json"):
            content = content[7:]
        elif content.startswith("```"):
            content = content[3:]
        
        if content.endswith("```"):
            content = content[:-3]
        
        content = content.strip()
        
        # Try to find JSON object bounds
        start = content.find('{')
        end = content.rfind('}')
        
        if start != -1 and end != -1:
            content = content[start:end+1]
        
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            # Show more context around error
            lines = content.split('\n')
            error_line = e.lineno - 1 if e.lineno else 0
            context_start = max(0, error_line - 3)
            context_end = min(len(lines), error_line + 3)
            
            context = '\n'.join(lines[context_start:context_end])
            
            raise ValueError(
                f"JSON Parse Error at line {e.lineno}, col {e.colno}\n"
                f"Error: {e.msg}\n\n"
                f"Context:\n{context}\n\n"
                f"Full content length: {len(content)} chars"
            )
    
    def _validate_architecture(self, architecture: Dict[str, Any]) -> None:
        """Validate required sections"""
        required = [
            "project_overview",
            "requirements",
            "database_architecture",
            "api_architecture",
            "frontend_architecture",
            "pricing"
        ]
        
        missing = [s for s in required if s not in architecture]
        if missing:
            raise ValueError(f"Missing sections: {', '.join(missing)}")
        
        # Quick validation
        if not architecture.get("database_architecture", {}).get("tables"):
            raise ValueError("No tables in database architecture")
        
        if not architecture.get("api_architecture", {}).get("endpoints"):
            raise ValueError("No endpoints in API architecture")
        
        if not architecture.get("frontend_architecture", {}).get("pages"):
            raise ValueError("No pages in frontend architecture")
    
    async def _save_to_project(self, project_id: str, architecture: Dict[str, Any]) -> None:
        """Save architecture to project"""
        from app.models import Project
        
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ValueError(f"Project not found: {project_id}")
        
        overview = architecture.get("project_overview", {})
        pricing = architecture.get("pricing", {})
        
        project.complexity_score = overview.get("complexity_score")
        project.tech_stack = architecture.get("technical_decisions")
        project.quoted_price = pricing.get("base_price")
        project.requirements_locked = True
        project.status = "architecture_complete"
        
        self.db.commit()