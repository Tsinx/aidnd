from __future__ import annotations
from typing import Optional

from enum import Enum

class EquipSlot(Enum):
    HEAD = 'head'
    CHEST = 'chest'
    LEGS = 'legs'
    FEET = 'feet'
    HAND = 'hand'  # Can be equipped in main_hand or off_hand
    RING1 = 'ring1'
    RING2 = 'ring2'
    NECKLACE = 'necklace'
    PROJECTILE = 'projectile'

class Item:
    """Represents an item in the game, which can be an equipment or a consumable."""
    def __init__(self, name: str, description: str, equip_slot: Optional[EquipSlot] = None, is_two_handed: bool = False):
        self.name = name
        self.description = description
        self.equip_slot = equip_slot
        self.is_two_handed = is_two_handed