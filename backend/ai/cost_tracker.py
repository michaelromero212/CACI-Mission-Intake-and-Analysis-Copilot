"""
Cost tracker for AI operations.
"""
from typing import Dict, Any
from config import get_settings

settings = get_settings()


def calculate_cost(
    input_tokens: int,
    output_tokens: int,
    model: str = None
) -> Dict[str, Any]:
    """
    Calculate estimated cost for token usage.
    
    For Hugging Face free tier, cost is $0.
    This is kept for transparency and if users switch to paid APIs.
    
    Args:
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        model: Model name (for future per-model pricing)
        
    Returns:
        Dict with cost breakdown
    """
    input_cost = (input_tokens / 1000) * settings.input_cost_per_1k
    output_cost = (output_tokens / 1000) * settings.output_cost_per_1k
    total_cost = input_cost + output_cost
    
    return {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
        "input_cost": round(input_cost, 6),
        "output_cost": round(output_cost, 6),
        "total_cost": round(total_cost, 6),
        "cost_per_1k_input": settings.input_cost_per_1k,
        "cost_per_1k_output": settings.output_cost_per_1k,
        "model": model or settings.huggingface_model,
        "note": "Using Hugging Face free tier - no cost incurred"
    }


def format_cost_display(cost_data: Dict[str, Any]) -> str:
    """
    Format cost data for user-friendly display.
    """
    return (
        f"Tokens: {cost_data['total_tokens']:,} "
        f"(in: {cost_data['input_tokens']:,}, out: {cost_data['output_tokens']:,}) | "
        f"Est. Cost: ${cost_data['total_cost']:.4f}"
    )
