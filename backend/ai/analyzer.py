"""
AI Analyzer - orchestrates LLM-based analysis tasks.

Performs:
- Summarization
- Entity extraction
- Risk classification
- Natural language explanation

All outputs are clearly labeled as AI-generated.
"""
import json
import logging
from typing import Dict, Any, Optional, List

from ai.llm_client import HuggingFaceLLMClient, load_prompt
from ai.cost_tracker import calculate_cost
from ai.rag_service import RAGService

logger = logging.getLogger(__name__)


async def analyze_content(
    content: str,
    llm_client: HuggingFaceLLMClient = None,
    rag_service: RAGService = None
) -> Dict[str, Any]:
    """
    Run full AI analysis on mission content.
    
    Args:
        content: Normalized mission content to analyze
        llm_client: LLM client instance
        rag_service: RAG service for context retrieval
        
    Returns:
        Dict containing all analysis results with cost transparency
    """
    if llm_client is None:
        from ai.llm_client import get_llm_client
        llm_client = get_llm_client()
    
    # Track total tokens
    total_input_tokens = 0
    total_output_tokens = 0
    
    # Get RAG context if available
    context = ""
    if rag_service:
        try:
            context = rag_service.get_context_for_analysis(content)
        except Exception as e:
            logger.warning(f"RAG context retrieval failed: {e}")
    
    # 1. Summarization
    summary = await _generate_summary(content, context, llm_client)
    total_input_tokens += summary.get("input_tokens", 0)
    total_output_tokens += summary.get("output_tokens", 0)
    
    # 2. Entity extraction
    entities = await _extract_entities(content, llm_client)
    total_input_tokens += entities.get("input_tokens", 0)
    total_output_tokens += entities.get("output_tokens", 0)
    
    # 3. Risk classification
    risk = await _classify_risk(content, entities.get("entities", []), llm_client)
    total_input_tokens += risk.get("input_tokens", 0)
    total_output_tokens += risk.get("output_tokens", 0)
    
    # 4. Generate explanation
    explanation = await _generate_explanation(
        summary.get("summary", ""),
        risk.get("risk_level", "medium"),
        entities.get("entities", []),
        llm_client
    )
    total_input_tokens += explanation.get("input_tokens", 0)
    total_output_tokens += explanation.get("output_tokens", 0)
    
    # Calculate cost
    cost_data = calculate_cost(
        total_input_tokens,
        total_output_tokens,
        llm_client.model
    )
    
    # Calculate heuristic confidence score
    confidence = _calculate_confidence(
        summary.get("summary", ""),
        entities.get("entities", []),
        content
    )
    
    return {
        "summary": f"[AI-Generated] {summary.get('summary', 'Analysis pending')}",
        "entities": entities.get("entities", []),
        "risk_level": risk.get("risk_level", "medium"),
        "explanation": f"[AI-Generated] {explanation.get('explanation', '')}",
        "model": llm_client.model,
        "input_tokens": total_input_tokens,
        "output_tokens": total_output_tokens,
        "total_tokens": total_input_tokens + total_output_tokens,
        "estimated_cost": cost_data["total_cost"],
        "confidence_score": confidence
    }


async def _generate_summary(
    content: str,
    context: str,
    llm_client: HuggingFaceLLMClient
) -> Dict[str, Any]:
    """Generate a summary of the content."""
    prompt_template = load_prompt("summarize")
    
    if not prompt_template:
        # Fallback prompt
        prompt_template = "Summarize the following content in 3-5 sentences:\n\n{content}"
    
    prompt = prompt_template.format(
        content=content[:3000],  # Limit content length
        context=context[:1000] if context else "No additional context available."
    )
    
    result = await llm_client.generate(prompt, max_tokens=300)
    
    return {
        "summary": result.get("text", "").strip(),
        "input_tokens": result.get("input_tokens", 0),
        "output_tokens": result.get("output_tokens", 0)
    }


async def _extract_entities(
    content: str,
    llm_client: HuggingFaceLLMClient
) -> Dict[str, Any]:
    """Extract key entities from content."""
    prompt_template = load_prompt("extract_entities")
    
    if not prompt_template:
        prompt_template = "Extract key entities from this text as a JSON array:\n\n{content}"
    
    prompt = prompt_template.format(content=content[:3000])
    
    result = await llm_client.generate(prompt, max_tokens=500)
    
    # Parse entities from response
    entities = _parse_entities(result.get("text", ""))
    
    return {
        "entities": entities,
        "input_tokens": result.get("input_tokens", 0),
        "output_tokens": result.get("output_tokens", 0)
    }


def _parse_entities(text: str) -> List[Dict[str, Any]]:
    """Parse entity extraction response into structured format."""
    try:
        # Try to find JSON array in response
        start = text.find('[')
        end = text.rfind(']') + 1
        
        if start >= 0 and end > start:
            json_str = text[start:end]
            entities = json.loads(json_str)
            
            # Validate structure
            valid_entities = []
            for entity in entities:
                if isinstance(entity, dict) and "name" in entity:
                    valid_entities.append({
                        "name": entity.get("name", "Unknown"),
                        "type": entity.get("type", "UNKNOWN"),
                        "relevance": entity.get("relevance", "medium")
                    })
            return valid_entities
    except (json.JSONDecodeError, Exception) as e:
        logger.warning(f"Failed to parse entities: {e}")
    
    # Fallback: extract simple entities
    return [{"name": "Analysis pending", "type": "SYSTEM", "relevance": "low"}]


async def _classify_risk(
    content: str,
    entities: List[Dict[str, Any]],
    llm_client: HuggingFaceLLMClient
) -> Dict[str, Any]:
    """Classify risk/priority level."""
    prompt_template = load_prompt("classify_risk")
    
    if not prompt_template:
        prompt_template = "Classify the risk level (LOW, MEDIUM, HIGH, CRITICAL):\n\n{content}"
    
    entities_str = ", ".join([e.get("name", "") for e in entities[:10]])
    prompt = prompt_template.format(
        content=content[:2000],
        entities=entities_str or "No entities identified"
    )
    
    result = await llm_client.generate(prompt, max_tokens=100)
    
    # Parse risk level
    risk_text = result.get("text", "").upper()
    risk_level = "medium"  # Default
    
    for level in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
        if level in risk_text:
            risk_level = level.lower()
            break
    
    return {
        "risk_level": risk_level,
        "input_tokens": result.get("input_tokens", 0),
        "output_tokens": result.get("output_tokens", 0)
    }


async def _generate_explanation(
    summary: str,
    risk_level: str,
    entities: List[Dict[str, Any]],
    llm_client: HuggingFaceLLMClient
) -> Dict[str, Any]:
    """Generate natural language explanation."""
    prompt_template = load_prompt("explain")
    
    if not prompt_template:
        prompt_template = "Explain the analysis in plain language:\n\nSummary: {summary}\nRisk: {risk_level}"
    
    entities_str = ", ".join([e.get("name", "") for e in entities[:5]])
    prompt = prompt_template.format(
        summary=summary[:500],
        risk_level=risk_level,
        entities=entities_str or "None identified"
    )
    
    result = await llm_client.generate(prompt, max_tokens=200)
    
    return {
        "explanation": result.get("text", "").strip(),
        "input_tokens": result.get("input_tokens", 0),
        "output_tokens": result.get("output_tokens", 0)
    }


def _calculate_confidence(
    summary: str,
    entities: list,
    original_content: str
) -> float:
    """
    Calculate heuristic-based confidence score.
    
    This is a simple heuristic, not a true ML confidence score.
    Factors considered:
    - Summary length relative to content
    - Number of entities extracted
    - Content quality indicators
    """
    score = 0.5  # Base score
    
    # Summary quality
    if summary and len(summary) > 50:
        score += 0.1
    if summary and len(summary) > 150:
        score += 0.05
    
    # Entity extraction success
    if entities and len(entities) > 0:
        score += 0.1
    if entities and len(entities) > 3:
        score += 0.05
    
    # Content quality
    content_length = len(original_content)
    if content_length > 500:
        score += 0.1
    if content_length > 2000:
        score += 0.05
    
    # Cap at 0.95 - never show 100% confidence for AI
    return min(round(score, 2), 0.95)
