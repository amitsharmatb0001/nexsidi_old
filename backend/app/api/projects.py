from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.database import get_db
from app.models import User, Project
from app.schemas import ProjectCreate, ProjectResponse
from app.dependencies import get_current_user

router = APIRouter()


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create new project
    
    When does this happen?
    - User has chatted with Tilotma
    - User decides to proceed with building something
    - We create formal project entry
    
    Initial state:
    - status: 'requirements_gathering'
    - current_agent: 'saanvi' (requirements analysis)
    - No price quoted yet
    """
    new_project = Project(
        user_id=current_user.id,
        title=project_data.title,
        description=project_data.description,
        status="requirements_gathering",
        current_agent="saanvi"
    )
    
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    
    return new_project


@router.get("/", response_model=List[ProjectResponse])
async def list_projects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all projects for current user
    
    Why filter by user_id?
    - Security: Users should only see their own projects
    - Multi-tenancy: Each user has isolated data
    
    Returns empty list if user has no projects yet
    """
    projects = db.query(Project).filter(Project.user_id == current_user.id).all()
    return projects


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get specific project details
    
    Security check:
    - Verify project exists
    - Verify project belongs to current user
    - Return 404 if not found or unauthorized (don't reveal if it exists)
    """
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id  # Important: prevent accessing others' projects
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete project (and all related data due to CASCADE)
    
    What gets deleted?
    - Project row
    - All conversations (CASCADE)
    - All agent_tasks (CASCADE)
    - All deployments (CASCADE)
    - All code_files (CASCADE)
    
    Why 204 No Content?
    - Successful deletion returns nothing
    - Standard REST practice
    """
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db.delete(project)
    db.commit()
    
    return None  # FastAPI converts this to 204