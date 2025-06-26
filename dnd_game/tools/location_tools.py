import json
from typing import List, Optional
from .base import BaseTool
from dnd_game.game_engine import Location

# In a real application, you would have a way to manage the game state,
# such as a database or a simple in-memory dictionary.
# For this example, we'll use a simple dictionary to store locations.
GAME_STATE = {
    "locations": {}
}

class CreateOrUpdateLocationTool(BaseTool):
    """A tool to create a new location or update an existing one."""

    @property
    def name(self) -> str:
        return "CreateOrUpdateLocation"

    def get_briefing(self) -> str:
        return "Creates a new location or updates an existing one. Use this to define new places in the world or modify their descriptions."

    def get_required_parameters(self) -> str:
        return '''{
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "The unique name of the location."},
                "description": {"type": "string", "description": "A detailed description of the location."},
                "parent_name": {"type": "string", "description": "The name of the parent location, if any."}
            },
            "required": ["name", "description"]
        }'''

    def execute_with_parameters(self, parameters: dict) -> str:
        """Creates or updates a location and adds it to the game state."""
        name = parameters.get("name")
        description = parameters.get("description")
        parent_name = parameters.get("parent_name")
        parent = None
        if parent_name:
            if parent_name not in GAME_STATE["locations"]:
                return f"Error: Parent location '{parent_name}' not found."
            parent = GAME_STATE["locations"][parent_name]

        if name in GAME_STATE["locations"]:
            # Update existing location
            location = GAME_STATE["locations"][name]
            location.description = description
            if parent:
                parent.add_sub_location(location)
            return f"Successfully updated location: {name}."
        else:
            # Create new location
            try:
                location = Location(name=name, description=description, parent=parent)
                GAME_STATE["locations"][name] = location
                return f"Successfully created location: {name}."
            except ValueError as e:
                return f"Error: {e}"

class LinkLocationsTool(BaseTool):
    """A tool to link two locations together."""

    @property
    def name(self) -> str:
        return "LinkLocations"

    def get_briefing(self) -> str:
        return "Creates a relationship between two existing locations, for example, to indicate they are geographically close."

    def get_required_parameters(self) -> str:
        return '''{
            "type": "object",
            "properties": {
                "location1_name": {"type": "string", "description": "The name of the first location."},
                "location2_name": {"type": "string", "description": "The name of the second location."}
            },
            "required": ["location1_name", "location2_name"]
        }'''

    def execute_with_parameters(self, parameters: dict) -> str:
        """Links two locations in the game state."""
        location1_name = parameters.get("location1_name")
        location2_name = parameters.get("location2_name")
        if location1_name not in GAME_STATE["locations"]:
            return f"Error: Location '{location1_name}' not found."
        if location2_name not in GAME_STATE["locations"]:
            return f"Error: Location '{location2_name}' not found."

        location1 = GAME_STATE["locations"][location1_name]
        location2 = GAME_STATE["locations"][location2_name]

        location1.add_related_location(location2)
        location2.add_related_location(location1) # Assuming the relationship is mutual

        return f"Successfully linked {location1_name} and {location2_name}."