from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.services.ai_router import ai_router, TaskComplexity
from app.models import AgentTask, Conversation
from uuid import UUID
from datetime import datetime

# Why abstract base class?
# - Enforces consistent interface across all agents
# - Shared functionality (logging, AI calls, etc)
# - Easy to add new agents - just inherit and implement execute()


class BaseAgent(ABC):
    """
    Foundation for all NexSidi agents
    
    All agents (Tilotma, Saanvi, Shubham, Navya, Pranav) inherit from this
    
    Shared capabilities:
    - Call AI models via router
    - Log tasks to database
    - Track costs
    - Get project context
    """
    
    def __init__(self, db: Session, project_id: Optional[UUID] = None, user_id: Optional[UUID] = None):
        """
        Initialize agent
        
        Args:
            db: Database session
            project_id: Project this agent is working on (None for pre-project chat)
            user_id: User this agent is talking to
        """
        self.db = db
        self.project_id = project_id
        self.user_id = user_id
        self.agent_name = self.__class__.__name__.lower()  # 'tilotma', 'saanvi', etc
        self.ai_router = ai_router
    
    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main execution method - MUST be implemented by each agent
        
        Each agent has different logic:
        - Tilotma: Chat with user, gather requirements
        - Saanvi: Analyze requirements, calculate complexity, quote price
        - Shubham: Generate code based on specs
        - Navya: Review code, suggest improvements
        - Pranav: Deploy to hosting platform
        
        Args:
            input_data: Agent-specific input
        
        Returns:
            Agent-specific output
        """
        pass
    
    async def call_ai(
        self,
        messages: list,
        complexity: int = 5,
        is_critical: bool = False,
        max_tokens: int = 4000
    ) -> Dict[str, Any]:
        """
        Call appropriate AI model based on task complexity
        
        This is the MAIN way agents interact with AI
        
        Example usage:
        response = await self.call_ai(
            messages=[
                {"role": "user", "content": "Explain React hooks"}
            ],
            complexity=4
        )
        ai_text = response["content"]
        """
        # Map 1-10 complexity to TaskComplexity enum
        if complexity <= 3:
            level = TaskComplexity.SIMPLE
        elif complexity <= 7:
            level = TaskComplexity.MEDIUM
        else:
            level = TaskComplexity.COMPLEX
        
        # Critical tasks always use COMPLEX
        if is_critical:
            level = TaskComplexity.COMPLEX
        
        # Router handles model selection internally
        response = await self.ai_router.generate(
            messages=messages,
            task_type="general",
            complexity=level,
            max_tokens=max_tokens
        )
        
        return {
            "content": response.content,
            "model": response.model_id,
            "tokens_used": response.output_tokens,
            "cost_inr": response.cost_estimate
        }
    
    async def log_task(
        self,
        task_type: str,
        status: str,
        input_data: Optional[Dict] = None,
        output_data: Optional[Dict] = None,
        ai_response: Optional[Dict] = None
    ) -> UUID:
        """
        Log agent activity to database
        
        Why log everything?
        - Cost tracking (know exactly what you spent)
        - Debugging (see what agent did)
        - Analytics (which tasks take longest?)
        - Audit trail (for customer disputes)
        
        Args:
            task_type: 'requirements_gathering', 'code_generation', etc
            status: 'running', 'completed', 'failed'
            input_data: What agent received
            output_data: What agent produced
            ai_response: AI model response (contains cost, tokens)
        """
        task = AgentTask(
            project_id=self.project_id,
            agent_name=self.agent_name,
            task_type=task_type,
            status=status,
            input_data=input_data,
            output_data=output_data,
            started_at=datetime.utcnow() if status == "running" else None,
            completed_at=datetime.utcnow() if status in ["completed", "failed"] else None
        )
        
        # Add AI metrics if available
        if ai_response:
            task.model_used = ai_response.get("model")
            task.tokens_used = ai_response.get("tokens_used")
            task.cost_inr = ai_response.get("cost_inr")
        
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        
        return task.id
    
    async def save_message(
        self,
        role: str,
        content: str,
        meta_info: Optional[Dict] = None
    ) -> UUID:
        """
        Save conversation message to database
        
        Args:
            role: 'user' or 'assistant'
            content: Message text
            meta_info: Additional data (model used, tokens, etc)
        """
        message = Conversation(
            user_id=self.user_id,
            project_id=self.project_id,
            agent_name=self.agent_name,
            role=role,
            content=content,
            meta_info=meta_info
        )
        
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        
        return message.id
    
    def get_conversation_history(self, limit: int = 20) -> list:
        """
        Get recent conversation history
        
        Why needed?
        - AI needs context from previous messages
        - "Tell me more about the pricing" - needs to know what we discussed
        
        Returns:
        [
            {"role": "user", "content": "I want a website"},
            {"role": "assistant", "content": "Great! What kind?"},
            ...
        ]
        """
        # Build query based on what IDs we have
        query = self.db.query(Conversation)
        
        if self.project_id:
            query = query.filter(Conversation.project_id == self.project_id)
        elif self.user_id:
            query = query.filter(Conversation.user_id == self.user_id)
        
        query = query.filter(Conversation.agent_name == self.agent_name)
        query = query.order_by(Conversation.created_at.desc())
        query = query.limit(limit)
        
        messages = query.all()
        
        # Reverse to get chronological order
        return [
            {"role": msg.role, "content": msg.content}
            for msg in reversed(messages)
        ]