"""
PRANAV - DevOps Engineer Agent

Purpose: Deploy applications to production (Railway + Vercel)
Technology: Docker, Railway API, Vercel API
Architecture: Standalone V2 (no BaseAgent inheritance)

Model: Gemini 3 Flash for deployment config generation
"""

from typing import Dict, Any, List
import json
import logging
from datetime import datetime
from uuid import uuid4

# Standalone - direct AI Router access
from app.services.ai_router import ai_router, TaskComplexity


class Pranav:
    """
    DevOps Engineer Agent - Deployment Specialist.
    
    Follows standalone V2 architecture - no BaseAgent inheritance.
    Uses AI Router directly for all AI operations.
    
    Usage:
        pranav = Pranav(project_id="proj-123")
        result = await pranav.execute(input_data)
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

    def __init__(self, project_id: str):
        """
        Initialize Pranav for a project.
        
        Args:
            project_id: UUID of the project
        """
        # Standalone - no inheritance
        self.project_id = project_id
        
        # Direct AI Router access
        self.ai_router = ai_router
        
        # Logging
        self.logger = logging.getLogger("agent.pranav")
        self.logger.setLevel(logging.INFO)
        
        # Statistics
        self.deployments_executed = 0
        self.total_cost = 0.0
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deploy application to production.
        
        Args:
            input_data: Contains:
                - backend_files: Approved backend code
                - frontend_files: Approved frontend code
                - architecture: Deployment decisions from Saanvi
        
        Returns:
            Dict containing:
                - success: Boolean
                - deployment: Backend and frontend deployment info
                - config_files: Generated configuration files
                - urls: Live application URLs
        """
        try:
            self.logger.info("🚀 Starting deployment process...")
            
            architecture = input_data.get("architecture", {})
            
            if not architecture:
                raise ValueError("Architecture is required for deployment")
            
            # Phase 1: Generate deployment configurations
            self.logger.info("📦 Generating deployment configurations...")
            config_files = await self._generate_deployment_configs(architecture)
            
            # Phase 2: Deploy to Railway (backend)
            self.logger.info("🚂 Deploying backend to Railway...")
            backend_deployment = await self._deploy_to_railway(self.project_id)
            
            # Phase 3: Deploy to Vercel (frontend)
            self.logger.info("▲ Deploying frontend to Vercel...")
            frontend_deployment = await self._deploy_to_vercel(
                self.project_id,
                backend_deployment["url"]
            )
            
            self.deployments_executed += 1
            
            self.logger.info(
                f"✅ Deployment complete:\n"
                f"  Backend: {backend_deployment['url']}\n"
                f"  Frontend: {frontend_deployment['url']}\n"
                f"  Cost: ₹{self.total_cost:.2f}"
            )
            
            return {
                "success": True,
                "deployment": {
                    "backend": backend_deployment,
                    "frontend": frontend_deployment
                },
                "config_files": config_files,
                "urls": {
                    "backend": backend_deployment["url"],
                    "frontend": frontend_deployment["url"]
                },
                "environment_variables": self._generate_env_vars(
                    backend_deployment["url"],
                    frontend_deployment["url"]
                ),
                "post_deployment_steps": self._generate_post_deployment_steps(
                    backend_deployment["url"]
                )
            }
            
        except Exception as e:
            self.logger.error(f"❌ Deployment failed: {e}")
            raise
    
    async def _generate_deployment_configs(
        self,
        architecture: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate all deployment configuration files using AI."""
        
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

Return ONLY valid JSON array, no markdown.
"""
        
        # Call AI Router directly
        response = await self.ai_router.generate(
            messages=[{"role": "user", "content": configs_prompt}],
            system_prompt=self.SYSTEM_PROMPT,
            task_type="deployment",
            complexity=TaskComplexity.MEDIUM,
            max_tokens=4000
        )
        
        # Log cost
        self.total_cost += response.cost_estimate
        self.logger.info(
            f"✅ Config generation: {response.output_tokens} tokens, "
            f"₹{response.cost_estimate:.4f}"
        )
        
        # Parse response
        return self._parse_json_response(response.content)
    
    async def _deploy_to_railway(self, project_id: str) -> Dict[str, Any]:
        """
        Deploy backend to Railway.
        
        NOTE: This is a MOCK implementation for v1.
        Real implementation would use Railway API.
        
        For production:
        1. Create Railway project via API
        2. Add PostgreSQL addon
        3. Deploy code from git or Docker
        4. Set environment variables
        5. Wait for deployment to complete
        6. Return deployment URL
        """
        
        self.logger.info("🚂 Railway deployment initiated (MOCK)")
        
        # Generate unique URL
        backend_url = f"https://nexsidi-{project_id[:8]}.railway.app"
        
        return {
            "platform": "Railway",
            "status": "deployed",
            "url": backend_url,
            "database_url": "postgresql://railway:***@containers-us-west.railway.app:5432/railway",
            "deployed_at": datetime.utcnow().isoformat()
        }
    
    async def _deploy_to_vercel(
        self, 
        project_id: str,
        backend_url: str
    ) -> Dict[str, Any]:
        """
        Deploy frontend to Vercel.
        
        NOTE: This is a MOCK implementation for v1.
        Real implementation would use Vercel API.
        
        For production:
        1. Create Vercel project via API
        2. Connect to git repository
        3. Set environment variables (VITE_API_URL)
        4. Trigger deployment
        5. Wait for build to complete
        6. Return deployment URL
        """
        
        self.logger.info("▲ Vercel deployment initiated (MOCK)")
        
        # Generate unique URL
        frontend_url = f"https://nexsidi-{project_id[:8]}.vercel.app"
        
        return {
            "platform": "Vercel",
            "status": "deployed",
            "url": frontend_url,
            "deployed_at": datetime.utcnow().isoformat(),
            "build_time": "45s",
            "edge_network": "enabled"
        }
    
    def _generate_env_vars(
        self,
        backend_url: str,
        frontend_url: str
    ) -> Dict[str, Any]:
        """Generate environment variables configuration."""
        
        return {
            "backend": {
                "DATABASE_URL": "Automatically set by Railway PostgreSQL addon",
                "JWT_SECRET": "Generate: openssl rand -hex 32",
                "CORS_ORIGINS": frontend_url,
                "ENVIRONMENT": "production"
            },
            "frontend": {
                "VITE_API_URL": f"{backend_url}/api/v1"
            }
        }
    
    def _generate_post_deployment_steps(self, backend_url: str) -> Dict[str, Any]:
        """Generate post-deployment checklist."""
        
        return {
            "database_migrations": f"Run: alembic upgrade head (via Railway console)",
            "health_check": f"GET {backend_url}/health",
            "admin_user": f"Create via: POST {backend_url}/api/auth/signup",
            "monitoring": "Configure error tracking (Sentry recommended)",
            "backups": "Railway PostgreSQL auto-backup enabled",
            "ssl": "Automatic HTTPS enabled on both platforms"
        }
    
    def _parse_json_response(self, ai_response: str) -> Any:
        """Parse JSON from AI response."""
        content = ai_response.strip()
        
        # Remove markdown code blocks
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
            self.logger.error(f"❌ Invalid JSON: {e}")
            self.logger.error(f"Response: {content[:500]}")
            raise ValueError(f"Invalid JSON response from AI: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get deployment statistics."""
        return {
            "deployments_executed": self.deployments_executed,
            "total_cost": self.total_cost
        }


if __name__ == "__main__":
    import asyncio
    
    async def test():
        pranav = Pranav(project_id="test-deploy-001")
        
        # Sample input
        input_data = {
            "architecture": {
                "backend": {
                    "framework": "FastAPI",
                    "database": "PostgreSQL",
                    "authentication": "JWT"
                },
                "frontend": {
                    "framework": "React",
                    "build_tool": "Vite",
                    "styling": "Tailwind"
                },
                "deployment": {
                    "backend_platform": "Railway",
                    "frontend_platform": "Vercel",
                    "database_platform": "Railway PostgreSQL"
                }
            }
        }
        
        result = await pranav.execute(input_data)
        print(json.dumps(result, indent=2))
        print(f"\nStatistics: {pranav.get_statistics()}")
    
    asyncio.run(test())