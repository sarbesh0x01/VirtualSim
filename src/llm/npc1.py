import asyncio
from ollama import AsyncClient

# Simple game state
game_state = {"location": "tavern", "npc_memory": [], "player_name": "Traveler"}


async def talk_to_npc(player_input):
    """Talk to the tavern keeper"""
    client = AsyncClient()

    # Build the conversation
    messages = [
        {
            "role": "system",
            "content": """You are Gareth, a friendly tavern keeper in a fantasy world.
You remember previous conversations and refer to them naturally.
Keep responses short (2-3 sentences) unless asked for more.""",
        }
    ]

    # Add memory (last 5 exchanges)
    for memory in game_state["npc_memory"][-10:]:
        messages.append(memory)

    # Add player input
    messages.append({"role": "user", "content": player_input})

    # Get response
    response = await client.chat(model="deepseek-r1", messages=messages)
    npc_response = response["message"]["content"]

    # Save to memory
    game_state["npc_memory"].append({"role": "user", "content": player_input})
    game_state["npc_memory"].append({"role": "assistant", "content": npc_response})

    return npc_response


async def main():
    print("=== Simple AI NPC Game ===")
    print("You're in a tavern. Gareth the tavern keeper is here.")
    print("Commands: talk, look, quit")

    while True:
        command = input("\n> ").strip().lower()

        if command == "quit":
            print("Goodbye!")
            break

        elif command == "look":
            print("\nYou're in a cozy tavern. Gareth is behind the bar.")

        elif command == "talk":
            print("\n[Talking to Gareth - type 'done' to stop]")

            # First greeting
            greeting = await talk_to_npc(
                f"{game_state['player_name']} walks up to the bar"
            )
            print(f"\nGareth: {greeting}")

            # Conversation loop
            while True:
                player_says = input(f"\n{game_state['player_name']}: ")

                if player_says.lower() == "done":
                    break

                response = await talk_to_npc(player_says)
                print(f"\nGareth: {response}")

        else:
            print("Commands: talk, look, quit")


if __name__ == "__main__":
    asyncio.run(main())
