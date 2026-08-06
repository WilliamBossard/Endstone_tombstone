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
        
        self.tombs: Dict[str, str] = {}
        self.tomb_items: Dict[str, Dict[str, Any]] = {}
        self.holograms: Dict[str, Any] = {}
        
        self.load_config()
        self.load_data()
        
        self.plugin.server.scheduler.run_task(self.plugin, self.update_holograms, delay=20, period=20)

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

    def add_tomb(self, block: Block, player_uuid: str, player_name: str, items: List[ItemStack], xp: int):
        key = self._get_key(block)
        self.tombs[key] = str(player_uuid)
        self.tomb_items[key] = {
            "owner_name": player_name,
            "items": items,
            "xp": xp,
            "creation_time": time.time()
        }
        self.save_data()
        
        try:
            loc = block.location
            actor_loc = loc
            actor_loc.x += 0.5
            actor_loc.y += 1.0
            actor_loc.z += 0.5
            
            dimension = block.dimension
            actor = dimension.spawn_actor(actor_loc, "minecraft:armor_stand")
            actor.is_name_tag_always_visible = True
            actor.name_tag = f"§eTombe de {player_name}"
            self.holograms[key] = actor
            
            cmd = f"effect @e[type=armor_stand,x={int(loc.x)},y={int(loc.y)},z={int(loc.z)},r=2] invisibility 999999 0 true"
            self.plugin.server.dispatch_command(self.plugin.server.command_sender, cmd)
        except Exception as e:
            self.plugin.logger.error(f"Failed to spawn hologram: {e}")

    def remove_tomb(self, block: Block):
        key = self._get_key(block)
        if key in self.tombs:
            del self.tombs[key]
        if key in self.tomb_items:
            del self.tomb_items[key]
            
        if key in self.holograms:
            try:
                self.holograms[key].remove()
            except:
                pass
            del self.holograms[key]
            
        self.save_data()

    def is_tomb(self, block: Block) -> bool:
        return self._get_key(block) in self.tombs

    def get_tomb_owner(self, block: Block) -> str:
        return self.tombs.get(self._get_key(block))

    def get_tomb_data(self, block: Block) -> Dict[str, Any]:
        key = self._get_key(block)
        return self.tomb_items.get(key, {})

    def _get_key(self, block: Block) -> str:
        return f"{block.dimension.name}:{block.x}:{block.y}:{block.z}"

    def update_holograms(self):
        expiration_seconds = self.config.get("expiration_seconds", 0)
        
        for key, actor in list(self.holograms.items()):
            try:
                if not actor.is_valid:
                    continue
                    
                data = self.tomb_items.get(key)
                if not data:
                    continue
                    
                owner_name = data.get("owner_name", "Inconnu")
                creation_time = data.get("creation_time", 0)
                
                if expiration_seconds <= 0:
                    actor.name_tag = f"§eTombe de {owner_name}"
                    continue
                    
                elapsed = time.time() - creation_time
                remaining = expiration_seconds - elapsed
                
                if remaining <= 0:
                    actor.name_tag = f"§eTombe de {owner_name}\n§c§l[EXPIRE]"
                else:
                    mins = int(remaining // 60)
                    secs = int(remaining % 60)
                    actor.name_tag = f"§eTombe de {owner_name}\n§bExpire dans {mins}m {secs}s"
            except Exception:
                pass

    def drop_all_items(self):
        to_remove = []
        for key, data in self.tomb_items.items():
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
                for item in data.get("items", []):
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
                
        for key, actor in self.holograms.items():
            try:
                actor.remove()
            except:
                pass
        self.holograms.clear()
                
        self.save_data()
