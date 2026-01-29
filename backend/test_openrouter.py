"""
Test OpenRouter API integration
Run this to verify OpenRouter is working correctly
"""
import asyncio
import os
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

async def test_openrouter():
    """Test OpenRouter API call"""
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("AGENT_MODEL", "openai/gpt-4-turbo")

    print(f"Testing OpenRouter...")
    print(f"API Key: {api_key[:20]}..." if api_key else "API Key: NOT FOUND")
    print(f"Model: {model}")

    client = AsyncOpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
        default_headers={
            "HTTP-Referer": "http://localhost:3000",  # Required by OpenRouter
            "X-Title": "TaskFlow AI Chatbot",  # Optional, for rankings
        }
    )

    try:
        print("\n🚀 Sending test message to OpenRouter...")
        completion = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'Hello! OpenRouter is working!' in one sentence."}
            ]
        )

        response = completion.choices[0].message.content
        print(f"\n✅ SUCCESS! Response from OpenRouter:")
        print(f"   {response}")
        return True

    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    asyncio.run(test_openrouter())
