import asyncio
from ollama import AsyncClient


async def chat_with_npc():
    client = AsyncClient()
    response = await client.chat(
        model="deepseek-r1",
        messages=[
            {
                "role": "system",
                "content": "You are a friendly tavern keeper in a fantasy world.",
            },
            {"role": "user", "content": "Hello! What's the news around here?"},
        ],
    )
    print(response["message"]["content"])


asyncio.run(chat_with_npc())
