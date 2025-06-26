from __future__ import annotations
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    # These are forward references to prevent circular imports.
    # We assume 'Character' and 'Faction' classes will be defined elsewhere.
    from .character import Character
    from .faction import Faction

class Location:
    """
    Represents a location within the game world.

    Locations can be nested (e.g., a city within a province) but are protected
    against circular dependencies (e.g., two locations cannot contain each other).
    """
    def __init__(self, name: str, description: str, parent: Optional[Location] = None):
        self.name: str = name
        self.description: str = description
        self.parent: Optional[Location] = None
        self.sub_locations: List[Location] = []
        self.related_locations: List[Location] = []
        self.related_characters: List[Character] = []
        self.related_factions: List[Faction] = []

        if parent:
            parent.add_sub_location(self)

    def add_sub_location(self, location: Location):
        """
        Adds a sub-location to this location and sets its parent.

        This method prevents circular dependencies by checking if the new location
        is already an ancestor, which would create an infinite loop.
        """
        # A location cannot contain itself.
        if location is self:
            raise ValueError(f"A location cannot be a sub-location of itself: {self.name}")

        # Check for circular dependency: Is the location to be added an ancestor of the current one?
        current = self
        while current.parent:
            if current.parent == location:
                raise ValueError(f"Circular dependency detected: Cannot add '{location.name}' as a sub-location of '{self.name}'.")
            current = current.parent
        
        if location not in self.sub_locations:
            self.sub_locations.append(location)
            location.parent = self

    def add_related_location(self, location: Location):
        """Adds a related location, avoiding duplicates."""
        if location not in self.related_locations:
            self.related_locations.append(location)

    def add_character(self, character: Character):
        """Adds a character associated with this location, avoiding duplicates."""
        if character not in self.related_characters:
            self.related_characters.append(character)

    def add_faction(self, faction: Faction):
        """Adds a faction associated with this location, avoiding duplicates."""
        if faction not in self.related_factions:
            self.related_factions.append(faction)

    def __repr__(self) -> str:
        return f"Location(name='{self.name}')"