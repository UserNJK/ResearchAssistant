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

# Rate limiting tracking
_last_call_time = 0.0
_min_call_interval = 0.5  # seconds


def _get_cache_key(prompt: str, model: str, temperature: float, max_tokens: int) -> str:
    """Generate a cache key from request parameters"""
    key_str = f"{prompt}|{model}|{temperature}|{max_tokens}"
    return hashlib.md5(key_str.encode()).hexdigest()


def _check_rate_limit() -> None:
    """
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
    max_tokens: Optional[int] = None,
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
    
    # Prepare request payload
    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False
    }
    
    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/ResearchAssistant",
        "X-Title": "ResearchAssistant"
    }
    
    # First attempt with specified model
    try:
        logger.info(f"Calling OpenRouter API with model: {model}")
        response = await _make_api_call(payload, headers)
        
        # Cache successful response
        if use_cache:
            cache_key = _get_cache_key(prompt, model, temperature, max_tokens)
            _add_to_cache(cache_key, response)
            logger.debug(f"Cached response (cache size: {len(_response_cache)})")
        
        return response
    except OpenRouterError as e:
        logger.warning(f"First attempt failed with {model}: {e}")
        
        # Retry once with fallback model if different from original
        if model != settings.DEFAULT_FALLBACK_MODEL:
            logger.info(f"Retrying with fallback model: {settings.DEFAULT_FALLBACK_MODEL}")
            payload["model"] = settings.DEFAULT_FALLBACK_MODEL
            
            try:
                response = await _make_api_call(payload, headers)
                
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
                
                raise OpenRouterError(
                    f"LLM call failed after retry. Original: {e}, Fallback: {retry_error}"
                )
        else:
            # Already using fallback model
            if "limit exceeded" in str(e).lower() or "403" in str(e):
                raise OpenRouterError(
                    f"OpenRouter API quota exceeded. This is normal for free-tier keys. "
                    f"Solutions: (1) Wait for quota reset, (2) Get new key from https://openrouter.ai/settings/keys, "
                    f"or (3) Add credits. Original error: {e}"
                )
            raise


async def _make_api_call(payload: Dict[str, Any], headers: Dict[str, str]) -> str:
    """
    Make the actual HTTP request to OpenRouter API
    
    Args:
        payload: The request payload
        headers: The request headers
    
    Returns:
        str: The LLM's response text
    
    Raises:
        OpenRouterError: If the API call fails
    """
    timeout = httpx.Timeout(settings.LLM_TIMEOUT_SECONDS, read=settings.LLM_TIMEOUT_SECONDS + 10)
    
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                f"{settings.OPENROUTER_BASE_URL}/chat/completions",
                json=payload,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if "choices" in data and len(data["choices"]) > 0:
                    content = data["choices"][0]["message"]["content"]
                    logger.debug(f"Received response: {content[:100]}...")
                    return content
                else:
                    raise OpenRouterError("Invalid response format: missing choices")
            
            elif response.status_code == 403:
                raise OpenRouterError("API quota exceeded (403)")
            
            elif response.status_code == 401:
                raise OpenRouterError("Invalid API key (401)")
            
            elif response.status_code == 429:
                raise OpenRouterError("Rate limit exceeded (429)")
            
            else:
                error_text = response.text
                raise OpenRouterError(
                    f"API call failed with status {response.status_code}: {error_text}"
                )
    
    except httpx.TimeoutException:
        raise OpenRouterError(f"Request timed out after {settings.LLM_TIMEOUT_SECONDS}s")
    
    except httpx.RequestError as e:
        raise OpenRouterError(f"Network error: {str(e)}")
    
    except Exception as e:
        if isinstance(e, OpenRouterError):
            raise
        raise OpenRouterError(f"Unexpected error: {str(e)}")


def _add_to_cache(key: str, value: str) -> None:
    """Add a response to the cache, removing oldest if at capacity"""
    if len(_response_cache) >= _cache_max_size:
        _response_cache.popitem(last=False)  # Remove oldest (FIFO)
    _response_cache[key] = value


def clear_cache() -> int:
    """
    Clear the response cache
    
    Returns:
        int: Number of entries cleared
    """
    count = len(_response_cache)
    _response_cache.clear()
    logger.info(f"Cleared {count} cached responses")
    return count


def get_cache_stats() -> Dict[str, Any]:
    """
    Get cache statistics
    
    Returns:
        dict: Cache statistics including size, max size, hit rate estimate
    """
    return {
        "cache_size": len(_response_cache),
        "max_cache_size": _cache_max_size,
        "rate_limit_interval": _min_call_interval,
        "last_call_time": _last_call_time
    }


async def test_llm_connection() -> Dict[str, Any]:
    """
    Test the LLM connection with a simple prompt
    
    Returns:
        dict: Test result with status and message
    """
    try:
        response = await call_llm(
            "Say 'Hello' and nothing else.",
            use_cache=False
        )
        return {
            "status": "success",
            "message": "LLM connection successful",
            "response": response
        }
    except OpenRouterError as e:
        return {
            "status": "error",
            "message": str(e)
        }
