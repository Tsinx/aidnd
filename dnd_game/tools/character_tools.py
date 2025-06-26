import json
from .base import BaseTool
from dnd_game.game_engine.game_state import GameState
from dnd_game.game_engine.item import Item, EquipSlot

class CreateCharacterTool(BaseTool):
    @property
    def name(self) -> str:
        return "create_character"

    def get_briefing(self) -> str:
        return "创建一个新的角色。"

    def get_required_parameters(self) -> str:
        return '''{
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "角色的名称"},
                "description": {"type": "string", "description": "角色的描述"},
                "background": {"type": "string", "description": "角色的背景故事"},
                "character_class": {"type": "string", "description": "角色的职业"},
                "race": {"type": "string", "description": "角色的种族"},
                "is_player": {"type": "boolean", "description": "是否为玩家角色"}
            },
            "required": ["name", "character_class", "race"]
        }'''

    def execute_with_parameters(self, parameters: dict, game_state: GameState):
        # Implementation for creating a character
        pass

class EditCharacterTool(BaseTool):
    @property
    def name(self) -> str:
        return "edit_character"

    def get_briefing(self) -> str:
        return "编辑现有角色的属性。"

    def get_required_parameters(self) -> str:
        return '''{
            "type": "object",
            "properties": {
                "character_name": {"type": "string", "description": "要编辑的角色名称"},
                "updates": {"type": "object", "description": "要更新的属性字典"}
            },
            "required": ["character_name", "updates"]
        }'''

    def execute_with_parameters(self, parameters: dict, game_state: GameState):
        # Implementation for editing a character
        pass

class AddToCharacterListAttributeTool(BaseTool):
    @property
    def name(self) -> str:
        return "add_to_character_list_attribute"

    def get_briefing(self) -> str:
        return "向角色的列表属性（如技能或物品）中添加项目。"

    def get_required_parameters(self) -> str:
        return '''{
            "type": "object",
            "properties": {
                "character_name": {"type": "string", "description": "角色名称"},
                "attribute": {"type": "string", "description": "要修改的列表属性名称"},
                "items": {"type": "array", "items": {"type": "string"}, "description": "要添加的项目列表"}
            },
            "required": ["character_name", "attribute", "items"]
        }'''

    def execute_with_parameters(self, parameters: dict, game_state: GameState):
        # Implementation for adding to a list attribute
        pass

class RemoveFromCharacterListAttributeTool(BaseTool):
    @property
    def name(self) -> str:
        return "remove_from_character_list_attribute"

    def get_briefing(self) -> str:
        return "从角色的列表属性中移除项目。"

    def get_required_parameters(self) -> str:
        return '''{
            "type": "object",
            "properties": {
                "character_name": {"type": "string", "description": "角色名称"},
                "attribute": {"type": "string", "description": "要修改的列表属性名称"},
                "items": {"type": "array", "items": {"type": "string"}, "description": "要移除的项目列表"}
            },
            "required": ["character_name", "attribute", "items"]
        }'''

    def execute_with_parameters(self, parameters: dict, game_state: GameState):
        # Implementation for removing from a list attribute
        pass

class CreateAndGiveItemTool(BaseTool):
    @property
    def name(self) -> str:
        return "create_and_give_item"

    def get_briefing(self) -> str:
        return "创建一个新物品并将其给予指定角色。"

    def get_required_parameters(self) -> str:
        return '''{
            "type": "object",
            "properties": {
                "character_name": {"type": "string", "description": "接收物品的角色名称"},
                "item_name": {"type": "string", "description": "物品的名称"},
                "item_description": {"type": "string", "description": "物品的描述"},
                "item_type": {"type": "string", "description": "物品类型"},
                "equip_slot": {"type": "string", "enum": [e.value for e in EquipSlot], "description": "物品的装备槽位"}
            },
            "required": ["character_name", "item_name", "item_type"]
        }'''

    def execute_with_parameters(self, parameters: dict, game_state: GameState):
        # Implementation for creating and giving an item
        pass

class EquipItemTool(BaseTool):
    @property
    def name(self) -> str:
        return "equip_item"

    def get_briefing(self) -> str:
        return "将角色物品栏中的物品装备到指定的槽位。"

    def get_required_parameters(self) -> str:
        return '''{
            "type": "object",
            "properties": {
                "character_name": {"type": "string", "description": "要装备物品的角色名称"},
                "item_name": {"type": "string", "description": "要装备的物品名称"},
                "slot": {"type": "string", "description": "要装备到的槽位"}
            },
            "required": ["character_name", "item_name", "slot"]
        }'''

    def execute_with_parameters(self, parameters: dict, game_state: GameState):
        character = game_state.get_character(parameters["character_name"])
        if not character:
            return f"错误：未找到名为 {parameters['character_name']} 的角色。"

        success = character.equip(parameters["item_name"], parameters["slot"])
        if success:
            return f"{parameters['character_name']} 成功装备了 {parameters['item_name']}。"
        else:
            return f"为 {parameters['character_name']} 装备 {parameters['item_name']} 失败。请检查物品是否存在或槽位是否可用。"