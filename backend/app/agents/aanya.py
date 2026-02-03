"""
AANYA - Frontend Developer Agent (React/TypeScript Specialist)

Purpose: Generate production-ready React frontend code
Technology: React 18+, TypeScript, Tailwind CSS, React Router
Architecture: Standalone V2 (no BaseAgent inheritance)

Model: Gemini 2.5 Pro for complex frontend generation
"""

from typing import Dict, Any, List
import json
import base64
import logging

# Standalone - direct AI Router access
from app.services.ai_router import ai_router, TaskComplexity


class Aanya:
    """
    Frontend Developer Agent - React/TypeScript Specialist.
    
    Follows standalone V2 architecture - no BaseAgent inheritance.
    Uses AI Router directly for all AI operations.
    
    Usage:
        aanya = Aanya(project_id="proj-123")
        result = await aanya.execute(input_data)
    """
    
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
3. Return in JSON format above

EXAMPLE:
If you write this React code:
```tsx
import React from 'react';

const Button = () => <button>Click</button>;
export default Button;
```

You must encode it and return:
{
    "file_path": "frontend/src/components/Button.tsx",
    "file_content_base64": "aW1wb3J0IFJlYWN0IGZyb20gJ3JlYWN0JzsKCmNvbnN0IEJ1dHRvbiA9ICgpID0+IDxidXR0b24+Q2xpY2s8L2J1dHRvbj47CmV4cG9ydCBkZWZhdWx0IEJ1dHRvbjs=",
    "file_type": "typescript-react",
    "description": "Simple button component"
}

NEVER return code in markdown blocks. ALWAYS base64 encode."""

    def __init__(self, project_id: str):
        """
        Initialize Aanya for a project.
        
        Args:
            project_id: UUID of the project
        """
        # Standalone - no inheritance
        self.project_id = project_id
        
        # Direct AI Router access
        self.ai_router = ai_router
        
        # Logging
        self.logger = logging.getLogger("agent.aanya")
        self.logger.setLevel(logging.INFO)
        
        # Statistics
        self.files_generated = 0
        self.total_cost = 0.0
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate frontend code based on architecture.
        
        Args:
            input_data: Contains:
                - frontend_architecture: From Saanvi
                - api_architecture: Backend API structure
                - business_requirements: Original requirements
        
        Returns:
            Dict containing:
                - status: "success" or "error"
                - files: List of generated files with base64 content
                - total_files: Count of files
                - cost: Total generation cost
        """
        try:
            self.logger.info("🎨 Starting frontend generation...")
            
            # Extract architecture
            fe_arch = input_data.get("frontend_architecture", {})
            api_arch = input_data.get("api_architecture", {})
            
            if not fe_arch:
                raise ValueError("Frontend architecture is required")
            
            # Generate file list
            file_plan = await self._plan_files(fe_arch, api_arch)
            
            # Generate each file
            generated_files = []
            context = []
            
            for file_spec in file_plan["files"]:
                self.logger.info(f"📝 Generating {file_spec['path']}...")
                
                file_result = await self._generate_frontend_file(
                    file_spec,
                    fe_arch,
                    api_arch,
                    context
                )
                
                generated_files.append(file_result)
                context.append(file_result)
                self.files_generated += 1
            
            self.logger.info(
                f"✅ Frontend generation complete: {len(generated_files)} files, "
                f"₹{self.total_cost:.2f}"
            )
            
            return {
                "status": "success",
                "files": generated_files,
                "total_files": len(generated_files),
                "cost": self.total_cost
            }
            
        except Exception as e:
            self.logger.error(f"❌ Frontend generation failed: {e}")
            raise
    
    async def _plan_files(
        self,
        fe_arch: Dict[str, Any],
        api_arch: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Plan which frontend files to generate.
        
        Returns ordered list of files with priorities.
        """
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

Return ONLY valid JSON in this format:
{{
    "file_path": "{file_spec['path']}",
    "file_content_base64": "YOUR_BASE64_ENCODED_CODE_HERE",
    "file_type": "{file_spec['type']}",
    "description": "Brief description"
}}
"""
        
        # Call AI Router directly
        response = await self.ai_router.generate(
            messages=[{"role": "user", "content": generation_prompt}],
            system_prompt=self.SYSTEM_PROMPT,
            task_type="code_generation",
            complexity=TaskComplexity.COMPLEX,
            max_tokens=8000
        )
        
        # Log cost
        self.total_cost += response.cost_estimate
        self.logger.info(
            f"✅ {response.output_tokens} tokens, "
            f"₹{response.cost_estimate:.4f}"
        )
        
        # Parse response
        try:
            result = json.loads(response.content)
            
            # Decode base64 content
            if "file_content_base64" in result:
                decoded = base64.b64decode(result["file_content_base64"]).decode("utf-8")
                result["file_content"] = decoded
            
            return result
            
        except json.JSONDecodeError as e:
            self.logger.error(f"❌ Failed to parse JSON: {e}")
            self.logger.error(f"Response: {response.content[:500]}")
            raise
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get generation statistics"""
        return {
            "files_generated": self.files_generated,
            "total_cost": self.total_cost
        }


if __name__ == "__main__":
    import asyncio
    
    async def test():
        aanya = Aanya(project_id="test-fe-001")
        
        # Sample input
        input_data = {
            "frontend_architecture": {
                "pages": [
                    {"component": "Home", "purpose": "Landing page"},
                    {"component": "About", "purpose": "About page"}
                ],
                "component_structure": {
                    "common": ["Button", "Card"],
                    "forms": ["Input", "Select"]
                }
            },
            "api_architecture": {
                "endpoints": [
                    {"path": "/api/users", "method": "GET"}
                ]
            }
        }
        
        result = await aanya.execute(input_data)
        print(json.dumps(result, indent=2))
        print(f"\nStatistics: {aanya.get_statistics()}")
    
    asyncio.run(test())