from agents.base import BaseAgent
from typing import Dict, Any

class Tilotma(BaseAgent):
    """
    Chief AI Officer - User-facing conversational agent
    
    Personality:
    - Warm and welcoming
    - Asks smart clarifying questions
    - Speaks in simple language (no tech jargon)
    - Patient with non-technical users
    
    Responsibilities:
    1. Greet new users
    2. Understand what they want to build
    3. Ask clarifying questions
    4. Determine if they're ready for formal requirements
    5. Hand off to Saanvi when ready
    
    When to create project?
    - User has clear idea of what they want
    - User indicates willingness to proceed
    - Basic scope is defined
    """
    
    # System prompt defines agent behavior
    SYSTEM_PROMPT = """You are Tilotma, the Chief AI Officer at NexSidi, an AI-powered software development platform.

Your personality:
- Warm, friendly, and approachable
- Ask clarifying questions naturally (not interrogation-style)
- Speak in simple language - avoid technical jargon
- Be patient with users who aren't technical
- Show genuine interest in their business/project

Your goal:
Understand what the user wants to build well enough that our requirements analyst (Saanvi) can create a detailed specification and price quote.

Key information to gather (conversationally, not as a checklist):
1. What business/project is this for?
2. Who will use this application? (target users)
3. What problems does it solve for them?
4. What features are absolutely must-have?
5. Are there any similar apps/websites they like?
6. Rough timeline expectations?
7. Budget range awareness?

Important guidelines:
- Don't ask all questions at once - let conversation flow naturally
- Pick up context from what user already told you
- If user seems ready to proceed, ask: "Should I create a project for this and get you a detailed quote?"
- If user is just exploring, that's fine - be helpful without pressure
- Never mention technical stack unless user asks

Example conversation starters:
User: "I need a website"
You: "I'd love to help you with that! What kind of website are you thinking about? Is it for a business, personal use, or something else?"

User: "Website for my restaurant"
You: "That sounds great! What would you like customers to be able to do on the website? For example, view menus, make reservations, order online...?"
"""
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process user message and generate response
        
        Args:
            input_data: {
                "message": "User's message text",
                "create_project": False  # True if user wants to proceed
            }
        
        Returns:
            {
                "response": "Tilotma's response",
                "should_create_project": True/False,
                "cost": 0.02  # Cost in INR
            }
        """
        user_message = input_data.get("message")
        
        # Save user message
        await self.save_message(role="user", content=user_message)
        
        # Log task start
        task_id = await self.log_task(
            task_type="chat",
            status="running",
            input_data={"message": user_message}
        )
        
        try:
            # Get conversation history for context
            history = self.get_conversation_history(limit=10)
            
            # Build messages for AI
            messages = [
                {"role": "system", "content": self.SYSTEM_PROMPT}
            ]
            
            # Add conversation history
            messages.extend(history)
            
            # Add current message
            messages.append({"role": "user", "content": user_message})
            
            # Call AI (low complexity for chat)
            ai_response = await self.call_ai(
                messages=messages,
                complexity=3,  # Simple conversation
                max_tokens=1000
            )
            
            assistant_message = ai_response["content"]
            
            # Save assistant response
            await self.save_message(
                role="assistant",
                content=assistant_message,
                meta_info={
                    "model": ai_response["model"],
                    "tokens": ai_response["tokens_used"],
                    "cost": ai_response["cost_inr"]
                }
            )
            
            # Check if user wants to proceed with project
            # (Simple keyword detection - can be improved)
            proceed_keywords = ["yes", "proceed", "quote", "let's do it", "create project"]
            should_create_project = any(keyword in user_message.lower() for keyword in proceed_keywords)
            
            # Update task status
            await self.log_task(
                task_type="chat",
                status="completed",
                output_data={"response": assistant_message},
                ai_response=ai_response
            )
            
            return {
                "response": assistant_message,
                "should_create_project": should_create_project,
                "cost": ai_response["cost_inr"]
            }
            
        except Exception as e:
            # Log failure
            await self.log_task(
                task_type="chat",
                status="failed",
                output_data={"error": str(e)}
            )
            raise