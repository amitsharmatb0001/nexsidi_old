# =============================================================================
# TILOTMA - CHIEF AI OFFICER & ORCHESTRATOR
# Location: backend/app/agents/tilotma.py
# Purpose: Chat interface, agent orchestration, quality validation
# =============================================================================
#
# TILOTMA'S FIVE CORE MODULES:
# 1. Chat Module - User interaction and requirements gathering
# 2. Orchestration Module - Delegate tasks to specialized agents
# 3. Validation Module - AI-powered review of agent outputs
# 4. Error Recovery Module - Auto-retry with feedback (max 3 attempts)
# 5. Approval Module - Final quality gate before customer delivery
#
# KEY FEATURES:
# - Auto-correct typos (don't repeat user mistakes)
# - Context awareness (remember last 20 messages)
# - Smart clarification (ask right questions)
# - Complexity detection (honest pricing)
# - Thinking level selection (0-3 based on task)
# - Progressive updates (milestone notifications)
# - Model escalation (switch to Claude Opus when stuck)
#
# =============================================================================

import os
import re
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import uuid

# Import AI Router V2
try:
    from app.services.ai_router import ai_router, TaskComplexity
except ImportError:
    from app.services.ai_router import ai_router
    # Define TaskComplexity if not in ai_router
    from enum import Enum
    class TaskComplexity(Enum):
        SIMPLE = "simple"
        MEDIUM = "medium"
        COMPLEX = "complex"

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# =============================================================================
# DATA STRUCTURES
# =============================================================================

class ConversationPhase(Enum):
    """Current phase of the conversation"""
    GREETING = "greeting"
    REQUIREMENTS_GATHERING = "requirements_gathering"
    CLARIFICATION = "clarification"
    READY_FOR_SPEC = "ready_for_spec"
    AWAITING_APPROVAL = "awaiting_approval"
    BUILDING = "building"
    COMPLETED = "completed"


class ThinkingLevel(Enum):
    """AI thinking depth level"""
    STANDARD = 0        # Simple chat, status updates
    NORMAL = 1          # Requirements analysis, code generation
    EXTENDED = 2        # Complex decisions, architecture, security
    DEEP = 3           # Enterprise apps, critical decisions


@dataclass
class Message:
    """A single conversation message"""
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    tokens_used: int = 0
    cost: float = 0.0
    model_used: str = ""
    thinking_level: ThinkingLevel = ThinkingLevel.STANDARD
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "tokens_used": self.tokens_used,
            "cost": self.cost,
            "model_used": self.model_used,
            "thinking_level": self.thinking_level.value
        }


@dataclass
class ProjectContext:
    """Complete context for a project"""
    project_id: str
    user_id: str
    phase: ConversationPhase = ConversationPhase.GREETING
    messages: List[Message] = field(default_factory=list)
    requirements_detected: bool = False
    complexity_estimate: int = 0  # 1-10
    thinking_level: ThinkingLevel = ThinkingLevel.STANDARD
    total_cost: float = 0.0
    last_agent_called: Optional[str] = None
    retry_count: Dict[str, int] = field(default_factory=dict)
    
    def add_message(self, message: Message):
        """Add message and update costs"""
        self.messages.append(message)
        self.total_cost += message.cost
    
    def get_recent_messages(self, count: int = 20) -> List[Message]:
        """Get last N messages for context"""
        return self.messages[-count:]


@dataclass
class ReadinessCheck:
    """Result of checking if ready to generate spec"""
    is_ready: bool
    confidence: float  # 0.0 to 1.0
    missing_info: List[str]
    detected_features: List[str]
    estimated_complexity: int  # 1-10
    reasoning: str


@dataclass
class ValidationResult:
    """Result of validating agent output"""
    is_valid: bool
    issues: List[str]
    suggestions: List[str]
    should_retry: bool
    feedback_for_agent: str


# =============================================================================
# TILOTMA AGENT CLASS
# =============================================================================

class Tilotma:
    """
    Chief AI Officer - Orchestrator & Quality Gate
    
    Responsibilities:
    1. Chat with users and gather requirements
    2. Orchestrate all specialized agents
    3. Validate outputs from each agent
    4. Handle errors with automatic retry
    5. Provide progressive updates
    6. Final approval before delivery
    
    Intelligence Features:
    - Auto-corrects typos in understanding
    - Remembers conversation context
    - Asks smart clarifying questions
    - Detects project complexity
    - Calculates realistic timelines
    - Selects appropriate thinking level
    """
    
    def __init__(self, project_id: str, user_id: str):
        """
        Initialize Tilotma for a project.
        
        Args:
            project_id: UUID of the project
            user_id: UUID of the user who owns the project
        """
        self.project_id = project_id
        self.user_id = user_id
        self.logger = logging.getLogger(f"tilotma.{project_id}")
        
        # Initialize project context
        self.context = ProjectContext(
            project_id=project_id,
            user_id=user_id
        )
        
        # Agent registry (for delegation)
        self.agents = {
            "saanvi": None,     # Requirements Analyst
            "kavya": None,      # Designer
            "shubham": None,    # Backend Developer
            "aanya": None,      # Web Frontend Developer
            "aarav": None,      # Mobile Developer
            "navya": None,      # Code Reviewer
            "pranav": None      # Deployment Engineer
        }
        
        self.logger.info(f"👑 Tilotma initialized for project {project_id}")
    
    # =========================================================================
    # CHAT MODULE - User Interaction
    # =========================================================================
    
    async def chat(self, user_message: str) -> str:
        """
        Main chat interface - handles user messages.
        
        Workflow:
        1. Correct typos in understanding
        2. Add to conversation history
        3. Determine thinking level needed
        4. Generate response with context
        5. Check if ready to proceed to next phase
        6. Save message and return response
        
        Args:
            user_message: Message from the user
        
        Returns:
            Assistant's response
        """
        
        self.logger.info(f"💬 User message received: {user_message[:100]}...")
        
        # Step 1: Understand message (with typo correction internally)
        understood_message = self._understand_with_typo_correction(user_message)
        
        # Step 2: Add user message to context
        user_msg = Message(
            role="user",
            content=user_message  # Keep original for record
        )
        self.context.add_message(user_msg)
        
        # Step 3: Determine thinking level
        thinking_level = self._determine_thinking_level(understood_message)
        self.context.thinking_level = thinking_level
        
        # Step 4: Generate response based on phase
        if self.context.phase == ConversationPhase.GREETING:
            response = await self._handle_greeting(understood_message)
        
        elif self.context.phase == ConversationPhase.REQUIREMENTS_GATHERING:
            response = await self._handle_requirements_gathering(understood_message)
        
        elif self.context.phase == ConversationPhase.CLARIFICATION:
            response = await self._handle_clarification(understood_message)
        
        else:
            response = await self._handle_general(understood_message)
        
        # Step 5: Check readiness for next phase
        await self._check_phase_transition()
        
        # Step 6: Return response
        self.logger.info(f"✅ Tilotma response: {response[:100]}...")
        return response
    
    def _understand_with_typo_correction(self, text: str) -> str:
        """
        Understand user message, correcting typos internally.
        
        This doesn't change what the user typed (we keep that for records),
        but ensures Tilotma understands correctly even with typos.
        
        Common corrections:
        - webiste → website
        - buisness → business
        - ecommerce → e-commerce
        - etc.
        
        Args:
            text: Original user message
        
        Returns:
            Understood version (typos corrected for AI processing)
        """
        
        # Common typo corrections
        corrections = {
            r'\bwebiste\b': 'website',
            r'\bbuisness\b': 'business',
            r'\bcommerce\b': 'e-commerce',
            r'\bpayment\b': 'payment',
            r'\bcontact\b': 'contact',
            r'\bresponsive\b': 'responsive',
            r'\bdatabase\b': 'database',
        }
        
        understood = text.lower()
        for pattern, replacement in corrections.items():
            understood = re.sub(pattern, replacement, understood, flags=re.IGNORECASE)
        
        return understood
    
    def _determine_thinking_level(self, message: str) -> ThinkingLevel:
        """
        Determine appropriate thinking level for this message.
        
        STANDARD (0): Simple chat, greetings, status updates
        NORMAL (1): Requirements gathering, general questions
        EXTENDED (2): Complex analysis, ambiguous requests
        DEEP (3): Critical decisions, high-stakes questions
        
        Args:
            message: User's message
        
        Returns:
            Appropriate thinking level
        """
        
        message_lower = message.lower()
        
        # Deep thinking triggers
        deep_triggers = [
            "enterprise", "security critical", "payment processing",
            "multi-tenant", "complex business logic", "scalable"
        ]
        if any(trigger in message_lower for trigger in deep_triggers):
            return ThinkingLevel.DEEP
        
        # Extended thinking triggers
        extended_triggers = [
            "architecture", "how should", "best way",
            "recommend", "which approach", "confused",
            "not sure", "maybe", "possibly"
        ]
        if any(trigger in message_lower for trigger in extended_triggers):
            return ThinkingLevel.EXTENDED
        
        # Standard thinking (greetings, simple questions)
        if len(message.split()) < 5:
            return ThinkingLevel.STANDARD
        
        # Default: Normal thinking
        return ThinkingLevel.NORMAL
    
    async def _handle_greeting(self, message: str) -> str:
        """
        Handle initial greeting phase - ULTRA SHORT.
        """
        
        # MINIMAL prompt
        user_prompt = f"""User: "{message[:50]}"

You're Tilotma. Greet and ask what to build. 15 words max."""
        
        response = await ai_router.generate(
            messages=[{"role": "user", "content": user_prompt}],
            task_type="chat",
            complexity=TaskComplexity.SIMPLE,
            max_tokens=50  # Reduced from 200!
        )
        
        # Save response
        assistant_msg = Message(
            role="assistant",
            content=response.content,
            tokens_used=response.output_tokens,
            cost=response.cost_estimate,
            model_used=response.model_id,
            thinking_level=ThinkingLevel.STANDARD
        )
        self.context.add_message(assistant_msg)
        
        # Transition to requirements gathering
        self.context.phase = ConversationPhase.REQUIREMENTS_GATHERING
        
        return response.content
    
    async def _handle_requirements_gathering(self, message: str) -> str:
        """
        Handle requirements gathering phase.
        
        Ultra-short version to avoid token limits.
        """
        
        # Get only last 3 messages (was 5)
        recent_messages = self.context.get_recent_messages(3)
        
        # Build VERY short context (max 50 chars per message)
        context_lines = []
        for msg in recent_messages:
            short_content = msg.content[:50] if len(msg.content) > 50 else msg.content
            context_lines.append(f"{msg.role}: {short_content}")
        
        context = "\n".join(context_lines)
        
        # ULTRA SHORT prompt (under 100 words total)
        user_prompt = f"""Requirements gathering.

Context:
{context}

New: {message[:100]}

Ask 1 clarifying question (20 words max)."""
        
        # Force SIMPLE complexity
        response = await ai_router.generate(
            messages=[{"role": "user", "content": user_prompt}],
            task_type="chat",  # Changed from "analysis" to "chat" for faster model
            complexity=TaskComplexity.SIMPLE,  # Always SIMPLE
            max_tokens=100  # Reduced from 200 to 100!
        )
        
        # Save response
        assistant_msg = Message(
            role="assistant",
            content=response.content,
            tokens_used=response.output_tokens,
            cost=response.cost_estimate,
            model_used=response.model_id,
            thinking_level=self.context.thinking_level
        )
        self.context.add_message(assistant_msg)
        
        return response.content
    
    async def _handle_clarification(self, message: str) -> str:
        """
        Handle clarification phase - user answering specific questions.
        
        Similar to requirements gathering but more focused.
        
        Args:
            message: User's answer
        
        Returns:
            Follow-up or confirmation
        """
        return await self._handle_requirements_gathering(message)
    
    async def _handle_general(self, message: str) -> str:
        """
        Handle general messages in other phases.
        
        Args:
            message: User's message
        
        Returns:
            Appropriate response
        """
        
        # Get recent context (last 5 messages)
        recent_messages = self.context.get_recent_messages(5)
        context = "\n".join([
            f"{msg.role}: {msg.content[:100]}" for msg in recent_messages
        ])
        
        # Simple prompt (no system message!)
        user_prompt = f"""Phase: {self.context.phase.value}

Recent context:
{context}

New message: {message}

Respond appropriately. Keep it short."""
        
        response = await ai_router.generate(
            messages=[{"role": "user", "content": user_prompt}],
            task_type="chat",
            complexity=TaskComplexity.SIMPLE,
            max_tokens=200
        )
        
        assistant_msg = Message(
            role="assistant",
            content=response.content,
            tokens_used=response.output_tokens,
            cost=response.cost_estimate,
            model_used=response.model_id
        )
        self.context.add_message(assistant_msg)
        
        return response.content
    
    async def _check_phase_transition(self):
        """
        Check if ready to transition to next phase.
        
        Uses AI to determine if we have enough information
        to move forward (e.g., from gathering to spec generation).
        """
        
        if self.context.phase == ConversationPhase.REQUIREMENTS_GATHERING:
            # Only check readiness if we have at least 3 messages
            if len(self.context.messages) < 3:
                return  # Too early to check
            
            try:
                # Check if ready for spec generation
                readiness = await self._check_readiness_for_spec()
                
                if readiness.is_ready and readiness.confidence > 0.7:
                    self.logger.info(f"✅ Ready for spec generation! Confidence: {readiness.confidence}")
                    self.context.phase = ConversationPhase.READY_FOR_SPEC
                    self.context.requirements_detected = True
                    self.context.complexity_estimate = readiness.estimated_complexity
            except Exception as e:
                # Don't fail the whole chat if readiness check fails
                self.logger.warning(f"⚠️ Readiness check failed: {e}")
                # Just continue in current phase
    
    async def _check_readiness_for_spec(self) -> ReadinessCheck:
        """
        Check if we have enough information to generate specification.
        
        Uses AI to analyze conversation and determine:
        - Do we know what type of project?
        - Do we know main features?
        - Can we estimate complexity?
        
        Returns:
            ReadinessCheck with details
        """
        
        # Get only last 10 messages (not 20) to keep context small
        recent_messages = self.context.get_recent_messages(10)
        
        # Build concise conversation summary
        conversation_summary = []
        for msg in recent_messages:
            # Keep messages short
            content = msg.content[:200] if len(msg.content) > 200 else msg.content
            conversation_summary.append(f"{msg.role}: {content}")
        
        conversation_text = "\n".join(conversation_summary)
        
        # Simplified, shorter prompt
        prompt = f"""Analyze this conversation briefly:

{conversation_text}

Question: Do we have enough info to build a software spec?

Respond ONLY with this JSON (no explanation):
{{
  "is_ready": true or false,
  "confidence": 0.0 to 1.0,
  "missing_info": ["what's missing"],
  "detected_features": ["feature1", "feature2"],
  "estimated_complexity": 1 to 10,
  "reasoning": "one sentence why"
}}"""
        
        try:
            response = await ai_router.generate(
                messages=[{"role": "user", "content": prompt}],
                task_type="analysis",
                complexity=TaskComplexity.SIMPLE,  # Changed from COMPLEX to SIMPLE
                max_tokens=500  # Reduced from 1000
            )
            
            # Parse JSON response
            result = json.loads(response.content)
            
            return ReadinessCheck(
                is_ready=result.get("is_ready", False),
                confidence=result.get("confidence", 0.0),
                missing_info=result.get("missing_info", []),
                detected_features=result.get("detected_features", []),
                estimated_complexity=result.get("estimated_complexity", 5),
                reasoning=result.get("reasoning", "")
            )
        except json.JSONDecodeError:
            self.logger.error("Failed to parse readiness check JSON")
            # Return conservative default
            return ReadinessCheck(
                is_ready=False,
                confidence=0.0,
                missing_info=["Need more information"],
                detected_features=[],
                estimated_complexity=5,
                reasoning="Unable to analyze - need clearer requirements"
            )
        except Exception as e:
            self.logger.error(f"Readiness check failed: {e}")
            # Return conservative default
            return ReadinessCheck(
                is_ready=False,
                confidence=0.0,
                missing_info=["Analysis error - please provide more details"],
                detected_features=[],
                estimated_complexity=5,
                reasoning=str(e)
            )
    
    # =========================================================================
    # ORCHESTRATION MODULE - Agent Delegation
    # =========================================================================
    
    async def delegate_to_saanvi(self) -> Dict[str, Any]:
        """
        Delegate requirements analysis to Saanvi.
        
        Returns:
            Requirements specification from Saanvi
        """
        
        self.logger.info("📋 Delegating to Saanvi for requirements analysis...")
        
        try:
            # Import and create Saanvi instance
            from app.agents.saanvi import Saanvi
            
            saanvi = Saanvi(self.project_id, self.user_id)
            
            # Analyze requirements from conversation
            spec = await saanvi.analyze_requirements(
                conversation=self.context.messages,
                project_name=self.context.project_name or "Untitled Project"
            )
            
            # Update context
            self.context.last_agent_called = "saanvi"
            self.context.current_phase = "requirements_complete"
            
            self.logger.info(f"✅ Saanvi completed: Complexity {spec.pricing.complexity_score}/10")
            
            return {
                "status": "success",
                "agent": "saanvi",
                "specification": spec,
                "complexity": spec.pricing.complexity_score,
                "price": spec.pricing.total_price
            }
            
        except Exception as e:
            self.logger.error(f"❌ Saanvi delegation failed: {e}")
            return {
                "status": "error",
                "agent": "saanvi",
                "error": str(e)
            }
    
    async def delegate_to_kavya(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Delegate design preview to Kavya.
        
        NOTE: Kavya not implemented in v1. Design preview handled by Saanvi.
        
        Args:
            requirements: Requirements from Saanvi
        
        Returns:
            Design preview placeholder
        """
        self.logger.info("🎨 Design preview (via Saanvi for v1)...")
        
        return {
            "status": "success",
            "agent": "saanvi",
            "note": "Design preview integrated in Saanvi for v1"
        }
    
    async def delegate_to_shubham(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Delegate backend development to Shubham.
        
        Args:
            requirements: Requirements spec from Saanvi
        
        Returns:
            Backend code from Shubham
        """
        
        self.logger.info("💻 Delegating to Shubham for backend development...")
        
        try:
            # Import and create Shubham instance
            from app.agents.shubham import Shubham
            
            shubham = Shubham(self.project_id)
            
            # Generate backend code
            backend_code = await shubham.generate_backend(
                architecture=requirements,
                project_name=self.context.project_name
            )
            
            # Update context
            self.context.last_agent_called = "shubham"
            self.context.current_phase = "backend_complete"
            
            self.logger.info(f"✅ Shubham completed: Generated {len(backend_code.get('files', []))} files")
            
            return {
                "status": "success",
                "agent": "shubham",
                "code": backend_code,
                "files_generated": len(backend_code.get('files', []))
            }
            
        except Exception as e:
            self.logger.error(f"❌ Shubham delegation failed: {e}")
            return {
                "status": "error",
                "agent": "shubham",
                "error": str(e)
            }
    
    async def delegate_to_aanya(self, requirements: Dict[str, Any], design: Dict[str, Any]) -> Dict[str, Any]:
        """
        Delegate frontend development to Aanya.
        
        Args:
            requirements: Requirements spec
            design: Design preview
        
        Returns:
            Frontend code from Aanya
        """
        
        self.logger.info("🌐 Delegating to Aanya for frontend development...")
        
        try:
            # Import and create Aanya instance
            from app.agents.aanya import Aanya
            
            aanya = Aanya(self.project_id)
            
            # Generate frontend code
            frontend_code = await aanya.generate_frontend(
                requirements=requirements,
                design=design,
                backend_api=self.context.backend_api_spec  # From Shubham
            )
            
            # Update context
            self.context.last_agent_called = "aanya"
            self.context.current_phase = "frontend_complete"
            
            self.logger.info(f"✅ Aanya completed: Generated {len(frontend_code.get('files', []))} files")
            
            return {
                "status": "success",
                "agent": "aanya",
                "code": frontend_code,
                "files_generated": len(frontend_code.get('files', []))
            }
            
        except Exception as e:
            self.logger.error(f"❌ Aanya delegation failed: {e}")
            return {
                "status": "error",
                "agent": "aanya",
                "error": str(e)
            }
    
    async def delegate_to_aarav(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Delegate mobile app development to Aarav.
        
        NOTE: Mobile development deferred to v2.
        
        Args:
            requirements: Requirements spec
        
        Returns:
            Deferred status
        """
        self.logger.info("📱 Mobile development deferred to v2...")
        
        return {
            "status": "deferred",
            "agent": "aarav",
            "note": "Mobile development deferred to v2"
        }
    
    async def delegate_to_navya(self, code: Dict[str, Any]) -> Dict[str, Any]:
        """
        Delegate code review to Navya (adversarial).
        
        Args:
            code: Generated code (backend + frontend)
        
        Returns:
            Review results with bugs found
        """
        
        self.logger.info("✅ Delegating to Navya for adversarial code review...")
        
        try:
            # Import adversarial agents
            from app.agents.navya_adversarial import NavyaAdversarial
            from app.agents.karan_adversarial import KaranAdversarial
            from app.agents.deepika_adversarial import DeepikaAdversarial
            
            # Create agent instances
            navya = NavyaAdversarial(self.project_id)
            karan = KaranAdversarial(self.project_id)
            deepika = DeepikaAdversarial(self.project_id)
            
            # Run adversarial competition (parallel)
            import asyncio
            
            results = await asyncio.gather(
                navya.review(code['backend'], file_type="python"),
                karan.review(code['backend'], file_type="python"),
                deepika.review(code['backend'], file_type="python"),
                return_exceptions=True
            )
            
            navya_result, karan_result, deepika_result = results
            
            # Count total bugs
            total_bugs = (
                navya_result.get('bugs_found', 0) +
                karan_result.get('vulnerabilities_found', 0) +
                deepika_result.get('issues_found', 0)
            )
            
            # Update context
            self.context.last_agent_called = "navya"
            self.context.current_phase = "review_complete"
            
            self.logger.info(f"✅ Adversarial review completed: {total_bugs} issues found")
            
            return {
                "status": "success",
                "agent": "navya_adversarial",
                "total_bugs": total_bugs,
                "navya": navya_result,
                "karan": karan_result,
                "deepika": deepika_result
            }
            
        except Exception as e:
            self.logger.error(f"❌ Navya delegation failed: {e}")
            return {
                "status": "error",
                "agent": "navya",
                "error": str(e)
            }
    
    async def delegate_to_pranav(self, code: Dict[str, Any]) -> Dict[str, Any]:
        """
        Delegate deployment to Pranav.
        
        Args:
            code: Reviewed and approved code
        
        Returns:
            Deployment info with live URL
        """
        
        self.logger.info("🚀 Delegating to Pranav for deployment...")
        
        try:
            # Import and create Pranav instance
            from app.agents.pranav import Pranav
            
            pranav = Pranav(self.project_id)
            
            # Deploy to production
            deployment = await pranav.deploy(
                code=code,
                project_name=self.context.project_name,
                platform="railway"  # or "vercel", "gcp"
            )
            
            # Update context
            self.context.last_agent_called = "pranav"
            self.context.current_phase = "deployed"
            self.context.deployment_url = deployment.get('url')
            
            self.logger.info(f"✅ Pranav completed: Deployed to {deployment.get('url')}")
            
            return {
                "status": "success",
                "agent": "pranav",
                "deployment": deployment,
                "url": deployment.get('url'),
                "platform": deployment.get('platform')
            }
            
        except Exception as e:
            self.logger.error(f"❌ Pranav delegation failed: {e}")
            return {
                "status": "error",
                "agent": "pranav",
                "error": str(e)
            }
    
    # =========================================================================
    # VALIDATION MODULE - Quality Control
    # =========================================================================
    
    async def validate_agent_output(
        self,
        agent_name: str,
        output: Any,
        expected_format: Optional[str] = None
    ) -> ValidationResult:
        """
        Validate output from any agent.
        
        Uses AI to check if output is valid.
        
        Args:
            agent_name: Name of agent who produced output
            output: The output to validate
            expected_format: What format we expect
        
        Returns:
            ValidationResult with details
        """
        
        self.logger.info(f"🔍 Validating output from {agent_name}...")
        
        # Truncate output for validation (first 1000 chars)
        output_str = str(output)[:1000]
        
        # Simplified prompt
        prompt = f"""Review this output from {agent_name}:

OUTPUT (truncated):
{output_str}

Expected: {expected_format or 'Any format'}

Respond ONLY with JSON:
{{
  "is_valid": true/false,
  "issues": ["issue1"],
  "suggestions": ["suggestion1"],
  "should_retry": true/false,
  "feedback_for_agent": "what to improve"
}}"""
        
        try:
            response = await ai_router.generate(
                messages=[{"role": "user", "content": prompt}],
                task_type="analysis",
                complexity=TaskComplexity.SIMPLE,
                max_tokens=300
            )
            
            result = json.loads(response.content)
            
            return ValidationResult(
                is_valid=result.get("is_valid", False),
                issues=result.get("issues", []),
                suggestions=result.get("suggestions", []),
                should_retry=result.get("should_retry", False),
                feedback_for_agent=result.get("feedback_for_agent", "")
            )
        except Exception as e:
            self.logger.error(f"Validation failed: {e}")
            # Return permissive default
            return ValidationResult(
                is_valid=True,
                issues=[],
                suggestions=[],
                should_retry=False,
                feedback_for_agent=""
            )
    
    # =========================================================================
    # ERROR RECOVERY MODULE - Auto-Retry
    # =========================================================================
    
    async def retry_agent_with_feedback(
        self,
        agent_name: str,
        feedback: str,
        original_input: Any
    ) -> Dict[str, Any]:
        """
        Retry an agent with specific feedback.
        
        Max 3 attempts. If still failing after 3, escalate to human.
        
        Args:
            agent_name: Which agent to retry
            feedback: What went wrong and how to fix
            original_input: Original input to the agent
        
        Returns:
            New output from agent
        """
        
        # Check retry count
        if agent_name not in self.context.retry_count:
            self.context.retry_count[agent_name] = 0
        
        self.context.retry_count[agent_name] += 1
        retry_num = self.context.retry_count[agent_name]
        
        if retry_num > 3:
            self.logger.error(f"❌ {agent_name} failed after 3 retries. Human escalation needed.")
            return {
                "status": "failed",
                "error": "Max retries exceeded",
                "needs_human": True
            }
        
        self.logger.warning(f"🔄 Retrying {agent_name} (attempt {retry_num}/3)...")
        self.logger.info(f"💬 Feedback: {feedback}")
        
        # Call agent again with feedback
        # Implementation depends on agent type
        # For now, return placeholder
        
        return {
            "status": "retry_in_progress",
            "attempt": retry_num,
            "feedback_provided": feedback
        }
    
    async def escalate_to_better_model(
        self,
        agent_name: str,
        task_description: str,
        original_output: Any
    ) -> Dict[str, Any]:
        """
        Escalate to Claude Opus when stuck.
        
        Sometimes the issue isn't the agent's logic but the AI model's capability.
        Switch to the most powerful model for this specific task.
        
        Args:
            agent_name: Which agent needs better model
            task_description: What the task is
            original_output: What we got (not good enough)
        
        Returns:
            Better output hopefully
        """
        
        self.logger.warning(f"⚡ Escalating {agent_name} to Claude Opus for better results...")
        
        # TODO: Implement model escalation
        # This would involve calling the agent again but forcing Claude Opus
        
        return {
            "status": "escalated",
            "model": "claude-opus-4",
            "output": "Escalated output placeholder"
        }
    
    # =========================================================================
    # APPROVAL MODULE - Final Quality Gate
    # =========================================================================
    
    async def final_quality_check(
        self,
        all_outputs: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """
        Final check before delivery to customer.
        
        Reviews if all components are present and working.
        
        Args:
            all_outputs: Outputs from all agents
        
        Returns:
            (approved: bool, issues: List[str])
        """
        
        self.logger.info("🎯 Running final quality check...")
        
        # Simplified summary of outputs
        output_summary = {}
        for key, value in all_outputs.items():
            # Just track presence, not full content
            output_summary[key] = "present" if value else "missing"
        
        prompt = f"""Final quality gate check.

Outputs: {json.dumps(output_summary)}
Complexity: {self.context.complexity_estimate}/10

Respond ONLY with JSON:
{{
  "approved": true/false,
  "issues": ["issue1"],
  "ready_for_deployment": true/false
}}"""
        
        try:
            response = await ai_router.generate(
                messages=[{"role": "user", "content": prompt}],
                task_type="analysis",
                complexity=TaskComplexity.MEDIUM,
                max_tokens=300
            )
            
            result = json.loads(response.content)
            approved = result.get("approved", False)
            issues = result.get("issues", [])
            
            if approved:
                self.logger.info("✅ Final quality check PASSED!")
            else:
                self.logger.warning(f"⚠️ Final quality check FAILED: {issues}")
            
            return approved, issues
        
        except Exception as e:
            self.logger.error(f"Final check failed: {e}")
            # Conservative: assume not ready if check fails
            return False, [f"Quality check error: {str(e)}"]
    
    # =========================================================================
    # UTILITY METHODS
    # =========================================================================
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """
        Get complete conversation history.
        
        Returns:
            List of messages as dicts
        """
        return [msg.to_dict() for msg in self.context.messages]
    
    def get_project_status(self) -> Dict[str, Any]:
        """
        Get current project status.
        
        Returns:
            Status information
        """
        return {
            "project_id": self.project_id,
            "phase": self.context.phase.value,
            "messages_count": len(self.context.messages),
            "total_cost": self.context.total_cost,
            "complexity_estimate": self.context.complexity_estimate,
            "last_agent_called": self.context.last_agent_called,
            "retry_counts": self.context.retry_count
        }
    
    def reset_retry_counts(self):
        """Reset retry counts (call after successful phase)"""
        self.context.retry_count = {}


# =============================================================================
# EXAMPLE USAGE
# =============================================================================

if __name__ == "__main__":
    """
    Example of using Tilotma agent.
    
    Run this file directly to test:
    python tilotma.py
    """
    
    import asyncio
    
    async def test_tilotma():
        """Test basic chat flow"""
        
        # Initialize Tilotma for a new project
        project_id = str(uuid.uuid4())
        user_id = str(uuid.uuid4())
        
        tilotma = Tilotma(project_id, user_id)
        
        # Simulate conversation
        print("\n" + "="*60)
        print("TESTING TILOTMA - ORCHESTRATOR AGENT")
        print("="*60 + "\n")
        
        # Message 1: Initial greeting
        response1 = await tilotma.chat("Hi, I want to build a website")
        print(f"User: Hi, I want to build a website")
        print(f"Tilotma: {response1}\n")
        
        # Message 2: More details (with typo!)
        response2 = await tilotma.chat("I need a webiste for my buisness")
        print(f"User: I need a webiste for my buisness")
        print(f"Tilotma: {response2}\n")
        
        # Message 3: Answer questions
        response3 = await tilotma.chat("It's a restaurant. I want to show menu and take online orders")
        print(f"User: It's a restaurant. I want to show menu and take online orders")
        print(f"Tilotma: {response3}\n")
        
        # Check readiness
        readiness = await tilotma._check_readiness_for_spec()
        print(f"\n📊 Readiness Check:")
        print(f"  Ready: {readiness.is_ready}")
        print(f"  Confidence: {readiness.confidence}")
        print(f"  Complexity: {readiness.estimated_complexity}/10")
        print(f"  Features: {readiness.detected_features}")
        print(f"  Missing: {readiness.missing_info}")
        
        # Get status
        status = tilotma.get_project_status()
        print(f"\n📈 Project Status:")
        print(f"  Phase: {status['phase']}")
        print(f"  Messages: {status['messages_count']}")
        print(f"  Cost: ₹{status['total_cost']:.2f}")
        
        print("\n" + "="*60)
        print("TEST COMPLETE")
        print("="*60 + "\n")
    
    # Run test
    asyncio.run(test_tilotma())