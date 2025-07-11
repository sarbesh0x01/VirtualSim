import json
import sys
import threading
from enum import Enum

import pygame
import requests

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
YELLOW = (255, 255, 0)
DARK_GREEN = (0, 128, 0)
BROWN = (139, 69, 19)


class GameState(Enum):
    EXPLORING = 1
    TALKING = 2
    WAITING_FOR_AI = 3


class GameConfig:
    """Game configuration and parameters"""

    API_URL = "http://127.0.0.1:8000/generate"

    WORLD_CONTEXT = """You are an NPC in a fantasy village. You have your own personality,
    memories, and goals. Respond naturally to the player's actions and questions.
    Keep responses under 80 words and be conversational."""

    # Location definitions with coordinates
    LOCATIONS = {
        "town_center": {
            "rect": pygame.Rect(400, 300, 200, 100),
            "color": LIGHT_GRAY,
            "name": "Town Center",
        },
        "market": {
            "rect": pygame.Rect(100, 200, 150, 120),
            "color": YELLOW,
            "name": "Market",
        },
        "tavern": {
            "rect": pygame.Rect(650, 150, 180, 140),
            "color": BROWN,
            "name": "Tavern",
        },
        "guard_post": {
            "rect": pygame.Rect(750, 450, 120, 100),
            "color": GRAY,
            "name": "Guard Post",
        },
    }

    # NPCs with positions and properties
    NPCS = {
        "merchant": {
            "name": "Old Tom",
            "personality": "A grumpy but fair merchant who sells potions and supplies.",
            "location": "market",
            "pos": (175, 250),
            "color": GREEN,
            "inventory": ["health potion", "magic scroll", "rope", "torch"],
        },
        "guard": {
            "name": "Captain Sarah",
            "personality": "A serious town guard who takes her duty seriously.",
            "location": "guard_post",
            "pos": (810, 500),
            "color": BLUE,
            "mood": "suspicious",
        },
        "tavern_keeper": {
            "name": "Merry Bob",
            "personality": "A cheerful tavern keeper who loves gossip and stories.",
            "location": "tavern",
            "pos": (740, 220),
            "color": RED,
            "special": "knows local rumors",
        },
    }


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 3
        self.radius = 15
        self.inventory = ["rusty sword", "5 gold coins"]
        self.current_location = "town_center"

    def move(self, dx, dy):
        self.x += dx * self.speed
        self.y += dy * self.speed

        # Keep player on screen
        self.x = max(self.radius, min(SCREEN_WIDTH - self.radius, self.x))
        self.y = max(
            self.radius, min(SCREEN_HEIGHT - 200, self.y)
        )  # Leave space for UI

        # Update current location based on position
        self.update_location()

    def update_location(self):
        player_rect = pygame.Rect(
            self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2
        )

        for loc_name, loc_data in GameConfig.LOCATIONS.items():
            if player_rect.colliderect(loc_data["rect"]):
                self.current_location = loc_name
                return

        self.current_location = "wilderness"

    def draw(self, screen):
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), self.radius, 2)


class DialogueBox:
    def __init__(self):
        self.active = False
        self.npc_name = ""
        self.npc_text = ""
        self.player_input = ""
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 20)
        self.rect = pygame.Rect(50, SCREEN_HEIGHT - 180, SCREEN_WIDTH - 100, 150)

    def start_conversation(self, npc_key):
        self.active = True
        self.npc_name = GameConfig.NPCS[npc_key]["name"]
        self.npc_text = f"Hello! I'm {self.npc_name}. What would you like to say?"
        self.player_input = ""

    def set_npc_response(self, text):
        self.npc_text = text
        self.player_input = ""

    def handle_input(self, event):
        if not self.active:
            return False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.active = False
                return True
            elif event.key == pygame.K_RETURN:
                if self.player_input.strip():
                    return "send_message"
            elif event.key == pygame.K_BACKSPACE:
                self.player_input = self.player_input[:-1]
            else:
                if len(self.player_input) < 100:  # Limit input length
                    self.player_input += event.unicode
        return False

    def draw(self, screen):
        if not self.active:
            return

        # Draw dialogue box background
        pygame.draw.rect(screen, WHITE, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 3)

        # Draw NPC name
        name_surface = self.font.render(self.npc_name, True, BLACK)
        screen.blit(name_surface, (self.rect.x + 10, self.rect.y + 5))

        # Draw NPC text (word wrap)
        words = self.npc_text.split()
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + word + " "
            if self.small_font.size(test_line)[0] < self.rect.width - 20:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line.strip())
                current_line = word + " "
        if current_line:
            lines.append(current_line.strip())

        for i, line in enumerate(lines[:4]):  # Max 4 lines
            line_surface = self.small_font.render(line, True, BLACK)
            screen.blit(line_surface, (self.rect.x + 10, self.rect.y + 30 + i * 20))

        # Draw input prompt
        prompt_surface = self.small_font.render("You say:", True, BLACK)
        screen.blit(prompt_surface, (self.rect.x + 10, self.rect.y + 110))

        # Draw input box
        input_rect = pygame.Rect(
            self.rect.x + 80, self.rect.y + 108, self.rect.width - 90, 25
        )
        pygame.draw.rect(screen, LIGHT_GRAY, input_rect)
        pygame.draw.rect(screen, BLACK, input_rect, 2)

        # Draw input text
        input_surface = self.small_font.render(self.player_input, True, BLACK)
        screen.blit(input_surface, (input_rect.x + 5, input_rect.y + 3))

        # Draw cursor
        cursor_x = input_rect.x + 5 + self.small_font.size(self.player_input)[0]
        if pygame.time.get_ticks() % 1000 < 500:  # Blinking cursor
            pygame.draw.line(
                screen,
                BLACK,
                (cursor_x, input_rect.y + 3),
                (cursor_x, input_rect.y + 20),
                1,
            )


class LLMGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("LLM Village Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)

        # Game objects
        self.player = Player(500, 350)
        self.dialogue = DialogueBox()
        self.game_state = GameState.EXPLORING
        self.conversation_history = {}
        self.current_npc = None
        self.ai_thinking = False

    def call_llm_async(self, prompt, npc_key):
        """Call LLM in a separate thread to avoid blocking"""

        def make_request():
            try:
                self.ai_thinking = True
                response = requests.post(
                    GameConfig.API_URL, json={"prompt": prompt}, timeout=30
                )
                response.raise_for_status()
                data = response.json()
                ai_response = data.get("response", "I'm not sure what to say...")

                # Update conversation history
                if npc_key not in self.conversation_history:
                    self.conversation_history[npc_key] = ""
                self.conversation_history[npc_key] += (
                    f"Player: {self.dialogue.player_input}\n{GameConfig.NPCS[npc_key]['name']}: {ai_response}\n"
                )

                # Update dialogue
                self.dialogue.set_npc_response(ai_response)
                self.ai_thinking = False
                self.game_state = GameState.TALKING

            except requests.RequestException as e:
                self.dialogue.set_npc_response(
                    f"Sorry, I can't respond right now. ({str(e)})"
                )
                self.ai_thinking = False
                self.game_state = GameState.TALKING

        thread = threading.Thread(target=make_request)
        thread.daemon = True
        thread.start()

    def build_npc_context(self, npc_key):
        """Build context for LLM based on game state"""
        npc = GameConfig.NPCS[npc_key]

        context = f"{GameConfig.WORLD_CONTEXT}\n\n"
        context += f"You are {npc['name']}, {npc['personality']}\n"
        context += f"Location: {npc['location']}\n"
        context += f"Player location: {self.player.current_location}\n"

        # Add conversation history if exists
        if npc_key in self.conversation_history:
            context += (
                f"Previous conversation: {self.conversation_history[npc_key][-300:]}\n"
            )

        context += "\nPlayer says: "
        return context

    def handle_npc_click(self, pos):
        """Check if player clicked on an NPC"""
        for npc_key, npc_data in GameConfig.NPCS.items():
            npc_x, npc_y = npc_data["pos"]
            distance = ((pos[0] - npc_x) ** 2 + (pos[1] - npc_y) ** 2) ** 0.5

            if distance < 20:  # NPC click radius
                # Check if player is close enough
                player_distance = (
                    (self.player.x - npc_x) ** 2 + (self.player.y - npc_y) ** 2
                ) ** 0.5
                if player_distance < 80:  # Talking distance
                    self.current_npc = npc_key
                    self.dialogue.start_conversation(npc_key)
                    self.game_state = GameState.TALKING
                    return True
                else:
                    # Show "too far" message briefly
                    pass
        return False

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            elif event.type == pygame.KEYDOWN:
                if (
                    event.key == pygame.K_ESCAPE
                    and self.game_state == GameState.TALKING
                ):
                    self.dialogue.active = False
                    self.game_state = GameState.EXPLORING

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.game_state == GameState.EXPLORING:
                    self.handle_npc_click(event.pos)

            # Handle dialogue input
            if self.game_state == GameState.TALKING:
                result = self.dialogue.handle_input(event)
                if result == "send_message" and not self.ai_thinking:
                    # Send message to LLM
                    context = self.build_npc_context(self.current_npc)
                    full_prompt = context + self.dialogue.player_input

                    self.game_state = GameState.WAITING_FOR_AI
                    self.call_llm_async(full_prompt, self.current_npc)

        return True

    def update(self):
        if self.game_state == GameState.EXPLORING:
            # Handle player movement
            keys = pygame.key.get_pressed()
            dx = dy = 0

            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                dx = -1
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                dx = 1
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                dy = -1
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                dy = 1

            if dx != 0 or dy != 0:
                self.player.move(dx, dy)

    def draw(self):
        self.screen.fill(DARK_GREEN)  # Background

        # Draw locations
        for loc_name, loc_data in GameConfig.LOCATIONS.items():
            pygame.draw.rect(self.screen, loc_data["color"], loc_data["rect"])
            pygame.draw.rect(self.screen, BLACK, loc_data["rect"], 2)

            # Draw location name
            text_surface = self.small_font.render(loc_data["name"], True, BLACK)
            text_rect = text_surface.get_rect(center=loc_data["rect"].center)
            self.screen.blit(text_surface, text_rect)

        # Draw NPCs
        for npc_key, npc_data in GameConfig.NPCS.items():
            x, y = npc_data["pos"]
            pygame.draw.circle(self.screen, npc_data["color"], (x, y), 15)
            pygame.draw.circle(self.screen, BLACK, (x, y), 15, 2)

            # Draw NPC name
            name_surface = self.small_font.render(npc_data["name"], True, BLACK)
            name_rect = name_surface.get_rect(center=(x, y - 25))
            self.screen.blit(name_surface, name_rect)

        # Draw player
        self.player.draw(self.screen)

        # Draw UI
        ui_rect = pygame.Rect(0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50)
        pygame.draw.rect(self.screen, LIGHT_GRAY, ui_rect)
        pygame.draw.rect(self.screen, BLACK, ui_rect, 2)

        # Draw location info
        location_text = f"Location: {self.player.current_location}"
        location_surface = self.font.render(location_text, True, BLACK)
        self.screen.blit(location_surface, (10, SCREEN_HEIGHT - 40))

        # Draw controls
        if self.game_state == GameState.EXPLORING:
            controls_text = "WASD: Move | Click NPCs to talk | ESC: Exit dialogue"
        elif self.game_state == GameState.TALKING:
            controls_text = "Type message and press ENTER | ESC: Stop talking"
        else:
            controls_text = "AI is thinking..."

        controls_surface = self.small_font.render(controls_text, True, BLACK)
        self.screen.blit(controls_surface, (10, SCREEN_HEIGHT - 20))

        # Draw dialogue box
        self.dialogue.draw(self.screen)

        # Draw AI thinking indicator
        if self.ai_thinking:
            thinking_surface = self.font.render("AI is thinking...", True, RED)
            self.screen.blit(thinking_surface, (SCREEN_WIDTH - 200, 10))

        pygame.display.flip()

    def run(self):
        print("Starting LLM Village Game!")
        print("Make sure your FastAPI server is running on http://127.0.0.1:8000")

        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = LLMGame()
    game.run()
