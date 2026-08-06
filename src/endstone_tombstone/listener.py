from endstone.event import (
    event_handler,
    EventPriority,
    PlayerDeathEvent,
    BlockBreakEvent,
    PlayerInteractEvent,
)
from endstone.plugin import Plugin
from endstone.block import Block

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
                
        self.plugin.logger.info(f"[DEBUG] {player.name} died. Items found in inventory: {len(drops)}")
                
        if not drops:
            self.plugin.logger.info(f"[DEBUG] No items found for {player.name}. No tombstone created.")
            return
            
        location = player.location
        block = location.block
        block.set_type("minecraft:chest")
        
        player_inv.clear()
        self.manager.add_tomb(block, player.unique_id, drops)
        
        x, y, z = int(location.x), int(location.y), int(location.z)
        player.send_message(f"§c[Tombstone]§7 You died! Your inventory has been secured in a chest at: §eX:{x} Y:{y} Z:{z}")

    @event_handler(priority=EventPriority.HIGH)
    def on_block_break(self, event: BlockBreakEvent):
        block = event.block
        if self.manager.is_tomb(block):
            event.cancelled = True
            event.player.send_message("§c[Tombstone]§7 This tombstone chest is indestructible! Please interact with it to claim your items.")

    @event_handler(priority=EventPriority.HIGH)
    def on_player_interact(self, event: PlayerInteractEvent):
        block = event.block
        if not block:
            return
            
        if self.manager.is_tomb(block):
            event.cancelled = True
            owner_uuid = self.manager.get_tomb_owner(block)
            
            if str(event.player.unique_id) != owner_uuid:
                event.player.send_message("§c[Tombstone]§7 This tombstone chest does not belong to you!")
                return
                
            items = self.manager.get_tomb_items(block)
            dimension = block.dimension
            for item in items:
                dimension.drop_item(block.location, item)
                
            block.set_type("minecraft:air")
            self.manager.remove_tomb(block)
            event.player.send_message("§a[Tombstone]§7 You have recovered your items!")
