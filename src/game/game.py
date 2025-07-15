## game state
import asyncio
from ollama import AsyncClient
import json
from datetime import datetime
from typing import Dict, List, Optional


class NPC:
    def __init__(self, name: str, role: str, personality: str, location: str):
        self.name = name
        self.role = role
        self.personality = personality
        self.location = location
        self.memory = []  # Store conversation history
        self.client = AsyncClient()

    async def talk(self, player_input: str, player_name: str = "Traveler") -> str:
        """Generate NPC response using LLM"""

        # Build conversation history for context
        messages = [
            {
                "role": "system",
                "content": f"""You are {self.name}, a {self.role} in a fantasy world.
Personality: {self.personality}
You are currently in: {self.location}
Remember previous conversations and refer to them naturally.
Keep responses concise (2-3 sentences) unless asked for more detail.""",
            }
        ]

        # Add conversation history (last 10 exchanges to manage context)
        for memory in self.memory[-10:]:
            messages.append({"role": memory["role"], "content": memory["content"]})

        # Add current player input
        messages.append({"role": "user", "content": f"{player_name}: {player_input}"})

        try:
            # Get response from LLM
            response = await self.client.chat(
                model="deepseek-r1", messages=messages  # Using deepseek-r1 as specified
            )

            npc_response = response["message"]["content"]

            # Store this exchange in memory
            self.memory.append(
                {"role": "user", "content": f"{player_name}: {player_input}"}
            )
            self.memory.append({"role": "assistant", "content": npc_response})

            return npc_response

        except Exception as e:
            return f"*{self.name} seems distracted and doesn't respond properly* (Error: {e})"


class GameWorld:
    def __init__(self):
        self.locations = {
            "tavern": {
                "description": "A cozy tavern with a crackling fireplace. The smell of ale and roasted meat fills the air.",
                "exits": {"outside": "town_square", "upstairs": "tavern_rooms"},
                "npcs": [],
            },
            "town_square": {
                "description": "The bustling town square. Market stalls line the edges and townsfolk go about their business.",
                "exits": {"tavern": "tavern", "north": "castle_gates"},
                "npcs": [],
            },
            "tavern_rooms": {
                "description": "The upper floor of the tavern. Several doors lead to guest rooms.",
                "exits": {"downstairs": "tavern"},
                "npcs": [],
            },
            "castle_gates": {
                "description": "Massive iron gates stand before you, guarded by stern-looking soldiers.",
                "exits": {"south": "town_square"},
                "npcs": [],
            },
        }

        self.current_location = "tavern"
        self.npcs = {}
        self.player_name = "Traveler"

        # Create our first NPC
        self.create_npc()

    def create_npc(self):
        """Create the tavern keeper NPC"""
        tavern_keeper = NPC(
            name="Gareth",
            role="tavern keeper",
            personality="friendly but gossipy, loves to share local rumors and stories, has a good memory for faces",
            location="tavern",
        )

        # Add NPC to the world
        self.npcs["gareth"] = tavern_keeper
        self.locations["tavern"]["npcs"].append("gareth")

    def get_location_description(self) -> str:
        """Get the current location's description including NPCs"""
        loc = self.locations[self.current_location]
        desc = loc["description"]

        if loc["npcs"]:
            desc += "\n\nPeople here:"
            for npc_id in loc["npcs"]:
                npc = self.npcs[npc_id]
                desc += f"\n- {npc.name} ({npc.role})"

        # Show available exits
        desc += "\n\nExits:"
        for direction, destination in loc["exits"].items():
            desc += f"\n- {direction}"

        return desc

    def move(self, direction: str) -> tuple[bool, str]:
        """Attempt to move in a direction"""
        current = self.locations[self.current_location]

        if direction.lower() in current["exits"]:
            self.current_location = current["exits"][direction.lower()]
            return True, self.get_location_description()
        else:
            return False, "You can't go that way."

    def get_npc_in_location(self, npc_name: str) -> Optional[NPC]:
        """Get an NPC if they're in the current location"""
        current_npcs = self.locations[self.current_location]["npcs"]

        for npc_id in current_npcs:
            npc = self.npcs[npc_id]
            if npc.name.lower() == npc_name.lower():
                return npc

        return None


class Game:
    def __init__(self):
        self.world = GameWorld()
        self.running = True

    def show_help(self):
        """Display available commands"""
        print("\nCommands:")
        print("- look: Describe current location")
        print("- go [direction]: Move in a direction")
        print("- talk [npc name]: Talk to an NPC")
        print("- name [your name]: Set your character name")
        print("- quit: Exit game")
        print("- help: Show this help")

    async def game_loop(self):
        """Main game loop"""
        print("=" * 50)
        print("Welcome to the AI-Powered Fantasy World!")
        print("=" * 50)
        print("\nYou find yourself in a medieval fantasy town...")
        print("\n" + self.world.get_location_description())

        self.show_help()

        while self.running:
            try:
                # Get player input
                user_input = input("\n> ").strip().lower()

                if not user_input:
                    continue

                # Parse commands
                parts = user_input.split(maxsplit=1)
                command = parts[0]
                args = parts[1] if len(parts) > 1 else ""

                # Handle commands
                if command == "quit":
                    print("Thanks for playing!")
                    self.running = False

                elif command == "help":
                    self.show_help()

                elif command == "look":
                    print("\n" + self.world.get_location_description())

                elif command == "go":
                    if args:
                        success, message = self.world.move(args)
                        print(f"\n{message}")
                    else:
                        print("Go where? (e.g., 'go outside')")

                elif command == "talk":
                    if args:
                        npc = self.world.get_npc_in_location(args)
                        if npc:
                            print(f"\nYou approach {npc.name}...")
                            await self.conversation_loop(npc)
                        else:
                            print(f"There's no one called '{args}' here.")
                    else:
                        print("Talk to whom? (e.g., 'talk gareth')")

                elif command == "name":
                    if args:
                        self.world.player_name = args.title()
                        print(f"You are now known as {self.world.player_name}")
                    else:
                        print(f"Your name is {self.world.player_name}")

                else:
                    print("I don't understand that command. Type 'help' for options.")

            except KeyboardInterrupt:
                print("\n\nInterrupted! Type 'quit' to exit properly.")
            except Exception as e:
                print(f"Error: {e}")

    async def conversation_loop(self, npc: NPC):
        """Handle conversation with an NPC"""
        print(f"\n[Talking to {npc.name}. Type 'bye' to end conversation]")

        # Greeting
        greeting = await npc.talk("*walks up to you*", self.world.player_name)
        print(f"\n{npc.name}: {greeting}")

        while True:
            user_input = input(f"\n{self.world.player_name}: ").strip()

            if user_input.lower() in ["bye", "goodbye", "farewell"]:
                farewell = await npc.talk("goodbye", self.world.player_name)
                print(f"\n{npc.name}: {farewell}")
                break

            if user_input:
                response = await npc.talk(user_input, self.world.player_name)
                print(f"\n{npc.name}: {response}")


async def main():
    """Run the game"""
    game = Game()
    await game.game_loop()


if __name__ == "__main__":
    # Run the game
    asyncio.run(main())
