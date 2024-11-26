import asyncio
from assistant_core.ai_integration import AIIntegration
from assistant_core.weather_service import WeatherService

async def test_assistant():
    # Initialize the AI integration
    ai = AIIntegration()
    
    # Test weather service directly
    print("\nTesting Weather Service:")
    weather = WeatherService()
    result = weather.get_weather("London")
    print(f"Weather in London: {result}")
    
    # Test AI with weather
    print("\nTesting AI with weather query:")
    response = await ai.get_enhanced_response("What's the weather like in London?")
    print(f"AI Response: {response}")
    
    # Test AI with general question
    print("\nTesting AI with general question:")
    response = await ai.get_enhanced_response("What are the benefits of exercise?")
    print(f"AI Response: {response}")
    
    # Test system command generation
    print("\nTesting system command generation:")
    command = ai.generate_system_command("open chrome and go to google.com")
    print(f"System Command: {command}")

if __name__ == "__main__":
    asyncio.run(test_assistant())
