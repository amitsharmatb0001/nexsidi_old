"""
AI Router Enhancements for Production
======================================

Add to your existing ai_router.py:

1. Gemini Vision support (for BRAND AGENT)
2. Automatic retry with exponential backoff (for rate limits)
3. Request deduplication (prevent duplicate calls)

Copy these methods into your AIRouter class.
"""

import asyncio
import hashlib
from typing import Dict, Any, List, Optional

# ==============================================================================
# ENHANCEMENT 1: Gemini Vision Support (Add to AIRouter class)
# ==============================================================================

def _convert_content_to_gemini(self, content):
    """
    Convert message content to Gemini format (handles multimodal).
    
    Supports:
    - Plain text strings
    - Multimodal content (text + images)
    
    Add this method to AIRouter class around line 230.
    """
    # Simple string content
    if isinstance(content, str):
        return [{"text": content}]
    
    # Multimodal content list
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, str):
                # Text part
                parts.append({"text": item})
            elif isinstance(item, dict) and item.get("type") == "image":
                # Image part (base64)
                parts.append({
                    "inline_data": {
                        "mime_type": item["source"]["media_type"],
                        "data": item["source"]["data"]
                    }
                })
        return parts
    
    # Fallback
    return [{"text": str(content)}]


# UPDATE _call_vertex method around line 583-589:
# FIND THIS CODE:
"""
contents = []
for msg in messages:
    role = "user" if msg["role"] == "user" else "model"
    contents.append({
        "role": role,
        "parts": [{"text": msg["content"]}]
    })
"""

# REPLACE WITH:
"""
contents = []
for msg in messages:
    role = "user" if msg["role"] == "user" else "model"
    
    # Handle both string and multimodal content
    parts = self._convert_content_to_gemini(msg["content"])
    
    contents.append({
        "role": role,
        "parts": parts
    })
"""

# ==============================================================================
# ENHANCEMENT 2: Automatic Retry with Exponential Backoff
# ==============================================================================

async def _call_with_retry(
    self,
    call_func,
    max_retries: int = 3,
    base_delay: int = 10,
    **kwargs
) -> Any:
    """
    Call AI provider with automatic retry on rate limits.
    
    Implements exponential backoff:
    - Retry 1: Wait 10 seconds
    - Retry 2: Wait 20 seconds
    - Retry 3: Wait 40 seconds
    
    Add this method to AIRouter class around line 450.
    
    Args:
        call_func: The provider call function (_call_claude, _call_vertex, etc.)
        max_retries: Maximum number of retry attempts
        base_delay: Base delay in seconds (doubles each retry)
        **kwargs: Arguments to pass to call_func
    
    Returns:
        Response from AI provider
    
    Raises:
        Exception if all retries exhausted
    """
    for attempt in range(max_retries):
        try:
            # Try to call the provider
            return await call_func(**kwargs)
            
        except Exception as e:
            error_msg = str(e)
            
            # Check if it's a rate limit error
            is_rate_limit = (
                "429" in error_msg or 
                "rate_limit" in error_msg.lower() or
                "quota" in error_msg.lower() or
                "too many requests" in error_msg.lower()
            )
            
            if is_rate_limit and attempt < max_retries - 1:
                # Calculate delay with exponential backoff
                delay = base_delay * (2 ** attempt)
                
                self.logger.warning(
                    f"⏱️  Rate limit hit. Retrying in {delay}s "
                    f"(attempt {attempt + 1}/{max_retries})"
                )
                
                # Wait before retry
                await asyncio.sleep(delay)
                continue
            
            # Not a rate limit error, or max retries exceeded
            if attempt == max_retries - 1:
                self.logger.error(f"❌ Max retries ({max_retries}) exceeded")
            
            raise


# UPDATE _call_model method around line 450:
# FIND THIS CODE:
"""
async def _call_model(self, ...):
    if provider == "claude":
        return await self._call_claude(...)
    elif provider == "vertex_ai":
        return await self._call_vertex(...)
"""

# REPLACE WITH:
"""
async def _call_model(self, ...):
    if provider == "claude":
        return await self._call_with_retry(
            self._call_claude,
            messages=messages,
            system_prompt=system_prompt,
            max_tokens=max_tokens,
            temperature=temperature
        )
    elif provider == "vertex_ai":
        return await self._call_with_retry(
            self._call_vertex,
            messages=messages,
            system_prompt=system_prompt,
            max_tokens=max_tokens,
            temperature=temperature
        )
"""

# ==============================================================================
# ENHANCEMENT 3: Request Deduplication (Prevent Duplicate Calls)
# ==============================================================================

def _generate_request_hash(
    self,
    messages: List[Dict],
    system_prompt: Optional[str],
    task_type: str
) -> str:
    """
    Generate unique hash for a request.
    
    Prevents duplicate API calls for identical requests within a short time window.
    
    Add this method to AIRouter class.
    """
    # Create hash from request parameters
    content = json.dumps({
        "messages": messages,
        "system_prompt": system_prompt,
        "task_type": task_type
    }, sort_keys=True)
    
    return hashlib.md5(content.encode()).hexdigest()


# Add to __init__ method:
"""
def __init__(self):
    # ... existing code ...
    
    # Request deduplication cache (in-memory)
    self._request_cache = {}
    self._cache_ttl = 60  # Cache for 60 seconds
"""


# UPDATE generate method around line 280:
# ADD THIS CODE at the beginning of generate():
"""
async def generate(self, messages, system_prompt=None, task_type="general", ...):
    # Check cache for duplicate requests
    request_hash = self._generate_request_hash(messages, system_prompt, task_type)
    
    if request_hash in self._request_cache:
        cached = self._request_cache[request_hash]
        
        # Check if cache is still valid (within TTL)
        if time.time() - cached["timestamp"] < self._cache_ttl:
            self.logger.info(f"♻️  Using cached response (hash: {request_hash[:8]})")
            return cached["response"]
    
    # ... rest of existing code ...
    
    # After successful response, cache it:
    self._request_cache[request_hash] = {
        "response": response,
        "timestamp": time.time()
    }
    
    # Clean old cache entries (keep cache size manageable)
    if len(self._request_cache) > 100:
        # Remove entries older than TTL
        cutoff = time.time() - self._cache_ttl
        self._request_cache = {
            k: v for k, v in self._request_cache.items()
            if v["timestamp"] > cutoff
        }
"""

# ==============================================================================
# SUMMARY OF CHANGES
# ==============================================================================

"""
Three enhancements to add to ai_router.py:

1. ✅ Gemini Vision Support
   - Add _convert_content_to_gemini() method
   - Update _call_vertex() to use it
   - Enables BRAND AGENT to send screenshots

2. ✅ Automatic Retry with Exponential Backoff
   - Add _call_with_retry() method
   - Update _call_model() to use it
   - Prevents demo failures from rate limits

3. ✅ Request Deduplication
   - Add _generate_request_hash() method
   - Update generate() to check cache
   - Prevents duplicate API calls (saves money + avoids rate limits)

IMPACT:
- BRAND AGENT will work (needs vision support)
- Rate limit errors won't crash demo (auto-retry)
- Duplicate requests avoided (saves ₹₹₹)
"""

# ==============================================================================
# TESTING
# ==============================================================================

"""
Test these enhancements:

# Test 1: Gemini Vision
from app.agents.brand_agent import BrandAgent
from app.agents.aarav_testing import AaravTesting

aarav = AaravTesting("test-001")
brand = BrandAgent("test-001")

screenshots = await aarav.capture_screenshots("https://example.com")
result = await brand.evaluate_screenshots(screenshots, "Test business")

# Should work without errors ✅


# Test 2: Rate Limit Retry
# Trigger multiple requests rapidly to hit rate limit
# System should auto-retry instead of failing ✅


# Test 3: Deduplication
# Send same request twice within 60 seconds
# Second request should use cache (faster + cheaper) ✅
"""
