from __future__ import annotations
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from .character import Character

class GameState:
    """Manages the overall state of the game, including all characters."""
    def __init__(self):
        self.characters: List[Character] = []

    def add_character(self, character: Character):
        """Adds a character to the game state."""
        if character not in self.characters:
            self.characters.append(character)

    def get_player_character(self) -> Character | None:
        """Finds the player character."""
        for character in self.characters:
            if character.is_player:
                return character
        return None

    def get_character_by_name(self, name: str) -> Character | None:
        """Finds a character by name."""
        for character in self.characters:
            if character.name == name:
                return character
        return None