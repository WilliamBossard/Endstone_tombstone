import json
import os
import time
from typing import Dict, List, Any

from endstone.plugin import Plugin
from endstone.block import Block
from endstone.inventory import ItemStack

class TombstoneManager:
    def __init__(self, plugin: Plugin):
        self.plugin = plugin
        self.data_dir = os.path.join(plugin.data_folder)
        self.data_file = os.path.join(self.data_dir, "tombs.json")
        self.config_file = os.path.join(self.data_dir, "config.json")
        self.config = {"expiration_seconds": 0, "give_death_compass": False}
        
        self.tombs: Dict[str, Dict[str, Any]] = {}
        
        self.load_config()
        self.load_data()

    def load_config(self):
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    data = json.load(f)
                    self.config.update(data)
            except Exception as e:
                self.plugin.logger.error(f"Failed to load config: {e}")
                
        with open(self.config_file, "w") as f:
            json.dump(self.config, f, indent=4)

    def load_data(self):
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r") as f:
                    raw_tombs = json.load(f)
                    self.tombs = {}
                    for k, v in raw_tombs.items():
                        if isinstance(v, str):
                            self.tombs[k] = {
                                "uuid": v,
                                "owner_name": "Unknown",
                                "xp": 0,
                                "creation_time": time.time(),
                                "items": []
                            }
                        else:
                            self.tombs[k] = v
            except Exception as e:
                self.plugin.logger.error(f"Failed to load tombs data: {e}")
                self.tombs = {}
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

    def add_tomb(self, block: Block, player_uuid: str, player_name: str, items: List[ItemStack], xp: int):
        key = self._get_key(block)
        serialized_items = []
        for item in items:
            serialized_items.append({
                "type": str(item.type),
                "amount": item.amount
            })
            
        self.tombs[key] = {
            "uuid": str(player_uuid),
            "owner_name": player_name,
            "items": serialized_items,
            "xp": xp,
            "creation_time": time.time()
        }
        self.save_data()

    def remove_tomb(self, block: Block):
        key = self._get_key(block)
        if key in self.tombs:
            del self.tombs[key]
            
        self.save_data()

    def is_tomb(self, block: Block) -> bool:
        return self._get_key(block) in self.tombs

    def get_tomb_owner(self, block: Block) -> str:
        tomb = self.tombs.get(self._get_key(block))
        return tomb.get("uuid") if tomb else None

    def get_tomb_data(self, block: Block) -> Dict[str, Any]:
        key = self._get_key(block)
        return self.tombs.get(key, {})

    def _get_key(self, block: Block) -> str:
        return f"{block.dimension.name}:{block.x}:{block.y}:{block.z}"

