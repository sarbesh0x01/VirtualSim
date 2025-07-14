import pygame
from ollama import AsyncClient
import json
from typing import Dict, List, Optional
from datetime import datetime


# NPC class to generate different NPC easily


## NPC class , will be used to create NPC, As expreiments to check the Ai behaviour and if they works or not.
## A NPC resposne will be based on their personality, the character rating, the character world with have keys and the response of the NPC will be also
##depended on their world key are obtained or not..
## Parameters, name, personality, their background
## and so on
class NPC:
    def __init__(self, name: str, personality: str, start_location: str, role: str):
        # For a NPC system
        self.name = name
        self.personality = personality
        self.location = start_location
        self.role = role
        self.memory = []  # to store conversation memory
        self.client = AsyncClient

    async def talk(self, player_input: str, player_name: str) -> str:
        # To generate NPC response using LLM

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

        for memory in self.memory[-10]:
            messages.append(
                {"role": "user", "content": f"{player_name}: {player_input}"}
            )

        return """a"""
