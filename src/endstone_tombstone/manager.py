import json
import os
from typing import Dict, List, Any

from endstone.plugin import Plugin
from endstone.block import Block
from endstone.inventory import ItemStack

class TombstoneManager:
    def __init__(self, plugin: Plugin):
        self.plugin = plugin
        self.data_dir = os.path.join(plugin.data_folder)
        self.data_file = os.path.join(self.data_dir, "tombs.json")
        self.tombs: Dict[str, str] = {}
        self.tomb_items: Dict[str, List[ItemStack]] = {}
        
        self.load_data()

    def load_data(self):
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r") as f:
                    self.tombs = json.load(f)
            except Exception as e:
                self.plugin.logger.error(f"Failed to load tombs data: {e}")
        else:
            self.tombs = {}

    def save_data(self):
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        try:
            with open(self.data_file, "w") as f:
                json.dump(self.tombs, f)
        except Exception as e:
            self.plugin.logger.error(f"Failed to save tombs data: {e}")

    def add_tomb(self, block: Block, player_uuid: str, items: List[ItemStack]):
        key = self._get_key(block)
        self.tombs[key] = str(player_uuid)
        self.tomb_items[key] = items
        self.save_data()

    def remove_tomb(self, block: Block):
        key = self._get_key(block)
        if key in self.tombs:
            del self.tombs[key]
        if key in self.tomb_items:
            del self.tomb_items[key]
        self.save_data()

    def is_tomb(self, block: Block) -> bool:
        return self._get_key(block) in self.tombs

    def get_tomb_owner(self, block: Block) -> str:
        return self.tombs.get(self._get_key(block))

    def get_tomb_items(self, block: Block) -> List[ItemStack]:
        key = self._get_key(block)
        return self.tomb_items.get(key, [])

    def _get_key(self, block: Block) -> str:
        return f"{block.dimension.name}:{block.x}:{block.y}:{block.z}"

    def drop_all_items(self):
        to_remove = []
        for key, items in self.tomb_items.items():
            try:
                dim_name, x_str, y_str, z_str = key.split(":")
                x, y, z = int(x_str), int(y_str), int(z_str)
                
                dimension = None
                for dim in self.plugin.server.levels[0].dimensions:
                    if dim.name == dim_name:
                        dimension = dim
                        break
                
                if not dimension:
                    continue
                
                block = dimension.get_block_at(x, y, z)
                for item in items:
                    dimension.drop_item(block.location, item)
                
                if block.type == "minecraft:chest":
                    block.set_type("minecraft:air")
                    
                to_remove.append(key)
            except Exception as e:
                self.plugin.logger.error(f"Failed to drop items for tomb {key}: {e}")
                
        for key in to_remove:
            if key in self.tombs:
                del self.tombs[key]
            if key in self.tomb_items:
                del self.tomb_items[key]
                
        self.save_data()
