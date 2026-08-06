import json
import os
from typing import Dict, Any

from endstone.plugin import Plugin
from endstone.block import Block

class TombstoneManager:
    def __init__(self, plugin: Plugin):
        self.plugin = plugin
        self.data_dir = os.path.join(plugin.data_folder)
        self.data_file = os.path.join(self.data_dir, "tombs.json")
        self.tombs: Dict[str, str] = {}
        
        self.load_data()
        self.plugin.server.scheduler.run_task(self.plugin, self.check_empty_tombs, delay=20, period=20)

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

    def add_tomb(self, block: Block, player_uuid: str):
        key = self._get_key(block)
        self.tombs[key] = str(player_uuid)
        self.save_data()

    def remove_tomb(self, block: Block):
        key = self._get_key(block)
        if key in self.tombs:
            del self.tombs[key]
            self.save_data()

    def is_tomb(self, block: Block) -> bool:
        return self._get_key(block) in self.tombs

    def get_tomb_owner(self, block: Block) -> str:
        return self.tombs.get(self._get_key(block))

    def _get_key(self, block: Block) -> str:
        return f"{block.dimension.name}:{block.x}:{block.y}:{block.z}"

    def check_empty_tombs(self):
        to_remove = []
        for key in self.tombs.keys():
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
                if block.type != "minecraft:chest":
                    to_remove.append(key)
                    continue
                    
                import endstone
                state = block.capture_state()
                if isinstance(state, endstone.block.Container):
                    inv = state.inventory
                    is_empty = True
                    for i in range(inv.size):
                        item = inv.get_item(i)
                        if item is not None and item.type != "minecraft:air":
                            is_empty = False
                            break
                    
                    if is_empty:
                        block.set_type("minecraft:air")
                        to_remove.append(key)
            except Exception as e:
                self.plugin.logger.warning(f"Error checking tomb {key}: {e}")
                
        for key in to_remove:
            del self.tombs[key]
            
        if to_remove:
            self.save_data()
