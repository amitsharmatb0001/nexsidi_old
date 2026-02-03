from app.agents.base import BaseAgent
from typing import Dict, Any, List
import json
import base64  # ← NEW: For encoding file content


class Aanya(BaseAgent):
    """Frontend Developer - React/TypeScript Specialist"""
    
    SYSTEM_PROMPT = """You are Aanya, a senior frontend developer specializing in React and TypeScript.

YOUR EXPERTISE:
- React 18+ (hooks, context, components)
- TypeScript (strict types, interfaces)
- React Router v6
- Tailwind CSS
- Fetch API
- Form handling
- Responsive design
- Accessibility

YOUR TASK:
Implement frontend architecture designed by Saanvi.

WHAT YOU GENERATE (Frontend Only):
1. React Components - Functional with TypeScript
2. Pages - Full page components with routing
3. API Integration - Fetch calls to backend
4. Styling - Tailwind utility classes
5. Configuration - package.json, tsconfig.json

WHAT YOU DO NOT GENERATE:
- ❌ Backend code (Python/FastAPI)
- ❌ Database models
- ❌ Deployment configs

CODE QUALITY:
1. TypeScript strict mode
2. Interface for all props
3. Error handling (try/catch)
4. Loading indicators
5. Responsive design
6. Accessibility (ARIA, alt text)
7. Environment variables for API URL

CRITICAL - OUTPUT FORMAT WITH BASE64:
To avoid JSON encoding issues with newlines/quotes/special characters,
encode the file content as base64.

{
    "file_path": "frontend/src/components/MenuItem.tsx",
    "file_content_base64": "BASE64_ENCODED_CONTENT_HERE",
    "file_type": "typescript-react",
    "description": "Menu item component"
}

HOW TO ENCODE IN BASE64:
1. Write your complete React/TypeScript code
2. Convert to base64 string
3. Put base64 string in file_content_base64

YOU MUST:
- Generate complete working code first
- Then encode it to base64
- Return JSON with file_content_base64 field
- Do NOT include raw code with newlines in JSON
"""
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate complete frontend codebase"""
        
        task_id = await self.log_task(
            task_type="frontend_generation",
            status="running",
            input_data={"project_id": input_data.get("project_id")}
        )
        
        try:
            architecture = input_data.get("architecture", {})
            project_id = input_data.get("project_id")
            
            if not architecture:
                raise ValueError("Architecture missing from input")
            
            fe_arch = architecture.get("frontend_architecture", {})
            api_arch = architecture.get("api_architecture", {})
            
            # Plan frontend structure
            print("📁 Planning frontend structure...")
            structure = self._plan_frontend_structure(fe_arch, api_arch)
            
            # Generate files
            print(f"📝 Generating {len(structure['files'])} frontend files...")
            files_generated = []
            
            for file_spec in structure["files"]:
                print(f"   Generating: {file_spec['path']}")
                
                file_result = await self._generate_frontend_file(
                    file_spec=file_spec,
                    fe_arch=fe_arch,
                    api_arch=api_arch,
                    context=files_generated
                )
                
                # Decode base64 content
                file_content = self._decode_base64_content(file_result)
                
                # Save to database
                file_id = await self._save_file(
                    project_id=project_id,
                    file_path=file_result["file_path"],
                    file_content=file_content,
                    file_type=file_result["file_type"]
                )
                
                files_generated.append({
                    "path": file_result["file_path"],
                    "type": file_result["file_type"],
                    "lines": len(file_content.split("\n")),
                    "file_id": file_id
                })
            
            # Log completion
            await self.log_task(
                task_type="frontend_generation",
                status="completed",
                output_data={
                    "files_count": len(files_generated),
                    "components": len([f for f in files_generated if "components" in f["path"]])
                }
            )
            
            return {
                "success": True,
                "frontend_files": len(files_generated),
                "file_manifest": files_generated,
                "structure": structure,
                "generation_id": task_id
            }
            
        except Exception as e:
            await self.log_task(
                task_type="frontend_generation",
                status="failed",
                output_data={"error": str(e)}
            )
            
            return {
                "success": False,
                "error": str(e),
                "generation_id": task_id
            }
    
    def _plan_frontend_structure(
        self,
        fe_arch: Dict[str, Any],
        api_arch: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Plan frontend file structure"""
        
        files = [
            # Core
            {"path": "frontend/src/App.tsx", "type": "typescript-react", "priority": 1, "purpose": "Main app with routing"},
            {"path": "frontend/src/main.tsx", "type": "typescript-react", "priority": 1, "purpose": "React entry"},
            {"path": "frontend/src/index.css", "type": "css", "priority": 1, "purpose": "Tailwind imports"},
            
            # API
            {"path": "frontend/src/api/client.ts", "type": "typescript", "priority": 2, "purpose": "API client"},
            {"path": "frontend/src/types/index.ts", "type": "typescript", "priority": 2, "purpose": "TypeScript interfaces"},
            
            # Context
            {"path": "frontend/src/context/AuthContext.tsx", "type": "typescript-react", "priority": 2, "purpose": "Auth context"},
            
            # Layout
            {"path": "frontend/src/components/layout/Header.tsx", "type": "typescript-react", "priority": 3, "purpose": "Header"},
            {"path": "frontend/src/components/layout/Footer.tsx", "type": "typescript-react", "priority": 3, "purpose": "Footer"},
        ]
        
        # Add pages
        for page in fe_arch.get("pages", []):
            files.append({
                "path": f"frontend/src/pages/{page['component']}.tsx",
                "type": "typescript-react",
                "priority": 4,
                "purpose": page["purpose"]
            })
        
        # Add components
        comp_struct = fe_arch.get("component_structure", {})
        for category, components in comp_struct.items():
            if category not in ["layout"]:
                for comp_name in components:
                    comp_clean = comp_name.split("(")[0].strip()
                    files.append({
                        "path": f"frontend/src/components/{category}/{comp_clean}.tsx",
                        "type": "typescript-react",
                        "priority": 5,
                        "purpose": comp_name
                    })
        
        # Config
        files.extend([
            {"path": "frontend/package.json", "type": "json", "priority": 6, "purpose": "NPM deps"},
            {"path": "frontend/tsconfig.json", "type": "json", "priority": 6, "purpose": "TS config"},
            {"path": "frontend/tailwind.config.js", "type": "javascript", "priority": 6, "purpose": "Tailwind config"},
            {"path": "frontend/vite.config.ts", "type": "typescript", "priority": 6, "purpose": "Vite config"},
            {"path": "frontend/.env.example", "type": "text", "priority": 6, "purpose": "Env template"},
            {"path": "frontend/README.md", "type": "markdown", "priority": 7, "purpose": "Documentation"}
        ])
        
        files.sort(key=lambda x: x["priority"])
        
        return {"files": files}
    
    async def _generate_frontend_file(
        self,
        file_spec: Dict[str, Any],
        fe_arch: Dict[str, Any],
        api_arch: Dict[str, Any],
        context: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate a single frontend file"""
        
        context_str = ""
        if context:
            context_str = "\n\nPREVIOUSLY GENERATED:\n"
            for prev in context[-3:]:
                context_str += f"- {prev['path']}\n"
        
        generation_prompt = f"""
Generate frontend code for:

FILE: {file_spec['path']}
PURPOSE: {file_spec['purpose']}

FRONTEND ARCHITECTURE:
{json.dumps(fe_arch, indent=2)}

API ARCHITECTURE:
{json.dumps(api_arch, indent=2)}
{context_str}

Generate COMPLETE, PRODUCTION-READY React/TypeScript code.
Include imports, types, error handling, accessibility.

CRITICAL: Return file content as BASE64 to avoid JSON issues.

Return JSON:
{{
    "file_path": "{file_spec['path']}",
    "file_content_base64": "BASE64_ENCODED_CODE_HERE",
    "file_type": "{file_spec['type']}",
    "description": "what this does"
}}
"""
        
        ai_response = await self.call_ai(
            messages=[
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": generation_prompt}
            ],
            complexity=8,
            max_tokens=4000
        )
        
        return self._parse_json_response(ai_response["content"])
    
    def _decode_base64_content(self, file_result: Dict[str, Any]) -> str:
        """Decode base64 file content with fallback"""
        if "file_content_base64" in file_result:
            try:
                encoded = file_result["file_content_base64"]
                decoded_bytes = base64.b64decode(encoded)
                return decoded_bytes.decode('utf-8')
            except Exception as e:
                raise ValueError(f"Failed to decode base64 content: {e}")
        elif "file_content" in file_result:
            return file_result["file_content"]
        else:
            raise ValueError("No file_content or file_content_base64 in response")
    
    async def _save_file(
        self,
        project_id: str,
        file_path: str,
        file_content: str,
        file_type: str
    ) -> str:
        """Save file to database"""
        from app.models import CodeFile
        from uuid import uuid4
        
        code_file = CodeFile(
            id=uuid4(),
            project_id=project_id,
            file_path=file_path,
            file_content=file_content,
            file_type=file_type,
            created_by_agent="aanya",
            version=1
        )
        
        self.db.add(code_file)
        self.db.commit()
        self.db.refresh(code_file)
        
        return str(code_file.id)
    
    def _parse_json_response(self, ai_response: str) -> Dict[str, Any]:
        """Parse JSON from AI response"""
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
            raise ValueError(f"Invalid JSON: {e}\n\n{content[:500]}...")