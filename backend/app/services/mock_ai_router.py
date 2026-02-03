# =============================================================================
# MOCK AI ROUTER - FOR TESTING WITHOUT API KEYS
# Use this for local testing when you don't have API keys configured
# =============================================================================

from enum import Enum
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


class TaskComplexity(Enum):
    """Task complexity levels"""
    SIMPLE = "simple"
    MEDIUM = "medium"
    COMPLEX = "complex"


class ThinkingLevel(Enum):
    """Thinking depth levels"""
    STANDARD = 0
    NORMAL = 1
    EXTENDED = 2
    DEEP = 3


@dataclass
class AIResponse:
    """Response from AI model"""
    content: str
    output_tokens: int
    cost_estimate: float
    model_id: str
    finish_reason: str = "stop"
    was_escalated: bool = False


class MockAIRouter:
    """
    Mock AI Router for testing.
    
    Returns predefined responses without calling actual AI APIs.
    Perfect for testing Tilotma logic without API keys.
    """
    
    def __init__(self):
        self.call_count = 0
        
    async def generate(
        self,
        messages: List[Dict[str, str]],
        task_type: str = "chat",
        complexity: TaskComplexity = TaskComplexity.MEDIUM,
        max_tokens: int = 1000,
        thinking_level: Any = None,
        auto_escalate: bool = False
    ) -> AIResponse:
        """
        Generate mock AI response.
        
        Returns realistic responses based on the last user message.
        """
        
        self.call_count += 1
        
        # Get last user message
        user_message = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_message = msg.get("content", "").lower()
                break
        
        # Generate appropriate mock response
        response = self._generate_mock_response(user_message, task_type)
        
        return AIResponse(
            content=response,
            output_tokens=len(response.split()),
            cost_estimate=0.05,  # Mock cost
            model_id="mock-model-v1",
            finish_reason="stop",
            was_escalated=False
        )
    
    def _generate_mock_response(self, user_message: str, task_type: str) -> str:
        """Generate contextual mock response"""
        
        # Greeting
        if any(word in user_message for word in ["hi", "hello", "hey"]):
            return "Hello! I'm Tilotma, your AI project manager. What would you like to build today?"
        
        # Website request
        if "website" in user_message or "site" in user_message:
            if "restaurant" in user_message or "business" in user_message:
                return "Great! A website for your restaurant. To help you best, I'd like to know: What features are most important to you? For example, online menu display, table reservations, online ordering, or something else?"
            else:
                return "I'd be happy to help you build a website! To give you an accurate quote and timeline, could you tell me more about what kind of website you need? For example, is it for business, e-commerce, blog, or portfolio?"
        
        # E-commerce
        if "e-commerce" in user_message or "shop" in user_message or "store" in user_message:
            return "Perfect! An e-commerce platform. Let me understand your requirements: What products will you sell? Do you need payment integration (like Razorpay)? Do you need user accounts and order tracking?"
        
        # Mobile app
        if "app" in user_message or "mobile" in user_message:
            return "Excellent! A mobile app. Would you like this for iOS, Android, or both? Also, what will the app do - is it connected to a backend system, or is it standalone?"
        
        # Payment/features questions
        if "payment" in user_message:
            return "Yes, we can integrate payment systems like Razorpay, Stripe, or PayPal. This will add payment processing, order confirmation, and transaction history to your project."
        
        # Readiness check (JSON response)
        if task_type == "analysis" and "respond in json" in user_message:
            if "readiness" in user_message or "enough information" in user_message:
                return """{
  "is_ready": true,
  "confidence": 0.85,
  "missing_info": [],
  "detected_features": ["website", "restaurant", "menu display", "online ordering"],
  "estimated_complexity": 6,
  "reasoning": "User has provided clear information about wanting a restaurant website with menu and ordering features. Sufficient for specification."
}"""
            
            if "validate" in user_message or "check" in user_message:
                return """{
  "is_valid": true,
  "issues": [],
  "suggestions": ["Consider adding responsive design for mobile users"],
  "should_retry": false,
  "feedback_for_agent": "Output looks good, all requirements met"
}"""
        
        # Default response
        return "I understand. Could you provide more details so I can help you better?"


# Create singleton instance
ai_router = MockAIRouter()


# Export for compatibility
__all__ = ['ai_router', 'TaskComplexity', 'ThinkingLevel', 'AIResponse']
