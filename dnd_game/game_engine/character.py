from __future__ import annotations

import json
from typing import List, Optional, Dict, TYPE_CHECKING

from dnd_game.game_engine.item import Item

if TYPE_CHECKING:
    from .location import Location
    from .faction import Faction

class Character:
    """Represents a character in the game, which can be a player or a non-player character (NPC)."""
    def __init__(self, name: str, description: str, background: str, character_class: str, level: int, max_hp: int, max_mp: int, strength: int, dexterity: int, stamina: int, intelligence: int, willpower: int, bloodline: int, is_player: bool = False, current_exp: int = 0, next_level_exp: int = 100):
        self.name: str = name
        self.description: str = description
        self.background: str = background
        self.character_class: str = character_class
        self.level: int = level
        self.current_exp: int = current_exp
        self.next_level_exp: int = next_level_exp
        self.max_hp: int = max_hp
        self.current_hp: int = max_hp
        self.max_mp: int = max_mp
        self.current_mp: int = max_mp
        self.strength: int = strength
        self.dexterity: int = dexterity
        self.stamina: int = stamina
        self.intelligence: int = intelligence
        self.willpower: int = willpower
        self.bloodline: int = bloodline
        self.base_ac: int = 10  # Base Armor Class
        self.buffs: List[str] = []
        self.debuffs: List[str] = []
        self.inventory: List[Item] = []
        self.is_player: bool = is_player
        self.equipment: Dict[str, Optional[Item]] = {
            'head': None,
            'chest': None,
            'legs': None,
            'feet': None,
            'main_hand': None,
            'off_hand': None,
            'ring1': None,
            'ring2': None,
            'necklace': None,
            'projectile': None
        }
        self.location: Optional[Location] = None
        self.faction: Optional[Faction] = None

    def equip(self, item: Item, slot: str = ''):
        """Equips an item from the inventory to the corresponding equipment slot."""
        if item not in self.inventory:
            print(f"Cannot equip {item.name}: not in inventory.")
            return

        if not item.equip_slot:
            print(f"Cannot equip {item.name}: not an equippable item.")
            return

        target_slot = ''
        if item.equip_slot.value == 'hand':
            if slot in ['main_hand', 'off_hand']:
                target_slot = slot
            else: # Default to main_hand if not specified or invalid
                target_slot = 'main_hand'
        else:
            target_slot = item.equip_slot.value

        if item.is_two_handed:
            if self.equipment.get('main_hand'):
                self.unequip('main_hand')
            if self.equipment.get('off_hand'):
                self.unequip('off_hand')
            self.equipment['main_hand'] = item
            self.equipment['off_hand'] = item # Mark both slots as occupied by the same item
        else:
            if self.equipment.get(target_slot):
                self.unequip(target_slot)
            self.equipment[target_slot] = item

        self.inventory.remove(item)
        print(f"{self.name} equipped {item.name} in {target_slot}.")

    @staticmethod
    def get_template() -> str:
        """Returns a JSON string representing the character's data structure."""
        template = {
            "name": "string",
            "description": "string",
            "background": "string",
            "character_class": "string",
            "level": "integer",
            "current_exp": "integer",
            "next_level_exp": "integer",
            "max_hp": "integer",
            "current_hp": "integer",
            "max_mp": "integer",
            "current_mp": "integer",
            "strength": "integer",
            "dexterity": "integer",
            "stamina": "integer",
            "intelligence": "integer",
            "willpower": "integer",
            "bloodline": "integer",
            "base_ac": "integer",
            "buffs": ["string"],
            "debuffs": ["string"],
            "inventory": [{"item_name": "string", "item_type": "string"}],
            "is_player": "boolean",
            "equipment": {
                "head": "string or null",
                "chest": "string or null",
                "legs": "string or null",
                "feet": "string or null",
                "main_hand": "string or null",
                "off_hand": "string or null",
                "ring1": "string or null",
                "ring2": "string or null",
                "necklace": "string or null",
                "projectile": "string or null"
            },
            "location": "string or null",
            "faction": "string or null"
        }
        return json.dumps(template, indent=2)

    def unequip(self, slot: str):
        """Unequips an item from a slot and moves it back to the inventory."""
        item_to_unequip = self.equipment.get(slot)
        if item_to_unequip:
            # If it's a two-handed weapon, clear both hand slots
            if item_to_unequip.is_two_handed:
                if self.equipment.get('main_hand') == item_to_unequip:
                    self.equipment['main_hand'] = None
                if self.equipment.get('off_hand') == item_to_unequip:
                    self.equipment['off_hand'] = None
            else:
                self.equipment[slot] = None

            if item_to_unequip not in self.inventory:
                 self.inventory.append(item_to_unequip)

            print(f"{self.name} unequipped {item_to_unequip.name}.")

    def __repr__(self) -> str:
        return f"Character(name='{self.name}')"