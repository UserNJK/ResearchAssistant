"""
OpenRouter LLM Integration
Provides a simple interface to call LLMs via OpenRouter API
"""
import httpx
import logging
import hashlib
import time
from typing import Optional, Dict, Any
from collections import OrderedDict
from ..config import settings

logger = logging.getLogger(__name__)


class OpenRouterError(Exception):
    """Custom exception for OpenRouter API errors"""
    pass


# In-memory cache for LLM responses (max 100 entries)
_response_cache: OrderedDict[str, str] = OrderedDict()
_cache_max_size = 100

# Rate limiting tracking,
    use_cache: bool = True
) -> str:
    """
    Call an LLM via OpenRouter API with retry and fallback logic
    
    Args:
        prompt: The text prompt to send to the LLM
        model: Model identifier (defaults to config default)
        temperature: Sampling temperature (defaults to config default)
        max_tokens: Maximum tokens in response (defaults to config default)
        use_cache: Whether to use cached responses (default True)
    
    Returns:
        str: The LLM's response text
    
    Raises:
        OpenRouterError: If the API call fails after retries
    """
    # Use defaults from config if not provided
    model = model or settings.DEFAULT_FALLBACK_MODEL
    temperature = temperature if temperature is not None else settings.LLM_TEMPERATURE
    max_tokens = max_tokens or settings.LLM_MAX_TOKENS
    
    # Check cache first
    if use_cache:
        cache_key = _get_cache_key(prompt, model, temperature, max_tokens)
        if cache_key in _response_cache:
            logger.info(f"Cache hit for prompt: {prompt[:50]}...")
            return _response_cache[cache_key]
    
    # Validate OpenRouter API key
    if not settings.OPENROUTER_API_KEY:
        raise OpenRouterError(
            "OPENROUTER_API_KEY not configured. "
            "Add your API key to backend/.env or get one from https://openrouter.ai/settings/keys"
        )
    
    # Rate limiting check
    try:
        _check_rate_limit()
    except OpenRouterError as e:
        logger.warning(str(e))
        raise
    Enforce minimum interval between API calls
    Raises OpenRouterError if called too quickly
    """
    global _last_call_time
    
    current_time = time.time()
    time_since_last_call = current_time - _last_call_time
    
    if _last_call_time > 0 and time_since_last_call < _min_call_interval:
        wait_time = _min_call_interval - time_since_last_call
        raise OpenRouterError(
            f"Rate limit: Please wait {wait_time:.1f}s before next call "
            f"(minimum {_min_call_interval}s interval)"
        )
    
    _last_call_time = current_time


async def call_llm(
    prompt: str,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None
) -> str:
    """
    Call an LLM via OpenRouter API with retry and fallback logic
    
    Args:
        prompt: The text prompt to send to the LLM
        model: Model identifier (defaults to config default)
        temperature: Sampling temperature (defaults to config default)
        max_tokens: Maximum tokens in response (defaults to config default)
    
    Returns:
        str: The LLM's response text
    
    Raises:
        OpenRouterError: If the API call fails after retries
    """
    # Use defaults from config if not provided
    model = model or settings.DEFAULT_FALLBACK_MODEL
    temperature = temperature if temperature is not None else settings.LLM_TEMPERATURE
    max_tokens = max_tokens or settings.LLM_MAX_TOKENS
    
    # Validate OpenRouter API key
    if not settings.OPENROUTER_API_KEY:
        raise OpenRouterError("OPENROUTER_API_KEY not configured")
    
    # Prepare request payload
    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
        
        # Cache successful response
        if use_cache:
            cache_key = _get_cache_key(prompt, model, temperature, max_tokens)
            _add_to_cache(cache_key, response)
            logger.debug(f"Cached response (cache size: {len(_response_cache)})")
        
        return response
    except OpenRouterError as e:
        logger.warning(f"First attempt failed with {model}: {e}")
        
        # Provid
                # Cache successful fallback response
                if use_cache:
                    cache_key = _get_cache_key(prompt, settings.DEFAULT_FALLBACK_MODEL, temperature, max_tokens)
                    _add_to_cache(cache_key, response)
                
                return response
            except OpenRouterError as retry_error:
                logger.error(f"Fallback attempt also failed: {retry_error}")
                
                # Provide helpful message for quota errors
                if "limit exceeded" in str(retry_error).lower() or "403" in str(retry_error):
                    raise OpenRouterError(
                        f"OpenRouter API quota exceeded on both attempts. "
                        f"Free-tier limits are expected. Wait for reset or get new key from "
                        f"https://openrouter.ai/settings/keys"
                    )
                
                f"OpenRouter API quota exceeded. This is normal for free-tier keys. "
                f"Solutions: (1) Wait for quota reset, (2) Get new key from https://openrouter.ai/settings/keys, "
                f"or (3) Add credits. Original error: {e}"
            
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False  # No streaming as per requirements
    }
    
    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/ResearchAssistant",  # Optional: for rankings
        "X-Title": "ResearchAssistant"  # Optional: for rankings
    }
    
    # First attempt with specified model
    try:
        logger.info(f"Calling OpenRouter API with model: {model}")
        response = await _make_api_call(payload, headers)
        return response
    except OpenRouterError as e:
        logger.warning(f"First attempt failed with {model}: {e}")
        
        # Retry once with fallback model if different from original
        if model != settings.DEFAULT_FALLBACK_MODEL:
            logger.info(f"Retrying with fallback model: {settings.DEFAULT_FALLBACK_MODEL}")
            payload["model"] = settings.DEFAULT_FALLBACK_MODEL
            
            try:
                response = await _make_api_call(payload, headers)
                return response
            except OpenRouterError as retry_error:
                logger.error(f"Fallback attempt also failed: {retry_error}")
                raise OpenRouterError(
                    f"LLM call failed after retry. Original: {e}, Fallback: {retry_error}"
                )
        else:
            # Al
                # Provide context for common errors
                if response.status_code == 403:
                    raise OpenRouterError(
                        f"API quota/limit exceeded (403). Free-tier keys have usage limits. "
                        f"Check https://openrouter.ai/settings/keys for usage stats. Detail: {error_detail}"
                    )
                elif response.status_code == 401:
                    raise OpenRouterError(
                        f"Invalid API key (401). Get a valid key from https://openrouter.ai/settings/keys"
                    )
                elif response.status_code == 429:
                    raise OpenRouterError(
                        f"Rate limit exceeded (429). Wait before making more requests. Detail: {error_detail}"
                    )
                else:
                    raise OpenRouterError(
                        f"API returned status {response.status_code}: {error_detail}"
    

async def _make_api_call(payload: Dict[str, Any], headers: Dict[str, str]) -> str:
    """
    Internal function to make the actual HTTP request to OpenRouter
    
    Args:
        payload: Request body
        headers: Request headers
    
    Returns:
        str: The LLM response text
    
    Raises:
        OpenRouterError: If the request fails
    """
    async with httpx.AsyncClient(timeout=settings.LLM_TIMEOUT_SECONDS) as client:
        try:
            response = await client.post(
                f"{settings.OPENROUTER_BASE_URL}/chat/completions",
                json=payload,
                headers=headers
            )
            
            # Check for HTTP errors
            if response.status_code != 200:
                error_detail = response.text
                logger.error(f"OpenRouter API error ({response.status_code}): {error_detail}")
                raise OpenRouterError(
                    f"API returned status {response.status_code}: {error_detail}"
                )
            
            # Parse response
            data = response.json()
            
            # Extract message content
            if "choices" not in data or len(data["choices"]) == 0:
                raise OpenRouterError("No choices returned from API")
            
            message = data["choices"][0].get("message", {})
            content = message.get("content", ""), use_cache=True)
        return {
            "status": "success",
            "model": settings.DEFAULT_FALLBACK_MODEL,
            "response": response,
            "message": "OpenRouter connection successful",
            "cache_info": {
                "size": len(_response_cache),
                "max_size": _cache_max_size
            }
        }
    except OpenRouterError as e:
        return {
            "status": "error",
            "model": settings.DEFAULT_FALLBACK_MODEL,
            "error": str(e),
            "message": "OpenRouter connection failed",
            "help": "Free-tier API limits are normal. Check https://openrouter.ai/settings/keys"
        }


def clear_cache() -> int:
    """
    Clear the response cache
    Returns number of entries cleared
    """
    global _response_cache
    size = len(_response_cache)
    _response_cache.clear()
    logger.info(f"Cleared {size} cached responses")
    return size


def get_cache_stats() -> Dict[str, Any]:
    """
    Get cache statistics
    Returns cache size and configuration
    """
    return {
        "current_size": len(_response_cache),
        "max_size": _cache_max_size,
        "rate_limit_interval": _min_call_interval,
        "last_call_time": _last_call_time
        raise OpenRouterError(f"Network error: {str(e)}")
        except KeyError as e:
            raise OpenRouterError(f"Unexpected response format: missing {str(e)}")
        except Exception as e:
            raise OpenRouterError(f"Unexpected error: {str(e)}")


async def test_llm_connection() -> Dict[str, Any]:
    """
    Test the OpenRouter connection with a simple prompt
    Useful for health checks and diagnostics
    
    Returns:
        dict: Test results with status and response info
    """
    test_prompt = "Say 'Hello' in one word."
    
    try:
        response = await call_llm(test_prompt, max_tokens=10)
        return {
            "status": "success",
            "model": settings.DEFAULT_FALLBACK_MODEL,
            "response": response,
            "message": "OpenRouter connection successful"
        }
    except OpenRouterError as e:
        return {
            "status": "error",
            "model": settings.DEFAULT_FALLBACK_MODEL,
            "error": str(e),
            "message": "OpenRouter connection failed"
        }
