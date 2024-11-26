import pytest
import asyncio
import json
from unittest.mock import Mock, patch
from src.assistant_core.ai_integration import AIIntegration, CommandType, CommandIntent

@pytest.fixture
async def ai_integration():
    """Create a test instance of AIIntegration"""
    integration = AIIntegration()
    integration.openai_client = Mock()
    integration.gemini_model = Mock()
    integration.logger = Mock()
    return integration

@pytest.mark.asyncio
async def test_multi_model_response_success(ai_integration):
    """Test successful multi-model response generation"""
    # Mock responses
    ai_integration.get_openai_response.return_value = "OpenAI response"
    ai_integration.get_gemini_response.return_value = "Gemini response"
    
    # Test message
    message = "What is the weather like today?"
    result = await ai_integration.multi_model_response(message)
    
    assert result["success"] is True
    assert "response" in result
    assert "metadata" in result
    assert "models_used" in result["metadata"]
    assert result["metadata"]["confidence"] > 0

@pytest.mark.asyncio
async def test_multi_model_response_failure(ai_integration):
    """Test multi-model response with model failures"""
    # Mock failures
    ai_integration.get_openai_response.side_effect = Exception("OpenAI error")
    ai_integration.get_gemini_response.side_effect = Exception("Gemini error")
    
    result = await ai_integration.multi_model_response("test message")
    
    assert result["success"] is False
    assert "error" in result

@pytest.mark.asyncio
async def test_generate_system_command_success(ai_integration):
    """Test successful system command generation"""
    # Mock response
    ai_integration.get_response.return_value = json.dumps({
        "command_type": "system",
        "action": "check_status",
        "parameters": {"component": "cpu"},
        "confidence": 0.9
    })
    
    result = await ai_integration.generate_system_command("Check system CPU status")
    
    assert isinstance(result, CommandIntent)
    assert result.command_type == CommandType.SYSTEM
    assert result.confidence >= 0.8

@pytest.mark.asyncio
async def test_generate_system_command_low_confidence(ai_integration):
    """Test system command generation with low confidence"""
    # Mock response with low confidence
    ai_integration.get_response.return_value = json.dumps({
        "command_type": "system",
        "action": "unknown_action",
        "parameters": {},
        "confidence": 0.3
    })
    
    result = await ai_integration.generate_system_command("Do something unclear")
    
    assert result is None

@pytest.mark.asyncio
async def test_response_quality_assessment(ai_integration):
    """Test response quality assessment"""
    analysis = {
        "complexity": 0.8,
        "required_capabilities": ["technical", "analysis"],
        "response_type": "analytical"
    }
    
    # Test good response
    good_response = """Here's a detailed analysis:
    1. First point
    2. Second point
    • Technical details
    • Analysis results"""
    
    good_score = ai_integration._assess_response_quality(good_response, analysis)
    assert good_score > 0.7
    
    # Test poor response
    poor_response = "ok"
    poor_score = ai_integration._assess_response_quality(poor_response, analysis)
    assert poor_score < 0.5

@pytest.mark.asyncio
async def test_model_selection(ai_integration):
    """Test model selection logic"""
    # Test analytical request
    analytical_analysis = {
        "complexity": 0.9,
        "response_type": "analytical",
        "required_capabilities": ["code", "technical"]
    }
    models = ai_integration._select_models(analytical_analysis)
    assert "openai" in models
    
    # Test creative request
    creative_analysis = {
        "complexity": 0.5,
        "response_type": "creative",
        "required_capabilities": ["visual", "creative"]
    }
    models = ai_integration._select_models(creative_analysis)
    assert "gemini" in models

@pytest.mark.asyncio
async def test_response_synthesis(ai_integration):
    """Test response synthesis"""
    responses = [
        {"response": "First response", "model": "openai", "quality_score": 0.9},
        {"response": "Second response", "model": "gemini", "quality_score": 0.8}
    ]
    
    analysis = {"complexity": 0.8}
    
    # Mock synthesized response
    ai_integration.get_response.return_value = "Combined response"
    
    result = await ai_integration._synthesize_responses(responses, analysis)
    
    assert "response" in result
    assert "quality_score" in result
    assert "confidence" in result
    assert "processing_time" in result

@pytest.mark.asyncio
async def test_response_stats_tracking(ai_integration):
    """Test response statistics tracking"""
    response = {
        "quality_score": 0.9,
        "processing_time": 100,
        "confidence": 0.85
    }
    
    # Track multiple responses
    for _ in range(5):
        ai_integration._update_response_stats(response)
    
    assert hasattr(ai_integration, 'response_stats')
    assert len(ai_integration.response_stats) == 5
    assert all(stat["quality_score"] == 0.9 for stat in ai_integration.response_stats)

@pytest.mark.asyncio
async def test_error_handling(ai_integration):
    """Test error handling in various scenarios"""
    # Test invalid JSON response
    ai_integration.get_response.return_value = "invalid json"
    result = await ai_integration._analyze_request("test message")
    assert isinstance(result, dict)
    assert "complexity" in result  # Should return default values
    
    # Test timeout handling
    ai_integration.get_response.side_effect = asyncio.TimeoutError()
    result = await ai_integration.multi_model_response("test message")
    assert result["success"] is False
    assert "timeout" in result["error"].lower()
    
    # Test general exception handling
    ai_integration.get_response.side_effect = Exception("Unknown error")
    result = await ai_integration.multi_model_response("test message")
    assert result["success"] is False
    assert "error" in result
