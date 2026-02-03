# =============================================================================
# SHUBHAM - BACKEND DEVELOPER (SPECIALIST)
# Location: app/agents/shubham.py
# Purpose: Generate backend code ONLY (FastAPI + Database)
# =============================================================================
#
# SHUBHAM'S SPECIALIZED ROLE IN THE PIPELINE:
# -------------------------------------------
# Saanvi (architect) designs the complete system
#   ↓
# **SHUBHAM TAKES OVER** ← We are here
#   ↓
# Implements BACKEND ONLY:
#   - Database models (SQLAlchemy code)
#   - API endpoints (FastAPI routes)
#   - Business logic (CRUD operations)
#   - Validation schemas (Pydantic)
#   - Configuration files (requirements.txt, .env.example)
#   ↓
# Saves to database (code_files table)
#   ↓
# Navya reviews the backend code
#
# WHAT SHUBHAM GENERATES (Backend Only):
# --------------------------------------
# ✅ backend/app/models.py - SQLAlchemy database models
# ✅ backend/app/schemas.py - Pydantic validation schemas
# ✅ backend/app/main.py - FastAPI application entry point
# ✅ backend/app/database.py - Database connection setup
# ✅ backend/app/security.py - Password hashing & JWT tokens
# ✅ backend/app/dependencies.py - Shared dependencies (auth, db)
# ✅ backend/app/routers/*.py - API endpoint implementations
# ✅ backend/requirements.txt - Python package dependencies
# ✅ backend/.env.example - Environment variable template
# ✅ backend/README.md - Backend documentation
#
# WHAT SHUBHAM DOES NOT GENERATE:
# -------------------------------
# ❌ Frontend (React/TypeScript) - That's Aanya's responsibility
# ❌ Deployment configs (Docker, Railway) - That's Pranav's responsibility
#
# WHY BACKEND-ONLY IS BETTER:
# ---------------------------
# Before: Shubham did backend + frontend + deployment = Overwhelmed
#         - Hit token limits (too much context)
#         - Lower quality (generalist vs specialist)
#         - Unrealistic (no real dev does everything)
#
# Now: Shubham focuses ONLY on backend = Excellence
#      - Deep expertise in Python/FastAPI
#      - Stays within token limits
#      - Higher quality output
#      - Mirrors real backend developers
#
# BASE64 ENCODING FIX:
# -------------------
# Problem: When AI returns code with newlines inside JSON strings,
#          JSON parsing fails due to literal newlines.
#
# Solution: Encode all file content as base64 BEFORE putting in JSON.
#           Base64 has no special characters, so JSON always parses.
#
# Flow:
# 1. AI generates Python code
# 2. AI encodes to base64
# 3. AI returns JSON with base64 string
# 4. We decode base64 → get original code
# 5. Save decoded code to database
#
# =============================================================================

from app.agents.base import BaseAgent
from typing import Dict, Any, List
import json
import base64  # For encoding/decoding file content


class Shubham(BaseAgent):
    """
    Backend Developer - Python and FastAPI specialist.
    
    Shubham is the "backend engineer" who implements the server-side
    of applications. He takes Saanvi's database and API designs and
    writes production-ready Python code.
    
    Think of him as a senior backend developer who:
    - Understands database modeling (SQLAlchemy ORM)
    - Writes clean, type-safe Python code
    - Implements RESTful APIs (FastAPI)
    - Follows security best practices
    - Uses base64 encoding to avoid JSON issues
    """
    
    # ==========================================================================
    # SYSTEM PROMPT - Defines Shubham's Personality and Expertise
    # ==========================================================================
    # This prompt is sent to the AI model to tell it HOW to behave as Shubham.
    # It's like giving instructions to a human backend developer.
    # ==========================================================================
    
    SYSTEM_PROMPT = """You are Shubham, a senior backend developer specializing in Python and FastAPI.

YOUR EXPERTISE:
---------------
Backend Technologies:
- Python 3.11+ with type hints and async/await
- FastAPI framework (routers, dependencies, middleware)
- SQLAlchemy ORM (models, relationships, queries)
- Pydantic (data validation, schemas)
- PostgreSQL database
- JWT authentication (JSON Web Tokens)
- RESTful API design patterns
- Error handling and logging

YOU ARE A SPECIALIST:
--------------------
You ONLY work on backend/server-side code.
You do NOT write frontend code (React, HTML, CSS).
You do NOT write deployment configs (Docker, Kubernetes).

Why? Because specialization = higher quality.
Real development teams have separate backend and frontend developers.

YOUR TASK:
---------
Implement the backend architecture designed by Saanvi (system architect).

Saanvi provides you with:
1. Database schema (what tables, columns, relationships)
2. API structure (what endpoints, request/response formats)

You turn these designs into working Python code.

WHAT YOU GENERATE (Backend Only):
---------------------------------
1. Database Models (models.py)
   - SQLAlchemy ORM models from Saanvi's schema
   - Proper relationships (one-to-many, many-to-many)
   - Database constraints (unique, not null, foreign keys)
   - Indexes for performance

2. Pydantic Schemas (schemas.py)
   - Request validation (what data can clients send?)
   - Response models (what data do we send back?)
   - Type safety (catch errors at development time)

3. API Routers (routers/*.py)
   - FastAPI endpoint implementations
   - Request handling (GET, POST, PUT, DELETE)
   - Error responses (404, 400, 500)
   - Authentication checks (is user logged in?)

4. Business Logic
   - CRUD operations (Create, Read, Update, Delete)
   - Data validation beyond Pydantic
   - Business rules (e.g., "can't delete user with active orders")

5. Security Components
   - Password hashing (bcrypt - never store plain passwords!)
   - JWT token generation and validation
   - Authentication dependencies

6. Configuration Files
   - requirements.txt (Python packages needed)
   - .env.example (environment variables template)
   - database.py (database connection setup)

WHAT YOU DO NOT GENERATE:
-------------------------
❌ Frontend code (React, TypeScript, HTML, CSS) - Aanya does this
❌ Dockerfile, docker-compose.yml - Pranav does this
❌ Deployment configs (Railway, Vercel) - Pranav does this

CODE QUALITY STANDARDS (Non-Negotiable):
----------------------------------------
1. Type Hints Everywhere
   Bad:  def get_user(id):
   Good: def get_user(id: UUID) -> User:
   
   Why? Catches bugs at development time, not production.

2. Async Functions for I/O Operations
   Bad:  def get_users(): return db.query(User).all()
   Good: async def get_users() -> List[User]: ...
   
   Why? Non-blocking - server can handle many requests simultaneously.

3. Proper Error Handling
   Bad:  user = db.query(User).first()  # What if not found?
   Good: user = db.query(User).first()
         if not user:
             raise HTTPException(status_code=404, detail="User not found")
   
   Why? Gives clear error messages to frontend/users.

4. Input Validation (Pydantic Models)
   Bad:  email = request.get("email")  # What if malformed?
   Good: class SignupRequest(BaseModel):
             email: EmailStr  # Validates email format automatically
   
   Why? Prevents bad data from entering database.

5. SQL Injection Prevention
   Bad:  db.execute(f"SELECT * FROM users WHERE email = '{email}'")
   Good: db.query(User).filter(User.email == email)
   
   Why? Raw SQL with user input = security vulnerability.

6. Password Hashing (bcrypt)
   Bad:  user.password = password  # NEVER store plain passwords!
   Good: user.password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
   
   Why? Database breach = all passwords compromised if not hashed.

7. Environment Variables for Secrets
   Bad:  DATABASE_URL = "postgresql://user:pass@localhost/db"
   Good: DATABASE_URL = os.getenv("DATABASE_URL")
   
   Why? Don't commit secrets to Git. Use .env files.

8. Comprehensive Docstrings
   Every function should explain:
   - What it does
   - What parameters it takes
   - What it returns
   - What errors it might raise

CRITICAL - BASE64 OUTPUT FORMAT:
--------------------------------
To avoid JSON encoding issues with newlines, quotes, and special characters,
you MUST encode all file content as base64 before returning JSON.

WHY BASE64?
- JSON strings cannot contain literal newlines
- Code has lots of newlines
- Escaping is error-prone and often fails
- Base64 has NO special characters
- Always produces valid JSON

OUTPUT FORMAT:
{
    "file_path": "backend/app/models.py",
    "file_content_base64": "BASE64_ENCODED_CONTENT_HERE",
    "file_type": "python",
    "description": "SQLAlchemy database models with relationships"
}

HOW TO CREATE BASE64:
1. Write your complete Python code as a string
2. Encode to base64: base64.b64encode(code.encode()).decode()
3. Put the base64 string in file_content_base64 field
4. Do NOT put raw code with newlines in JSON

EXAMPLE CONVERSION:
```python
# Original code (what you write):
code = '''from sqlalchemy import Column, String
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True)
'''

# Convert to base64:
import base64
encoded = base64.b64encode(code.encode()).decode()
# Result: "ZnJvbSBzcWxhbGNoZW15IGltcG9ydCBDb2x1bW4sIFN0cmluZwpmcm9tIGRhdGFiYXNlIGltcG9ydCBCYXNlCgpjbGFzcyBVc2VyKEJhc2UpOgogICAgX190YWJsZW5hbWVfXyA9ICJ1c2VycyIKICAgIGlkID0gQ29sdW1uKFN0cmluZywgcHJpbWFyeV9rZXk9VHJ1ZSk="

# Return this in JSON:
{
    "file_path": "backend/app/models.py",
    "file_content_base64": "ZnJvbSBzcWxhbGNoZW15IGltcG9ydCBDb2x1bW4sIFN0cmluZwpmcm9tIGRhdGFiYXNlIGltcG9ydCBCYXNlCgpjbGFzcyBVc2VyKEJhc2UpOgogICAgX190YWJsZW5hbWVfXyA9ICJ1c2VycyIKICAgIGlkID0gQ29sdW1uKFN0cmluZywgcHJpbWFyeV9rZXk9VHJ1ZSk=",
    "file_type": "python",
    "description": "User database model"
}
```

EXAMPLE DATABASE MODEL (what you might generate):
-------------------------------------------------
```python
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from database import Base
import uuid
from datetime import datetime

class User(Base):
    \"\"\"
    User account model.
    
    Represents a registered user in the system.
    Used for authentication and linking to other entities.
    \"\"\"
    
    # Table name in PostgreSQL
    __tablename__ = "users"
    
    # Columns
    id = Column(
        UUID(as_uuid=True),  # Use UUID type for PostgreSQL
        primary_key=True,    # This is the primary key
        default=uuid.uuid4   # Auto-generate UUID on creation
    )
    
    email = Column(
        String(255),         # Max 255 characters
        unique=True,         # No duplicate emails
        nullable=False,      # Required field
        index=True           # Create index for fast lookups
    )
    
    password_hash = Column(
        String(255),         # Hashed password (never store plain text!)
        nullable=False       # Required field
    )
    
    full_name = Column(
        String(200),         # Optional name field
        nullable=True
    )
    
    is_active = Column(
        Boolean,             # True/False
        default=True         # New users are active by default
    )
    
    created_at = Column(
        DateTime,            # Timestamp
        default=datetime.utcnow  # Auto-set on creation
    )
    
    # Relationships
    # One user can have many reservations
    reservations = relationship(
        "Reservation",                    # Related model
        back_populates="user",            # Reverse relationship name
        cascade="all, delete-orphan"      # Delete reservations if user deleted
    )
    
    def __repr__(self):
        \"\"\"String representation for debugging\"\"\"
        return f"<User {self.email}>"
```

EXAMPLE PYDANTIC SCHEMA (what you might generate):
--------------------------------------------------
```python
from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from datetime import datetime

class UserSignupRequest(BaseModel):
    \"\"\"
    Schema for user signup request.
    
    Validates incoming data when user creates account.
    \"\"\"
    email: EmailStr  # Validates email format automatically
    password: str = Field(min_length=8, max_length=100)  # Password constraints
    full_name: str | None = None  # Optional field

class UserResponse(BaseModel):
    \"\"\"
    Schema for user data in API responses.
    
    Never include password_hash in responses!
    \"\"\"
    id: UUID
    email: EmailStr
    full_name: str | None
    is_active: bool
    created_at: datetime
    
    class Config:
        # Allow creating from SQLAlchemy models
        from_attributes = True
```

EXAMPLE API ROUTER (what you might generate):
---------------------------------------------
```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import MenuItem
from schemas import MenuItemResponse
from dependencies import get_current_user

# Create router with prefix and tags
router = APIRouter(
    prefix="/menu",      # All routes start with /menu
    tags=["Menu"]        # Groups in API docs
)

@router.get("/", response_model=List[MenuItemResponse])
async def get_menu_items(
    category: str | None = None,       # Optional query parameter
    db: Session = Depends(get_db)      # Inject database session
):
    \"\"\"
    Get all menu items, optionally filtered by category.
    
    Args:
        category: Optional category filter (e.g., "appetizers", "mains")
        db: Database session (injected automatically)
    
    Returns:
        List of menu items
    
    Example:
        GET /menu?category=appetizers
        
        Returns:
        [
            {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Bruschetta",
                "description": "Toasted bread with tomatoes",
                "price": 8.99,
                "category": "appetizers"
            }
        ]
    \"\"\"
    
    # Build query
    query = db.query(MenuItem).filter(MenuItem.is_available == True)
    
    # Apply category filter if provided
    if category:
        query = query.filter(MenuItem.category == category)
    
    # Execute query and return results
    items = query.all()
    return items


@router.post("/", response_model=MenuItemResponse, status_code=status.HTTP_201_CREATED)
async def create_menu_item(
    item: MenuItemCreate,                              # Request body (validated by Pydantic)
    db: Session = Depends(get_db),                     # Database session
    current_user: User = Depends(get_current_user)    # Requires authentication
):
    \"\"\"
    Create a new menu item.
    
    Requires authentication (admin only in real app).
    
    Args:
        item: Menu item data from request body
        db: Database session
        current_user: Authenticated user (from JWT token)
    
    Returns:
        Created menu item
    
    Raises:
        HTTPException: 401 if not authenticated
        HTTPException: 400 if validation fails
    \"\"\"
    
    # Create database model from Pydantic schema
    db_item = MenuItem(**item.dict())
    
    # Save to database
    db.add(db_item)
    db.commit()
    db.refresh(db_item)  # Get ID assigned by database
    
    return db_item
```

IMPORTANT REMINDERS:
-------------------
1. Write COMPLETE, WORKING code (not pseudocode or TODOs)
2. Include ALL necessary imports at the top
3. Add type hints to EVERY function
4. Handle errors gracefully (never let app crash)
5. Use environment variables for configuration
6. Follow Python PEP 8 style guide
7. Add helpful docstrings explaining what code does
8. Implement proper authentication checks on protected endpoints
9. Use database transactions (commit/rollback)
10. ENCODE ALL FILE CONTENT AS BASE64 BEFORE RETURNING JSON
11. NEVER generate frontend code - that's Aanya's job!
"""
    
    # ==========================================================================
    # EXECUTE METHOD - Main Entry Point
    # ==========================================================================
    # This is called when the API triggers Shubham to generate backend code.
    # ==========================================================================
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate complete backend codebase.
        
        WHAT THIS METHOD DOES:
        ---------------------
        1. Receive architecture from Saanvi (database schema + API structure)
        2. Plan which backend files need to be created
        3. Generate each file using AI (models, routers, schemas, etc)
        4. Decode base64 content from AI
        5. Save decoded files to database (code_files table)
        6. Return manifest of all files created
        
        INPUT FORMAT:
        ------------
        {
            "architecture": {
                "database_architecture": {
                    "tables": [...],  # From Saanvi
                },
                "api_architecture": {
                    "endpoints": [...],  # From Saanvi
                }
            },
            "project_id": "uuid-here"
        }
        
        OUTPUT FORMAT:
        -------------
        {
            "success": true,
            "backend_files": 12,  # Number of files generated
            "file_manifest": [
                {
                    "path": "backend/app/models.py",
                    "type": "python",
                    "lines": 150,
                    "file_id": "uuid"
                },
                ...
            ],
            "structure": {
                "files": [...]  # Complete file structure
            },
            "generation_id": "task-uuid"  # For tracking
        }
        
        GENERATION PROCESS:
        ------------------
        Phase 1: Planning
          - Determine which files are needed
          - Create file structure (models.py, routers/auth.py, etc)
          - Sort by priority (core files first)
        
        Phase 2: Generation (Iterative)
          - Generate one file at a time
          - Use AI to write actual code
          - AI returns base64-encoded content
          - Decode base64 to get original code
          - Pass context from previous files
          - Save each file to database
        
        Phase 3: Return Results
          - Compile manifest of all files
          - Log completion with statistics
          - Return to caller (API endpoint or workflow orchestrator)
        
        WHY ITERATIVE GENERATION?
        ------------------------
        We generate files one at a time instead of all at once because:
        1. Token limits - Can't fit 15 files in one AI call
        2. Context - Later files can reference earlier files
        3. Error handling - If one file fails, others still succeed
        4. Progress tracking - Can show "Generating 3/15 files..."
        
        WHY BASE64 ENCODING?
        -------------------
        Problem: AI generates code with newlines like this:
        {
            "file_content": "line1
            line2
            line3"
        }
        ❌ This breaks JSON parsing (literal newlines not allowed)
        
        Solution: AI encodes to base64:
        {
            "file_content_base64": "bGluZTEKbGluZTIKbGluZTMK"
        }
        ✅ Always valid JSON, we decode to get original code
        
        EXAMPLE WORKFLOW:
        ----------------
        1. API receives request: "Generate backend for restaurant app"
        2. Calls: await shubham.execute({"architecture": saanvi_output})
        3. Shubham plans: "Need 12 files (models, 3 routers, schemas, etc)"
        4. Shubham generates each file using AI
        5. Shubham decodes base64 content
        6. Shubham saves files to code_files table
        7. Returns: "Generated 12 backend files successfully"
        8. Workflow orchestrator calls Navya to review the code
        """
        
        # Step 1: Log that we're starting
        # This creates a record in agent_tasks table
        # Status will be updated to 'completed' or 'failed' at the end
        task_id = await self.log_task(
            task_type="backend_generation",
            status="running",
            input_data={"project_id": input_data.get("project_id")}
        )
        
        try:
            # Step 2: Extract inputs
            architecture = input_data.get("architecture", {})
            project_id = input_data.get("project_id")
            
            # Validate we have architecture
            if not architecture:
                raise ValueError("Architecture missing from input - cannot generate without Saanvi's design")
            
            # Extract the parts Shubham needs
            db_arch = architecture.get("database_architecture", {})  # Table designs
            api_arch = architecture.get("api_architecture", {})      # Endpoint designs
            
            # Step 3: Plan backend file structure
            print("📁 Planning backend structure...")
            structure = self._plan_backend_structure(db_arch, api_arch)
            
            # Step 4: Generate files iteratively
            print(f"📝 Generating {len(structure['files'])} backend files...")
            files_generated = []
            
            for file_spec in structure["files"]:
                print(f"   Generating: {file_spec['path']}")
                
                # Generate this specific file using AI
                # AI will return base64-encoded content
                file_result = await self._generate_backend_file(
                    file_spec=file_spec,
                    db_arch=db_arch,
                    api_arch=api_arch,
                    context=files_generated  # Pass already-generated files for context
                )
                
                # Decode base64 content to get original code
                # This is where we convert: "bGluZTEK..." → "line1\nline2\n..."
                file_content = self._decode_base64_content(file_result)
                
                # Save decoded content to database (code_files table)
                file_id = await self._save_file(
                    project_id=project_id,
                    file_path=file_result["file_path"],
                    file_content=file_content,  # ← Decoded, human-readable code
                    file_type=file_result["file_type"]
                )
                
                # Add to manifest
                files_generated.append({
                    "path": file_result["file_path"],
                    "type": file_result["file_type"],
                    "lines": len(file_content.split("\n")),
                    "file_id": file_id
                })
            
            # Step 5: Log successful completion
            await self.log_task(
                task_type="backend_generation",
                status="completed",
                output_data={
                    "files_count": len(files_generated),
                    "file_types": list(set(f["type"] for f in files_generated))
                }
            )
            
            # Step 6: Return success
            return {
                "success": True,
                "backend_files": len(files_generated),
                "file_manifest": files_generated,
                "structure": structure,
                "generation_id": task_id
            }
            
        except Exception as e:
            # Something went wrong - log failure
            await self.log_task(
                task_type="backend_generation",
                status="failed",
                output_data={"error": str(e)}
            )
            
            # Return error (don't crash - let caller handle it)
            return {
                "success": False,
                "error": str(e),
                "generation_id": task_id
            }
    
    # ==========================================================================
    # HELPER METHODS - Internal Functions
    # ==========================================================================
    
    def _plan_backend_structure(
        self,
        db_arch: Dict[str, Any],
        api_arch: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Plan which backend files need to be created.
        
        WHAT THIS DOES:
        --------------
        Based on Saanvi's architecture, determine the complete file structure
        for the backend. Think of this as creating a blueprint before building.
        
        INPUT:
        -----
        db_arch: Database architecture from Saanvi
        api_arch: API architecture from Saanvi
        
        OUTPUT:
        ------
        {
            "files": [
                {
                    "path": "backend/app/models.py",
                    "type": "python",
                    "priority": 1,
                    "purpose": "Database models"
                },
                ...
            ]
        }
        
        FILE STRUCTURE EXPLAINED:
        ------------------------
        Standard FastAPI project structure:
        
        backend/
        ├── app/
        │   ├── main.py              # FastAPI app entry point
        │   ├── database.py          # Database connection
        │   ├── models.py            # SQLAlchemy models (ALL tables)
        │   ├── schemas.py           # Pydantic schemas (ALL endpoints)
        │   ├── dependencies.py      # Shared dependencies (auth, db)
        │   ├── security.py          # Password hashing, JWT
        │   └── routers/
        │       ├── auth.py          # Authentication endpoints
        │       ├── menu.py          # Menu-related endpoints
        │       └── reservations.py  # Reservation endpoints
        ├── requirements.txt         # Python packages
        ├── .env.example            # Environment variables template
        └── README.md               # Documentation
        
        PRIORITY SYSTEM:
        ---------------
        1 = Core/Foundation (must generate first)
            - database.py, models.py, schemas.py
            Why first? Other files depend on these
        
        2 = Application Setup
            - main.py, dependencies.py, security.py
            Why second? Uses models/schemas from priority 1
        
        3 = Business Logic
            - routers/*.py (actual endpoints)
            Why third? Uses everything from 1 and 2
        
        4 = Configuration
            - requirements.txt, .env.example
            Why fourth? Just config, no code dependencies
        
        5 = Documentation
            - README.md
            Why last? References everything else
        
        ROUTER GROUPING LOGIC:
        ---------------------
        We create one router file per endpoint group.
        
        Example: If API has these endpoints:
        - /auth/signup
        - /auth/login
        - /menu (GET)
        - /menu (POST)
        - /reservations (GET)
        - /reservations (POST)
        
        We create:
        - routers/auth.py (signup, login)
        - routers/menu.py (GET menu, POST menu)
        - routers/reservations.py (GET reservations, POST reservations)
        
        Why group? Keeps related endpoints together, easier to maintain.
        """
        
        # Start with core files (every FastAPI app needs these)
        files = [
            {
                "path": "backend/app/database.py",
                "type": "python",
                "priority": 1,
                "purpose": "Database connection and session management"
            },
            {
                "path": "backend/app/models.py",
                "type": "python",
                "priority": 1,
                "purpose": "SQLAlchemy ORM models for all tables"
            },
            {
                "path": "backend/app/schemas.py",
                "type": "python",
                "priority": 1,
                "purpose": "Pydantic validation schemas for all endpoints"
            },
            {
                "path": "backend/app/main.py",
                "type": "python",
                "priority": 2,
                "purpose": "FastAPI application entry point with CORS and routers"
            },
            {
                "path": "backend/app/dependencies.py",
                "type": "python",
                "priority": 2,
                "purpose": "Shared dependencies for authentication and database"
            },
            {
                "path": "backend/app/security.py",
                "type": "python",
                "priority": 2,
                "purpose": "Password hashing (bcrypt) and JWT token handling"
            },
        ]
        
        # Analyze API endpoints and group into routers
        # Example: /auth/signup, /auth/login → routers/auth.py
        endpoint_groups = {}
        for endpoint in api_arch.get("endpoints", []):
            # Split path: /auth/signup → ["", "auth", "signup"]
            path_parts = endpoint["path"].split("/")
            
            if len(path_parts) > 1:
                # Get first part after leading slash
                group = path_parts[1]  # "auth", "menu", "reservations", etc
                
                # Create group if doesn't exist
                if group not in endpoint_groups:
                    endpoint_groups[group] = []
                
                # Add endpoint to this group
                endpoint_groups[group].append(endpoint)
        
        # Create one router file per group
        for group in endpoint_groups:
            files.append({
                "path": f"backend/app/routers/{group}.py",
                "type": "python",
                "priority": 3,
                "purpose": f"API routes for {group} functionality"
            })
        
        # Add configuration files
        files.extend([
            {
                "path": "backend/requirements.txt",
                "type": "text",
                "priority": 4,
                "purpose": "Python package dependencies (fastapi, sqlalchemy, etc)"
            },
            {
                "path": "backend/.env.example",
                "type": "text",
                "priority": 4,
                "purpose": "Environment variables template (DATABASE_URL, JWT_SECRET)"
            },
            {
                "path": "backend/README.md",
                "type": "markdown",
                "priority": 5,
                "purpose": "Backend documentation and setup instructions"
            }
        ])
        
        # Sort by priority (generate core files first)
        files.sort(key=lambda x: x["priority"])
        
        return {"files": files}
    
    async def _generate_backend_file(
        self,
        file_spec: Dict[str, Any],
        db_arch: Dict[str, Any],
        api_arch: Dict[str, Any],
        context: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate code for a single backend file using AI.
        
        WHAT THIS DOES:
        --------------
        Uses AI (Claude or Gemini) to write actual code for one file.
        Sends the file specification + architecture to AI, gets back
        base64-encoded code in JSON format.
        
        PARAMETERS:
        ----------
        file_spec: Specification for this file
            {
                "path": "backend/app/models.py",
                "type": "python",
                "purpose": "Database models"
            }
        
        db_arch: Database architecture from Saanvi
        api_arch: API architecture from Saanvi
        context: Previously generated files (for reference)
        
        RETURNS:
        -------
        {
            "file_path": "backend/app/models.py",
            "file_content_base64": "ZnJvbSBzcWxhbGNoZW15...",  # Base64-encoded
            "file_type": "python",
            "description": "SQLAlchemy models with relationships"
        }
        
        HOW IT WORKS:
        ------------
        1. Build context from previous files
           Example: If generating routers/auth.py, AI can see that
           models.py was already generated with User model
        
        2. Create detailed prompt for AI
           - What file to generate
           - What it should contain
           - Reference to database/API architecture
           - Context from previous files
           - CRITICAL: Instruct to return base64-encoded content
        
        3. Call AI with system prompt + generation prompt
           - System prompt: "You are Shubham, backend developer..."
           - User prompt: "Generate models.py with these tables..."
        
        4. AI writes code, encodes to base64, returns JSON
        
        5. Parse JSON, extract base64 content
        
        6. Return to caller (who will decode base64)
        
        WHY PASS CONTEXT?
        ----------------
        Later files can reference earlier files.
        
        Example:
        - First generate models.py (User, MenuItem models)
        - Then generate routers/menu.py
        - Router needs to import MenuItem from models.py
        - AI sees "models.py was generated with MenuItem class"
        - AI writes: "from app.models import MenuItem"
        
        Without context, AI might not know class names to import!
        
        TOKEN MANAGEMENT:
        ----------------
        We only pass last 3 files as context to avoid hitting token limits.
        Full context could be 10+ files × 200 lines each = too much.
        Last 3 files usually provides enough context.
        
        BASE64 ENCODING:
        ---------------
        We explicitly tell AI to encode content as base64.
        This prevents JSON parsing errors from newlines/quotes in code.
        """
        
        # Build context string from previously generated files
        context_str = ""
        if context:
            context_str = "\n\nPREVIOUSLY GENERATED FILES (for reference):\n"
            # Only use last 3 files to avoid token limit
            for prev in context[-3:]:
                context_str += f"- {prev['path']} ({prev['lines']} lines)\n"
        
        # Build comprehensive prompt for AI
        generation_prompt = f"""
Generate backend code for this file:

FILE SPECIFICATION:
Path: {file_spec['path']}
Type: {file_spec['type']}
Purpose: {file_spec['purpose']}

DATABASE ARCHITECTURE (from Saanvi):
{json.dumps(db_arch, indent=2)}

API ARCHITECTURE (from Saanvi):
{json.dumps(api_arch, indent=2)}
{context_str}

Generate COMPLETE, PRODUCTION-READY Python code for this file.

Requirements:
- Include ALL necessary imports
- Add type hints to every function
- Handle errors gracefully (HTTPException with details)
- Add comprehensive docstrings
- Follow FastAPI/SQLAlchemy best practices
- Use async for database operations
- Implement proper validation
- Never hardcode secrets (use environment variables)

CRITICAL - BASE64 ENCODING:
Your response MUST use base64 encoding for file content.
This prevents JSON parsing errors from newlines and special characters.

Steps:
1. Write complete Python code
2. Encode to base64: base64.b64encode(code.encode()).decode()
3. Return JSON with file_content_base64 field

Return JSON format:
{{
    "file_path": "{file_spec['path']}",
    "file_content_base64": "BASE64_ENCODED_CODE_HERE",
    "file_type": "{file_spec['type']}",
    "description": "brief description of what this file does"
}}

DO NOT return raw code with newlines in JSON.
DO encode to base64 first.
"""
        
        # Call AI to generate code
        # Uses base class call_ai() method (from BaseAgent)
        # Complexity 8 = high (code generation is complex)
        # max_tokens 4000 = allow long files
        ai_response = await self.call_ai(
            messages=[
                {"role": "system", "content": self.SYSTEM_PROMPT},  # Shubham's personality
                {"role": "user", "content": generation_prompt}       # What to generate
            ],
            complexity=8,     # High complexity
            max_tokens=4000   # Allow up to 4000 tokens (~3000 words)
        )
        
        # Parse AI response (extract JSON from possible markdown)
        return self._parse_json_response(ai_response["content"])
    
    def _decode_base64_content(self, file_result: Dict[str, Any]) -> str:
        """
        Decode base64 file content.
        
        WHAT THIS DOES:
        --------------
        Converts base64-encoded string back to original code.
        
        Example:
        Input:  "ZnJvbSBzcWxhbGNoZW15IGltcG9ydCBDb2x1bW4K..."
        Output: "from sqlalchemy import Column\n..."
        
        PARAMETERS:
        ----------
        file_result: Dict from AI with either:
            - file_content_base64 (preferred - new format)
            - file_content (fallback - if AI didn't use base64)
        
        RETURNS:
        -------
        Decoded file content as string (human-readable code)
        
        ERROR HANDLING:
        --------------
        - If base64 decoding fails, raises ValueError with details
        - If neither field exists, raises ValueError
        - Handles UTF-8 encoding issues
        
        WHY FALLBACK TO PLAIN CONTENT?
        ------------------------------
        Sometimes AI might not follow instructions and return
        plain text instead of base64. We handle both cases:
        
        1. Try base64 first (preferred)
        2. Fall back to plain content if no base64
        3. Error if neither exists
        
        This makes the system more robust to AI mistakes.
        """
        # Try base64 first (preferred format)
        if "file_content_base64" in file_result:
            try:
                # Get the base64 string
                encoded = file_result["file_content_base64"]
                
                # Decode from base64 to bytes
                decoded_bytes = base64.b64decode(encoded)
                
                # Convert bytes to UTF-8 string
                return decoded_bytes.decode('utf-8')
                
            except Exception as e:
                # Base64 decoding failed - provide helpful error
                raise ValueError(
                    f"Failed to decode base64 content: {e}\n"
                    f"File: {file_result.get('file_path', 'unknown')}"
                )
        
        # Fallback to plain content (if AI didn't use base64)
        elif "file_content" in file_result:
            print(f"⚠️ Warning: AI returned plain content instead of base64 for {file_result.get('file_path')}")
            return file_result["file_content"]
        
        # Neither field exists - error
        else:
            raise ValueError(
                f"AI response missing both file_content_base64 and file_content\n"
                f"File: {file_result.get('file_path', 'unknown')}\n"
                f"Available keys: {list(file_result.keys())}"
            )
    
    async def _save_file(
        self,
        project_id: str,
        file_path: str,
        file_content: str,
        file_type: str
    ) -> str:
        """
        Save generated file to database.
        
        WHAT THIS DOES:
        --------------
        Saves the generated code to the code_files table in database.
        This allows:
        1. Version control (can track changes)
        2. Review by Navya (QA agent)
        3. Deployment by Pranav (DevOps agent)
        4. Retrieval by user (download code)
        
        PARAMETERS:
        ----------
        project_id: Which project this file belongs to
        file_path: Path like "backend/app/models.py"
        file_content: Actual code content (decoded, human-readable)
        file_type: "python", "text", "markdown", etc
        
        RETURNS:
        -------
        file_id: UUID of saved file (for tracking)
        
        DATABASE RECORD:
        ---------------
        Saved to code_files table with:
        - id: UUID (auto-generated)
        - project_id: Links to projects table
        - file_path: Where file goes in project structure
        - file_content: Actual code (decoded, ready to use)
        - file_type: Language/type
        - created_by_agent: "shubham" (who generated it)
        - version: 1 (for future versioning)
        - created_at: Timestamp
        
        WHY SAVE TO DATABASE?
        --------------------
        Alternative would be writing directly to filesystem, but database is better:
        1. Multi-user: Many projects can be generated simultaneously
        2. Isolation: Projects don't interfere with each other
        3. Review: Navya can review before deployment
        4. Versioning: Can track changes over time
        5. Deployment: Pranav can pull files when deploying
        6. Security: Files isolated per project/user
        """
        from app.models import CodeFile
        from uuid import uuid4
        
        # Create database model instance
        code_file = CodeFile(
            id=uuid4(),                      # Generate new UUID
            project_id=project_id,           # Link to project
            file_path=file_path,             # Where this file goes
            file_content=file_content,       # Actual code (decoded)
            file_type=file_type,             # Language/type
            created_by_agent="shubham",      # Track who generated it
            version=1                        # Initial version
        )
        
        # Save to database
        self.db.add(code_file)          # Stage for insertion
        self.db.commit()                # Actually insert into database
        self.db.refresh(code_file)      # Get ID that database assigned
        
        # Return the file ID (for tracking)
        return str(code_file.id)
    
    def _parse_json_response(self, ai_response: str) -> Dict[str, Any]:
        """
        Extract JSON from AI response (handles markdown formatting).
        
        WHAT THIS DOES:
        --------------
        AI sometimes returns JSON wrapped in markdown code blocks:
        ```json
        {"key": "value"}
        ```
        
        This method extracts just the JSON part.
        
        PARAMETERS:
        ----------
        ai_response: Raw response from AI
        
        RETURNS:
        -------
        Parsed dictionary from JSON
        
        COMMON FORMATS:
        --------------
        Format 1: Just JSON
            {"file_path": "..."}
        
        Format 2: Markdown with language
            ```json
            {"file_path": "..."}
            ```
        
        Format 3: Markdown without language
            ```
            {"file_path": "..."}
            ```
        
        All three are handled by this method.
        
        ERROR HANDLING:
        --------------
        If JSON is malformed, raises ValueError with:
        - What went wrong
        - First 500 chars of content (for debugging)
        """
        content = ai_response.strip()
        
        # Remove markdown code blocks if present
        if content.startswith("```json"):
            content = content[7:]  # Remove ```json
        if content.startswith("```"):
            content = content[3:]  # Remove ```
        if content.endswith("```"):
            content = content[:-3]  # Remove closing ```
        
        content = content.strip()
        
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            # JSON parsing failed - provide helpful error
            raise ValueError(
                f"AI returned invalid JSON\n"
                f"Error: {e}\n"
                f"Content preview: {content[:500]}..."
            )


# =============================================================================
# END OF SHUBHAM (FULLY DOCUMENTED + BASE64 FIX)
# =============================================================================
#
# WHAT'S NEXT?
# -----------
# 1. Shubham generates backend files (with base64 encoding)
# 2. Files saved to code_files table (decoded, ready to use)
# 3. Aanya (frontend developer) generates frontend files
# 4. Navya (QA) reviews ALL code (backend + frontend)
# 5. If approved, Pranav (DevOps) deploys everything
#
# =============================================================================
