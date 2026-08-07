import time
from endstone.event import (
    event_handler,
    EventPriority,
    PlayerDeathEvent,
    BlockBreakEvent,
    PlayerInteractEvent,
)
from endstone.plugin import Plugin
from endstone.block import Block
from endstone.inventory import ItemStack

class TombstoneListener:
    def __init__(self, plugin: Plugin, manager):
        self.plugin = plugin
        self.manager = manager

    @event_handler(priority=EventPriority.NORMAL)
    def on_player_death(self, event: PlayerDeathEvent):
        player = event.player
        player_inv = player.inventory
        drops = []
        for item in player_inv.contents:
            if item and item.type != "minecraft:air":
                drops.append(item)
                
        for equip in [player_inv.helmet, player_inv.chestplate, player_inv.leggings, player_inv.boots, player_inv.item_in_off_hand]:
            if equip and equip.type != "minecraft:air":
                drops.append(equip)
                
        if not drops:
            return
            
        xp = player.total_exp
        player.exp_level = 0
        player.exp_progress = 0.0
            
        location = player.location
        block = location.block
        block.set_type("minecraft:chest")
        
        player_inv.clear()
        self.manager.add_tomb(block, player.unique_id, player.name, drops, xp)
        
        x, y, z = int(location.x), int(location.y), int(location.z)
        player.send_message(f"§c[Tombstone]§7 You died! Your inventory and {xp} XP have been secured in a chest at: §eX:{x} Y:{y} Z:{z}")
        
        if self.manager.config.get("give_death_compass", False):
            try:
                compass = ItemStack("minecraft:recovery_compass")
            except:
                compass = ItemStack("minecraft:compass")
            meta = compass.item_meta
            meta.display_name = f"§5Tombstone Compass§r\n§eX:{x} Y:{y} Z:{z}"
            compass.set_item_meta(meta)
            player_inv.add_item(compass)

    @event_handler(priority=EventPriority.HIGH)
    def on_block_break(self, event: BlockBreakEvent):
        block = event.block
        if self.manager.is_tomb(block):
            event.is_cancelled = True
            event.player.send_message("§c[Tombstone]§7 This tombstone chest is indestructible! Please interact with it to claim the items.")

    @event_handler(priority=EventPriority.HIGH)
    def on_player_interact(self, event: PlayerInteractEvent):
        block = event.block
        if not block:
            return
            
        if self.manager.is_tomb(block):
            event.is_cancelled = True
            owner_uuid = self.manager.get_tomb_owner(block)
            tomb_data = self.manager.get_tomb_data(block)
            creation_time = tomb_data.get("creation_time", time.time())
            
            expiration_seconds = self.manager.config.get("expiration_seconds", 0)
            is_expired = False
            if expiration_seconds > 0 and (time.time() - creation_time) > expiration_seconds:
                is_expired = True
            
            if str(event.player.unique_id) != owner_uuid and not is_expired:
                event.player.send_message("§c[Tombstone]§7 This tombstone chest does not belong to you, and it has not expired yet!")
                return
                
            items = tomb_data.get("items", [])
            xp = tomb_data.get("xp", 0)
            
            dimension = block.dimension
            for item_data in items:
                if isinstance(item_data, dict):
                    try:
                        item = ItemStack(item_data["type"], item_data.get("amount", 1))
                    except:
                        continue
                else:
                    item = item_data
                dimension.drop_item(block.location, item)
                
            if xp > 0:
                event.player.give_exp(xp)
                
            if self.manager.config.get("give_death_compass", False):
                inv = event.player.inventory
                for i in range(inv.size):
                    item = inv.get_item(i)
                    if item and item.type != "minecraft:air" and (item.type == "minecraft:recovery_compass" or item.type == "minecraft:compass"):
                        if item.item_meta.has_display_name and "Tombstone" in item.item_meta.display_name:
                            inv.clear(i)
                
            block.set_type("minecraft:air")
            self.manager.remove_tomb(block)
            
            if str(event.player.unique_id) == owner_uuid:
                event.player.send_message("§a[Tombstone]§7 You have recovered your items and XP!")
            else:
                event.player.send_message("§a[Tombstone]§7 You looted an expired tombstone!")
