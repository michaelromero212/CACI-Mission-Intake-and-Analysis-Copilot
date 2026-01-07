"""
Hugging Face LLM client with cost tracking.
"""
import httpx
import logging
from typing import Dict, Any, Optional
from pathlib import Path

from config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Prompts directory
PROMPTS_DIR = Path(__file__).parent.parent.parent / "prompts"


def load_prompt(prompt_name: str) -> str:
    """Load a prompt template from the prompts directory."""
    prompt_path = PROMPTS_DIR / f"{prompt_name}.txt"
    if prompt_path.exists():
        return prompt_path.read_text()
    logger.warning(f"Prompt {prompt_name} not found at {prompt_path}")
    return ""


class HuggingFaceLLMClient:
    """
    Hugging Face Inference API client.
    
    Uses the free Inference API for text generation.
    Tracks token usage for cost transparency (though HF free tier is $0).
    """
    
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or settings.huggingface_api_key
        self.model = model or settings.huggingface_model
        # Use the new OpenAI-compatible Inference Providers API
        self.base_url = "https://router.huggingface.co/v1/chat/completions"
        self.total_tokens_used = 0
        self.total_requests = 0
        
    async def generate(
        self,
        prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Generate text using Hugging Face Inference API (OpenAI-compatible).
        
        Returns dict with:
        - text: Generated text
        - input_tokens: Estimated input token count
        - output_tokens: Estimated output token count
        - model: Model used
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Use OpenAI-compatible chat completions format
        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        # Estimate input tokens (rough approximation: ~4 chars per token)
        input_tokens = len(prompt) // 4
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self.base_url,
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Handle OpenAI-compatible response format
                    if "choices" in result and len(result["choices"]) > 0:
                        generated_text = result["choices"][0].get("message", {}).get("content", "")
                    else:
                        generated_text = str(result)
                    
                    # Use actual token counts from response if available
                    usage = result.get("usage", {})
                    input_tokens = usage.get("prompt_tokens", input_tokens)
                    output_tokens = usage.get("completion_tokens", len(generated_text) // 4)
                    
                    self.total_tokens_used += input_tokens + output_tokens
                    self.total_requests += 1
                    
                    return {
                        "text": generated_text,
                        "input_tokens": input_tokens,
                        "output_tokens": output_tokens,
                        "total_tokens": input_tokens + output_tokens,
                        "model": self.model
                    }
                else:
                    error_msg = f"HuggingFace API error: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    
                    # Return fallback with error
                    return {
                        "text": f"[AI generation failed: {response.status_code}]",
                        "input_tokens": input_tokens,
                        "output_tokens": 0,
                        "total_tokens": input_tokens,
                        "model": self.model,
                        "error": error_msg
                    }
                    
        except httpx.TimeoutException as e:
            logger.error(f"LLM request timed out: {str(e)}")
            return {
                "text": "[AI generation failed: Request timed out]",
                "input_tokens": input_tokens,
                "output_tokens": 0,
                "total_tokens": input_tokens,
                "model": self.model,
                "error": f"Timeout: {str(e)}"
            }
        except httpx.RequestError as e:
            logger.error(f"LLM request failed: {str(e)}")
            return {
                "text": f"[AI generation failed: Network error]",
                "input_tokens": input_tokens,
                "output_tokens": 0,
                "total_tokens": input_tokens,
                "model": self.model,
                "error": f"Network error: {str(e)}"
            }
        except Exception as e:
            # Catch-all for unexpected errors
            logger.error(f"Unexpected LLM error: {str(e)}")
            return {
                "text": f"[AI generation failed: {str(e)}]",
                "input_tokens": input_tokens,
                "output_tokens": 0,
                "total_tokens": input_tokens,
                "model": self.model,
                "error": str(e)
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get usage statistics."""
        return {
            "total_tokens": self.total_tokens_used,
            "total_requests": self.total_requests,
            "model": self.model
        }
    
    async def test_connection(self) -> Dict[str, Any]:
        """
        Test connection to Hugging Face API.
        
        Returns dict with:
        - connected: Whether the API is reachable
        - model: Model being used
        - response_time_ms: Response time in milliseconds
        - error: Error message if connection failed
        """
        import time
        
        if not self.api_key:
            return {
                "connected": False,
                "model": self.model,
                "response_time_ms": 0,
                "error": "No API key configured"
            }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Use OpenAI-compatible chat completions format for testing
        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": "Hi"}
            ],
            "max_tokens": 1
        }
        
        start_time = time.time()
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.base_url,
                    headers=headers,
                    json=payload
                )
                
                response_time_ms = int((time.time() - start_time) * 1000)
                
                if response.status_code == 200:
                    return {
                        "connected": True,
                        "model": self.model,
                        "response_time_ms": response_time_ms,
                        "error": None
                    }
                elif response.status_code == 503:
                    # Model is loading - still counts as connected
                    return {
                        "connected": True,
                        "model": self.model,
                        "response_time_ms": response_time_ms,
                        "error": "Model is loading, please wait",
                        "loading": True
                    }
                else:
                    error_text = response.text
                    return {
                        "connected": False,
                        "model": self.model,
                        "response_time_ms": response_time_ms,
                        "error": f"API error: {response.status_code} - {error_text[:100]}"
                    }
                    
        except Exception as e:
            response_time_ms = int((time.time() - start_time) * 1000)
            return {
                "connected": False,
                "model": self.model,
                "response_time_ms": response_time_ms,
                "error": str(e)
            }


# Global client instance
_llm_client: Optional[HuggingFaceLLMClient] = None


def get_llm_client() -> HuggingFaceLLMClient:
    """Get or create the LLM client singleton."""
    global _llm_client
    if _llm_client is None:
        _llm_client = HuggingFaceLLMClient()
    return _llm_client
