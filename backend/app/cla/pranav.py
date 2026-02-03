# =============================================================================
# PRANAV - DEVOPS ENGINEER
# Location: app/agents/pranav.py
# Purpose: Deployment and infrastructure management
# =============================================================================
#
# PRANAV'S ROLE:
# -------------
# DEVOPS SPECIALIST - deploys everything to production:
#
# What he does:
# ✅ Generates Docker configuration
# ✅ Creates docker-compose.yml
# ✅ Deploys backend to Railway
# ✅ Deploys frontend to Vercel
# ✅ Sets up database (Railway PostgreSQL)
# ✅ Configures environment variables
# ✅ Returns deployment URLs
#
# INPUT:
# - Approved code from Navya (backend + frontend)
# - Architecture from Saanvi (deployment decisions)
#
# OUTPUT:
# - Live application URLs
# - Deployment status
# - Access instructions
#
# =============================================================================

from app.agents.base import BaseAgent
from typing import Dict, Any, List
import json


class Pranav(BaseAgent):
    """
    DevOps engineer and deployment specialist.
    
    Pranav takes approved code and deploys it to production.
    He handles all infrastructure, configuration, and monitoring.
    """
    
    SYSTEM_PROMPT = """You are Pranav, a senior DevOps engineer specializing in cloud deployments.

YOUR EXPERTISE:
- Docker (containerization, multi-stage builds)
- Railway (Python deployments, PostgreSQL addons)
- Vercel (React deployments, edge functions)
- Environment configuration
- CI/CD pipelines
- Monitoring and logging

YOUR TASK:
Deploy approved code to production environments.

DEPLOYMENT TARGETS:
1. Backend → Railway
   - Dockerized FastAPI app
   - PostgreSQL addon
   - Environment variables configured
   - HTTPS enabled

2. Frontend → Vercel
   - React build optimized
   - Environment variables (API URL)
   - Custom domain (optional)
   - CDN distribution

3. Database → Railway PostgreSQL
   - Automatic backups
   - SSL connection
   - Connection pooling

WHAT YOU GENERATE:

1. Docker Files (Backend)
   - Dockerfile (multi-stage build)
   - docker-compose.yml (local development)
   - .dockerignore

2. Deployment Configuration
   - railway.json (Railway config)
   - vercel.json (Vercel config)
   - Environment variable templates

3. Deployment Scripts
   - deploy.sh (automated deployment)
   - setup.sh (initial setup)

4. Documentation
   - DEPLOYMENT.md (deployment guide)
   - PRODUCTION.md (production notes)

OUTPUT FORMAT:
{
    "deployment_configs": [
        {
            "file_path": "Dockerfile",
            "file_content": "complete Docker config here",
            "file_type": "docker",
            "purpose": "Backend containerization"
        }
    ],
    
    "deployment_status": {
        "backend": {
            "platform": "Railway",
            "status": "deployed",
            "url": "https://your-app.railway.app",
            "database_url": "postgresql://...",
            "deployed_at": "2025-12-31T10:30:00Z"
        },
        "frontend": {
            "platform": "Vercel",
            "status": "deployed",
            "url": "https://your-app.vercel.app",
            "deployed_at": "2025-12-31T10:35:00Z"
        }
    },
    
    "environment_variables": {
        "backend": {
            "DATABASE_URL": "Automatically set by Railway PostgreSQL addon",
            "JWT_SECRET": "Generate: openssl rand -hex 32",
            "CORS_ORIGINS": "https://your-app.vercel.app"
        },
        "frontend": {
            "VITE_API_URL": "https://your-app.railway.app/api/v1"
        }
    },
    
    "post_deployment": {
        "database_migrations": "Run: alembic upgrade head",
        "health_check": "GET https://your-app.railway.app/health",
        "admin_user": "Create via: POST /api/auth/signup"
    }
}

EXAMPLE DOCKERFILE (Multi-stage):
```dockerfile
# Build stage
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

DEPLOYMENT CHECKLIST:
1. ✅ Backend builds successfully
2. ✅ Database migrations run
3. ✅ Frontend connects to backend
4. ✅ HTTPS enabled (automatic on Railway/Vercel)
5. ✅ Environment variables set
6. ✅ CORS configured properly
7. ✅ Health check endpoint works
8. ✅ Error monitoring configured

IMPORTANT:
- Use environment variables for ALL configuration
- Enable HTTPS (automatic on Railway/Vercel)
- Set proper CORS origins (frontend URL)
- Configure database connection pooling
- Set up automatic backups
- Monitor deployment logs
"""
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deploy application to production.
        
        INPUT:
        - backend_files: Approved backend code
        - frontend_files: Approved frontend code
        - architecture: Deployment decisions from Saanvi
        
        OUTPUT:
        - Deployment configuration files
        - Deployment status
        - Live URLs
        """
        
        task_id = await self.log_task(
            task_type="deployment",
            status="running",
            input_data={"project_id": input_data.get("project_id")}
        )
        
        try:
            architecture = input_data.get("architecture", {})
            project_id = input_data.get("project_id")
            
            # Phase 1: Generate deployment configurations
            print("📦 Generating deployment configurations...")
            config_files = await self._generate_deployment_configs(architecture)
            
            # Save config files to database
            files_saved = []
            for config in config_files:
                file_id = await self._save_file(
                    project_id=project_id,
                    file_path=config["file_path"],
                    file_content=config["file_content"],
                    file_type=config["file_type"]
                )
                files_saved.append({
                    "path": config["file_path"],
                    "file_id": file_id
                })
            
            # Phase 2: Deploy to Railway (backend)
            print("🚂 Deploying backend to Railway...")
            backend_deployment = await self._deploy_to_railway(project_id)
            
            # Phase 3: Deploy to Vercel (frontend)
            print("▲ Deploying frontend to Vercel...")
            frontend_deployment = await self._deploy_to_vercel(project_id)
            
            # Save deployment info
            await self._save_deployment_info(
                project_id=project_id,
                backend_url=backend_deployment["url"],
                frontend_url=frontend_deployment["url"]
            )
            
            # Log completion
            await self.log_task(
                task_type="deployment",
                status="completed",
                output_data={
                    "backend_url": backend_deployment["url"],
                    "frontend_url": frontend_deployment["url"],
                    "config_files": len(files_saved)
                }
            )
            
            return {
                "success": True,
                "deployment": {
                    "backend": backend_deployment,
                    "frontend": frontend_deployment
                },
                "config_files": files_saved,
                "deployment_id": task_id
            }
            
        except Exception as e:
            await self.log_task(
                task_type="deployment",
                status="failed",
                output_data={"error": str(e)}
            )
            
            return {
                "success": False,
                "error": str(e),
                "deployment_id": task_id
            }
    
    async def _generate_deployment_configs(
        self,
        architecture: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate all deployment configuration files."""
        
        configs_prompt = f"""
Generate deployment configuration files for this architecture:

{json.dumps(architecture, indent=2)}

Generate:
1. Dockerfile (multi-stage, optimized)
2. docker-compose.yml (for local dev)
3. .dockerignore
4. railway.json (Railway configuration)
5. vercel.json (Vercel configuration)
6. DEPLOYMENT.md (deployment guide)

Return JSON array:
[
    {{
        "file_path": "Dockerfile",
        "file_content": "complete config here",
        "file_type": "docker",
        "purpose": "Backend containerization"
    }},
    ...
]
"""
        
        ai_response = await self.call_ai(
            messages=[
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": configs_prompt}
            ],
            complexity=6,
            max_tokens=3000
        )
        
        return self._parse_json_response(ai_response["content"])
    
    async def _deploy_to_railway(self, project_id: str) -> Dict[str, Any]:
        """
        Deploy backend to Railway.
        
        NOTE: This is a MOCK implementation.
        Real implementation would use Railway API.
        """
        
        # In real implementation:
        # 1. Create Railway project via API
        # 2. Add PostgreSQL addon
        # 3. Deploy code from git or Docker
        # 4. Set environment variables
        # 5. Wait for deployment to complete
        # 6. Return deployment URL
        
        # For now, return mock data
        return {
            "platform": "Railway",
            "status": "deployed",
            "url": f"https://nexsidi-{project_id[:8]}.railway.app",
            "database_url": "postgresql://railway:***@containers-us-west.railway.app:5432/railway",
            "deployed_at": "2025-12-31T10:30:00Z"
        }
    
    async def _deploy_to_vercel(self, project_id: str) -> Dict[str, Any]:
        """
        Deploy frontend to Vercel.
        
        NOTE: This is a MOCK implementation.
        Real implementation would use Vercel API.
        """
        
        # In real implementation:
        # 1. Create Vercel project via API
        # 2. Connect to git repository
        # 3. Set environment variables (VITE_API_URL)
        # 4. Trigger deployment
        # 5. Wait for build to complete
        # 6. Return deployment URL
        
        # For now, return mock data
        return {
            "platform": "Vercel",
            "status": "deployed",
            "url": f"https://nexsidi-{project_id[:8]}.vercel.app",
            "deployed_at": "2025-12-31T10:35:00Z"
        }
    
    async def _save_deployment_info(
        self,
        project_id: str,
        backend_url: str,
        frontend_url: str
    ) -> None:
        """Save deployment URLs to database."""
        from app.models import Deployment
        from uuid import uuid4
        from datetime import datetime
        
        # Save backend deployment
        backend_deploy = Deployment(
            id=uuid4(),
            project_id=project_id,
            deployment_type="railway",
            deployment_url=backend_url,
            config={"platform": "Railway", "type": "backend"},
            created_at=datetime.utcnow()
        )
        
        # Save frontend deployment
        frontend_deploy = Deployment(
            id=uuid4(),
            project_id=project_id,
            deployment_type="vercel",
            deployment_url=frontend_url,
            config={"platform": "Vercel", "type": "frontend"},
            created_at=datetime.utcnow()
        )
        
        self.db.add(backend_deploy)
        self.db.add(frontend_deploy)
        self.db.commit()
    
    async def _save_file(
        self,
        project_id: str,
        file_path: str,
        file_content: str,
        file_type: str
    ) -> str:
        """Save deployment config file to database."""
        from app.models import CodeFile
        from uuid import uuid4
        
        code_file = CodeFile(
            id=uuid4(),
            project_id=project_id,
            file_path=file_path,
            file_content=file_content,
            file_type=file_type,
            created_by_agent="pranav",
            version=1
        )
        
        self.db.add(code_file)
        self.db.commit()
        self.db.refresh(code_file)
        
        return str(code_file.id)
    
    def _parse_json_response(self, ai_response: str) -> Any:
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
# END OF PRANAV (NEW - DEVOPS SPECIALIST)
# =============================================================================