# =============================================================================
# FILE: backend/services/ai_router.py
# PURPOSE: Unified interface for AI model interactions (Claude & Gemini)
# UPDATED: Vertex AI fallback when AI Studio quota exhausted
# =============================================================================

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import logging
import time
import httpx
import os
import asyncio

logger = logging.getLogger(__name__)


# =============================================================================
# ENUMS AND DATA CLASSES
# =============================================================================

class TaskType(Enum):
    """Types of tasks for model selection."""
    GENERAL = "general"
    CHAT = "chat"
    CODE_GENERATION = "code_generation"
    CODE_REVIEW = "code_review"
    ARCHITECTURE = "architecture"
    ANALYSIS = "analysis"
    CREATIVE = "creative"
    REASONING = "reasoning"
    COMPLEX_REASONING = "complex_reasoning"


class Complexity(Enum):
    """Task complexity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ModelProvider(Enum):
    """AI model providers."""
    CLAUDE = "claude"
    GEMINI_AI_STUDIO = "gemini_ai_studio"
    GEMINI_VERTEX = "gemini_vertex"


@dataclass
class AIResponse:
    """Standardized response from any AI model."""
    content: str
    model_id: str
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    latency_ms: float = 0.0
    finish_reason: str = "stop"
    cost: float = 0.0
    raw_response: Any = None


# =============================================================================
# MODEL CONFIGURATIONS
# =============================================================================

CLAUDE_MODELS = {
    "claude-opus-4.5": "claude-opus-4-5-20251101",
    "claude-sonnet-4.5": "claude-sonnet-4-5-20250929",
    "claude-haiku-4.5": "claude-haiku-4-5-20251001",
    "claude-opus-4.1": "claude-opus-4-1-20250514",
}

GEMINI_MODELS_AI_STUDIO = {
    "gemini-3-pro-preview": "gemini-3-pro-preview",
}

GEMINI_MODELS_VERTEX = {
    "gemini-3-pro-preview": "gemini-3-pro-preview",
    "gemini-2.5-pro": "gemini-2.5-pro",
    "gemini-2.5-flash": "gemini-2.5-flash",
    "gemini-2.5-flash-lite": "gemini-2.5-flash-lite",
}

class ModelTier:
    """Model tiers for different use cases."""
    CLAUDE_BEST = "claude-opus-4-5-20251101"
    CLAUDE_BALANCED = "claude-sonnet-4-5-20250929"
    CLAUDE_FAST = "claude-haiku-4-5-20251001"
    
    GEMINI_AI_STUDIO_BEST = "gemini-3-pro-preview"
    GEMINI_AI_STUDIO_BALANCED = "gemini-2.5-pro"
    GEMINI_AI_STUDIO_FAST = "gemini-2.5-flash"
    
    GEMINI_VERTEX_BEST = "gemini-1.5-pro"
    GEMINI_VERTEX_FAST = "gemini-1.5-flash"


# =============================================================================
# TASK-TO-MODEL MAPPING
# =============================================================================

def get_best_model_for_task(
    task_type: TaskType, 
    complexity: Complexity,
    has_anthropic: bool,
    has_gemini_ai_studio: bool,
    has_vertex_ai: bool
) -> tuple[ModelProvider, str]:
    """Select the best model based on task type, complexity, and availability."""
    
    # HIGH complexity
    if complexity == Complexity.HIGH:
        if task_type in [TaskType.CODE_REVIEW, TaskType.ARCHITECTURE, 
                         TaskType.REASONING, TaskType.COMPLEX_REASONING]:
            if has_anthropic:
                return ModelProvider.CLAUDE, ModelTier.CLAUDE_BEST
            elif has_vertex_ai:
                return ModelProvider.GEMINI_VERTEX, ModelTier.GEMINI_VERTEX_BEST
            elif has_gemini_ai_studio:
                return ModelProvider.GEMINI_AI_STUDIO, ModelTier.GEMINI_AI_STUDIO_BEST
        elif task_type == TaskType.CODE_GENERATION:
            if has_vertex_ai:
                return ModelProvider.GEMINI_VERTEX, ModelTier.GEMINI_VERTEX_BEST
            elif has_gemini_ai_studio:
                return ModelProvider.GEMINI_AI_STUDIO, ModelTier.GEMINI_AI_STUDIO_BALANCED
            elif has_anthropic:
                return ModelProvider.CLAUDE, ModelTier.CLAUDE_BEST
    
    # MEDIUM complexity
    if complexity == Complexity.MEDIUM:
        if task_type in [TaskType.CODE_GENERATION, TaskType.ANALYSIS]:
            if has_gemini_ai_studio:
                return ModelProvider.GEMINI_AI_STUDIO, ModelTier.GEMINI_AI_STUDIO_BALANCED
            elif has_vertex_ai:
                return ModelProvider.GEMINI_VERTEX, ModelTier.GEMINI_VERTEX_BEST
            elif has_anthropic:
                return ModelProvider.CLAUDE, ModelTier.CLAUDE_BALANCED
        elif task_type in [TaskType.CODE_REVIEW, TaskType.REASONING]:
            if has_anthropic:
                return ModelProvider.CLAUDE, ModelTier.CLAUDE_BALANCED
            elif has_vertex_ai:
                return ModelProvider.GEMINI_VERTEX, ModelTier.GEMINI_VERTEX_BEST
    
    # LOW complexity (prefer free/fast options)
    if has_gemini_ai_studio:
        return ModelProvider.GEMINI_AI_STUDIO, ModelTier.GEMINI_AI_STUDIO_FAST
    elif has_vertex_ai:
        return ModelProvider.GEMINI_VERTEX, ModelTier.GEMINI_VERTEX_FAST
    elif has_anthropic:
        return ModelProvider.CLAUDE, ModelTier.CLAUDE_FAST
    
    # Fallback
    if has_anthropic:
        return ModelProvider.CLAUDE, ModelTier.CLAUDE_BALANCED
    elif has_gemini_ai_studio:
        return ModelProvider.GEMINI_AI_STUDIO, ModelTier.GEMINI_AI_STUDIO_BALANCED
    elif has_vertex_ai:
        return ModelProvider.GEMINI_VERTEX, ModelTier.GEMINI_VERTEX_BEST
    
    raise ValueError("No AI providers available!")


# =============================================================================
# AI ROUTER CLASS
# =============================================================================

class AIRouter:
    """Routes AI requests to the best model with automatic fallback."""
    
    def __init__(self):
        self.logger = logging.getLogger("ai.router")
        self._http_client: Optional[httpx.AsyncClient] = None
        
        # Load API keys from environment
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.google_ai_studio_key = os.getenv("GOOGLE_API_KEY")
        self.google_cloud_project = os.getenv("GOOGLE_CLOUD_PROJECT")
        self.google_cloud_location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
        self.google_application_credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        
        # Check availability
        self.has_anthropic = bool(self.anthropic_api_key)
        self.has_gemini_ai_studio = bool(self.google_ai_studio_key)
        self.has_vertex_ai = False
        
        # Initialize Vertex AI if configured
        if self.google_cloud_project:
            try:
                import vertexai
                from google.oauth2 import service_account
                from vertexai.generative_models import GenerativeModel
                
                if self.google_application_credentials and os.path.exists(self.google_application_credentials):
                    credentials = service_account.Credentials.from_service_account_file(
                        self.google_application_credentials
                    )
                    vertexai.init(
                        project=self.google_cloud_project,
                        location=self.google_cloud_location,
                        credentials=credentials
                    )
                else:
                    vertexai.init(
                        project=self.google_cloud_project,
                        location=self.google_cloud_location
                    )
                
                self.has_vertex_ai = True
                self.logger.info(f"✅ Vertex AI initialized (project: {self.google_cloud_project})")
            except Exception as e:
                self.logger.warning(f"⚠️ Vertex AI initialization failed: {e}")
        
        # Log available providers
        providers = []
        if self.has_anthropic:
            providers.append("Claude")
        if self.has_gemini_ai_studio:
            providers.append("Gemini AI Studio")
        if self.has_vertex_ai:
            providers.append("Vertex AI")
        
        self.logger.info(f"AI Router initialized: {', '.join(providers) or 'NO PROVIDERS!'}")
        
        if not providers:
            self.logger.warning("⚠️ No AI providers configured! Add API keys to .env")
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client with retry logic."""
        if self._http_client is None or self._http_client.is_closed:
            # Create transport with retry logic
            transport = httpx.AsyncHTTPTransport(retries=3)
            self._http_client = httpx.AsyncClient(
                timeout=120.0,
                transport=transport,
                limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
            )
        return self._http_client
    
    async def close(self):
        """Close HTTP client."""
        if self._http_client:
            await self._http_client.aclose()
    
    def get_available_models(self) -> Dict[str, List[str]]:
        """Return list of available models."""
        models = {"claude": [], "gemini_ai_studio": [], "gemini_vertex": []}
        
        if self.has_anthropic:
            models["claude"] = list(CLAUDE_MODELS.values())
        
        if self.has_gemini_ai_studio:
            models["gemini_ai_studio"] = list(GEMINI_MODELS_AI_STUDIO.values())
        
        if self.has_vertex_ai:
            models["gemini_vertex"] = list(GEMINI_MODELS_VERTEX.values())
        
        return models
    
    async def complete(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        task_type: TaskType = TaskType.GENERAL,
        complexity: Complexity = Complexity.MEDIUM,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        provider: Optional[ModelProvider] = None,
        model: Optional[str] = None,
        **kwargs
    ) -> AIResponse:
        """Generate completion with automatic fallback on quota errors."""
        
        start_time = time.time()
        
        # Select model
        if provider and model:
            selected_provider = provider
            selected_model = model
        else:
            selected_provider, selected_model = get_best_model_for_task(
                task_type, 
                complexity,
                self.has_anthropic,
                self.has_gemini_ai_studio,
                self.has_vertex_ai
            )
        
        self.logger.info(f"🤖 Task: {task_type.value}/{complexity.value} → {selected_provider.value}:{selected_model}")
        
        # Try primary model
        try:
            response = await self._call_provider(
                selected_provider,
                selected_model,
                messages,
                system_prompt,
                max_tokens,
                temperature,
                **kwargs
            )
            response.latency_ms = (time.time() - start_time) * 1000
            self.logger.info(f"✅ Success: {response.total_tokens} tokens, {response.latency_ms:.0f}ms")
            return response
            
        except Exception as e:
            error_msg = str(e).lower()
            
            # Check if quota/rate limit error
            is_quota_error = any(keyword in error_msg for keyword in [
                'quota', 'rate limit', '429', 'resourceexhausted', 'exceeded'
            ])
            
            if not is_quota_error:
                self.logger.error(f"❌ Non-quota error: {e}")
                raise
            
            self.logger.warning(f"⚠️ Quota exhausted on {selected_provider.value}: {e}")
            
            # Try fallbacks
            fallback_chain = self._get_fallback_chain(selected_provider)
            
            for fallback_provider, fallback_model in fallback_chain:
                try:
                    self.logger.info(f"🔄 Trying fallback: {fallback_provider.value}")
                    response = await self._call_provider(
                        fallback_provider,
                        fallback_model,
                        messages,
                        system_prompt,
                        max_tokens,
                        temperature,
                        **kwargs
                    )
                    response.latency_ms = (time.time() - start_time) * 1000
                    self.logger.info(f"✅ Fallback success: {fallback_provider.value}")
                    return response
                    
                except Exception as fallback_error:
                    self.logger.warning(f"❌ Fallback {fallback_provider.value} failed: {fallback_error}")
                    continue
            
            # All failed
            raise Exception(f"All AI providers failed. Original error: {e}")
    
    def _get_fallback_chain(self, primary: ModelProvider) -> List[tuple[ModelProvider, str]]:
        """Determine fallback order."""
        fallbacks = []
        
        if primary == ModelProvider.GEMINI_AI_STUDIO:
            # AI Studio failed → try Vertex AI, then Claude
            if self.has_vertex_ai:
                fallbacks.append((ModelProvider.GEMINI_VERTEX, ModelTier.GEMINI_VERTEX_BEST))
            if self.has_anthropic:
                fallbacks.append((ModelProvider.CLAUDE, ModelTier.CLAUDE_BALANCED))
        
        elif primary == ModelProvider.GEMINI_VERTEX:
            # Vertex AI failed → try AI Studio, then Claude
            if self.has_gemini_ai_studio:
                fallbacks.append((ModelProvider.GEMINI_AI_STUDIO, ModelTier.GEMINI_AI_STUDIO_BALANCED))
            if self.has_anthropic:
                fallbacks.append((ModelProvider.CLAUDE, ModelTier.CLAUDE_BALANCED))
        
        elif primary == ModelProvider.CLAUDE:
            # Claude failed → try Vertex AI, then AI Studio
            if self.has_vertex_ai:
                fallbacks.append((ModelProvider.GEMINI_VERTEX, ModelTier.GEMINI_VERTEX_BEST))
            if self.has_gemini_ai_studio:
                fallbacks.append((ModelProvider.GEMINI_AI_STUDIO, ModelTier.GEMINI_AI_STUDIO_BALANCED))
        
        return fallbacks
    
    async def _call_provider(
        self,
        provider: ModelProvider,
        model: str,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str],
        max_tokens: int,
        temperature: float,
        **kwargs
    ) -> AIResponse:
        """Route to appropriate provider implementation."""
        
        if provider == ModelProvider.CLAUDE:
            return await self._call_anthropic(messages, system_prompt, model, max_tokens, temperature, **kwargs)
        elif provider == ModelProvider.GEMINI_AI_STUDIO:
            return await self._call_gemini_ai_studio(messages, system_prompt, model, max_tokens, temperature, **kwargs)
        elif provider == ModelProvider.GEMINI_VERTEX:
            return await self._call_gemini_vertex(messages, system_prompt, model, max_tokens, temperature, **kwargs)
        else:
            raise ValueError(f"Unknown provider: {provider}")
    
    # =========================================================================
    # ANTHROPIC (CLAUDE) IMPLEMENTATION
    # =========================================================================
    
    async def _call_anthropic(
        self, 
        messages: List[Dict[str, str]], 
        system_prompt: Optional[str],
        model: str,
        max_tokens: int,
        temperature: float,
        **kwargs
    ) -> AIResponse:
        """Call Anthropic Claude API."""
        
        if not self.has_anthropic:
            raise ValueError("Anthropic API key not configured")
        
        client = await self._get_client()
        
        request_body = {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": messages,
        }
        
        if system_prompt:
            request_body["system"] = system_prompt
        
        response = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": self.anthropic_api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json=request_body,
        )
        
        if response.status_code != 200:
            raise Exception(f"Anthropic API error: {response.status_code} - {response.text}")
        
        data = response.json()
        
        content = ""
        if data.get("content"):
            for block in data["content"]:
                if block.get("type") == "text":
                    content += block.get("text", "")
        
        input_tokens = data.get("usage", {}).get("input_tokens", 0)
        output_tokens = data.get("usage", {}).get("output_tokens", 0)
        
        return AIResponse(
            content=content,
            model_id=data.get("model", model),
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens,
            finish_reason=data.get("stop_reason", "stop"),
            raw_response=data,
        )

    # =========================================================================
    # GOOGLE GEMINI AI STUDIO IMPLEMENTATION
    # =========================================================================
    
    async def _call_gemini_ai_studio(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str],
        model: str,
        max_tokens: int,
        temperature: float,
        **kwargs
    ) -> AIResponse:
        """Call Gemini via AI Studio API."""
        
        if not self.has_gemini_ai_studio:
            raise ValueError("Google AI Studio API key not configured")
        
        client = await self._get_client()
        
        contents = []
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            contents.append({
                "role": role,
                "parts": [{"text": msg["content"]}]
            })
        
        request_body = {
            "contents": contents,
            "generationConfig": {
                "maxOutputTokens": max_tokens,
                "temperature": temperature,
            }
        }
        
        if system_prompt:
            request_body["systemInstruction"] = {
                "parts": [{"text": system_prompt}]
            }
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.google_ai_studio_key}"
        
        # Retry logic for network failures
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = await client.post(url, json=request_body)
                
                if response.status_code != 200:
                    raise Exception(f"Gemini AI Studio error: {response.status_code} - {response.text}")
                
                break  # Success, exit retry loop
                
            except (httpx.ConnectError, httpx.TimeoutException, OSError) as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                    self.logger.warning(f"Network error (attempt {attempt + 1}/{max_retries}): {e}. Retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                else:
                    # All retries failed
                    raise Exception(
                        f"Network connection failed after {max_retries} attempts. "
                        f"Please check your internet connection and firewall settings. "
                        f"Original error: {e}"
                    )
        
        data = response.json()
        
        content = ""
        if data.get("candidates"):
            candidate = data["candidates"][0]
            if candidate.get("content", {}).get("parts"):
                for part in candidate["content"]["parts"]:
                    content += part.get("text", "")
        
        usage = data.get("usageMetadata", {})
        
        return AIResponse(
            content=content,
            model_id=model,
            input_tokens=usage.get("promptTokenCount", 0),
            output_tokens=usage.get("candidatesTokenCount", 0),
            total_tokens=usage.get("totalTokenCount", 0),
            finish_reason=data.get("candidates", [{}])[0].get("finishReason", "STOP"),
            raw_response=data,
        )
    
    # =========================================================================
    # GOOGLE VERTEX AI IMPLEMENTATION
    # =========================================================================
    
    async def _call_gemini_vertex(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str],
        model: str,
        max_tokens: int,
        temperature: float,
        **kwargs
    ) -> AIResponse:
        """Call Gemini via Vertex AI."""
        
        if not self.has_vertex_ai:
            raise ValueError("Vertex AI not configured")
        
        from vertexai.generative_models import GenerativeModel, Content, Part
        
        # Convert messages to Vertex AI format
        contents = []
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            contents.append(Content(
                role=role,
                parts=[Part.from_text(msg["content"])]
            ))
        
        # Initialize model
        vertex_model = GenerativeModel(model)
        
        # Set system instruction if provided
        if system_prompt:
            vertex_model = GenerativeModel(
                model,
                system_instruction=[system_prompt]
            )
        
        # Generate content
        response = vertex_model.generate_content(
            contents,
            generation_config={
                "max_output_tokens": max_tokens,
                "temperature": temperature,
            }
        )
        
        content = response.text
        
        # Approximate token count (Vertex AI doesn't always provide exact counts)
        total_input = sum(len(msg["content"].split()) for msg in messages)
        total_output = len(content.split())
        
        return AIResponse(
            content=content,
            model_id=model,
            input_tokens=total_input,
            output_tokens=total_output,
            total_tokens=total_input + total_output,
            finish_reason="STOP",
            raw_response=response,
        )


# =============================================================================
# GLOBAL INSTANCE
# =============================================================================

ai_router = AIRouter()


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

async def quick_complete(
    prompt: str,
    system_prompt: Optional[str] = None,
    task_type: TaskType = TaskType.CHAT,
    complexity: Complexity = Complexity.LOW,
) -> str:
    """Quick helper for simple completions."""
    response = await ai_router.complete(
        messages=[{"role": "user", "content": prompt}],
        system_prompt=system_prompt,
        task_type=task_type,
        complexity=complexity,
    )
    return response.content


def list_models() -> Dict[str, Dict[str, str]]:
    """Return all available model configurations."""
    return {
        "claude": CLAUDE_MODELS,
        "gemini_ai_studio": GEMINI_MODELS_AI_STUDIO,
        "gemini_vertex": GEMINI_MODELS_VERTEX,
    }
