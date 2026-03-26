import os
from dotenv import load_dotenv
from groq import AsyncGroq   # direct Groq client

load_dotenv(override=True)

key = os.getenv("GROQ_API_KEY")
print("Key loaded:", key[:15] + "..." if key else "MISSING")

client = AsyncGroq(api_key=key)

async def test():
    try:
        response = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": "Say hello in one word"}],
            max_tokens=10
        )
        print("✅ Success! Response:", response.choices[0].message.content)
    except Exception as e:
        print("❌ Error:", e)

import asyncio
asyncio.run(test())