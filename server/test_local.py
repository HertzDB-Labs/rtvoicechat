#!/usr/bin/env python3
"""
Local test script for the Voice Agent.
Run this script to test the voice agent functionality locally.
"""

import asyncio
import json
from app.voice_agent import VoiceAgent

async def test_voice_agent():
    """Test the voice agent with various inputs."""
    
    print("🧪 Testing Voice Agent...")
    print("=" * 50)
    
    # Initialize voice agent
    voice_agent = VoiceAgent()
    
    # Test system status
    print("\n📊 System Status:")
    status = voice_agent.get_system_status()
    print(json.dumps(status, indent=2))
    
    # Test data loading
    print("\n📋 Data Summary:")
    entities = voice_agent.get_available_entities()
    print(f"Countries loaded: {len(entities['countries'])}")
    print(f"States loaded: {len(entities['states'])}")
    
    # Test cases
    test_cases = [
        "What is the capital of France?",
        "What's the capital of California?",
        "What is the capital of Japan?",
        "What's the capital of Texas?",
        "What's the weather like today?",
        "Tell me about history",
        "What is the capital of Germany?",
        "What's the capital of New York?"
    ]
    
    print("\n🔍 Testing Text Processing:")
    print("=" * 50)
    
    for i, test_input in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_input}")
        print("-" * 40)
        
        try:
            result = await voice_agent.process_text_input(test_input)
            
            if result['success']:
                print(f"✅ Success: {result['response']}")
                if result.get('query_type'):
                    print(f"   Type: {result['query_type']}")
                if result.get('entity'):
                    print(f"   Entity: {result['entity']}")
                if result.get('capital'):
                    print(f"   Capital: {result['capital']}")
            else:
                print(f"❌ Error: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
    
    print("\n" + "=" * 50)
    print("✅ Testing complete!")

def test_data_handler():
    """Test the data handler directly."""
    print("\n🔍 Testing Data Handler:")
    print("=" * 50)
    
    from app.data_handler import DataHandler
    
    handler = DataHandler()
    
    # Test country lookups
    test_countries = ["France", "Japan", "Germany", "United States", "Canada"]
    for country in test_countries:
        capital = handler.find_country_capital(country)
        print(f"Country: {country} → Capital: {capital}")
    
    # Test state lookups
    test_states = ["California", "Texas", "New York", "Florida", "Alaska"]
    for state in test_states:
        capital = handler.find_state_capital(state)
        print(f"State: {state} → Capital: {capital}")
    
    # Test combined lookup
    test_entities = ["France", "California", "Japan", "Texas"]
    for entity in test_entities:
        capital = handler.find_capital(entity)
        print(f"Entity: {entity} → Capital: {capital}")

if __name__ == "__main__":
    print("🚀 Voice Agent Local Test Suite")
    print("=" * 50)
    
    # Test data handler
    test_data_handler()
    
    # Test voice agent
    asyncio.run(test_voice_agent()) 