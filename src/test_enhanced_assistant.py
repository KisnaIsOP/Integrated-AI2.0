import asyncio
from assistant_core.ai_integration import AIIntegration
from assistant_core.weather_service import WeatherService
from assistant_core.system_control import SystemController

async def test_enhanced_assistant():
    print("\n=== Testing Enhanced AI Assistant ===\n")
    
    # Initialize the AI integration
    ai = AIIntegration()
    
    # Test 1: Basic conversation with memory
    print("\n1. Testing Basic Conversation with Memory:")
    response = await ai.get_enhanced_response("Hello! How can you help me?")
    print(f"AI Response: {response}")
    
    # Test 2: Weather query
    print("\n2. Testing Weather Integration:")
    response = await ai.get_enhanced_response("What's the weather like in London?")
    print(f"AI Response: {response}")
    
    # Test 3: System control
    print("\n3. Testing System Control:")
    response = await ai.get_enhanced_response("Can you open Notepad for me?")
    print(f"AI Response: {response}")
    
    # Test 4: System information
    print("\n4. Testing System Information:")
    response = await ai.get_enhanced_response("What's my current CPU and memory usage?")
    print(f"AI Response: {response}")
    
    # Test 5: Contextual conversation
    print("\n5. Testing Contextual Conversation:")
    response = await ai.get_enhanced_response("Tell me more about system resources")
    print(f"AI Response: {response}")
    
    # Test 6: Web navigation
    print("\n6. Testing Web Navigation:")
    response = await ai.get_enhanced_response("Can you open google.com?")
    print(f"AI Response: {response}")
    
    # Test 7: Combined features
    print("\n7. Testing Combined Features:")
    response = await ai.get_enhanced_response(
        "What's the weather in London and can you also show me my system status?"
    )
    print(f"AI Response: {response}")
    
    print("\n=== Testing Complete ===")

if __name__ == "__main__":
    asyncio.run(test_enhanced_assistant())
