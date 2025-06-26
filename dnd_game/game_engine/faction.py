from __future__ import annotations
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .location import Location
    from .character import Character

class Faction:
    """Represents a faction or organization in the game."""
    def __init__(self, name: str, description: str):
        self.name: str = name
        self.description: str = description
        self.members: List[Character] = []
        self.headquarters: Optional[Location] = None

    def add_member(self, character: Character):
        """Adds a character to the faction."""
        if character not in self.members:
            self.members.append(character)
            character.faction = self

    def __repr__(self) -> str:
        return f"Faction(name='{self.name}')"