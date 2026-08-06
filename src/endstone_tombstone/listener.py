from endstone.event import (
    event_handler,
    EventPriority,
    PlayerDeathEvent,
    BlockBreakEvent,
    PlayerInteractEvent,
)
from endstone.plugin import Plugin
from endstone.block import Block
import endstone

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
        block.type = "minecraft:chest"
        
        state = block.capture_state()
        if isinstance(state, endstone.block.Container):
            chest_inv = state.inventory
            
            for item in drops:
                if item and item.type != "minecraft:air":
                    chest_inv.add_item(item)
                    
            state.update(True)
            player_inv.clear() # Clear player inventory to try preventing drops
            self.manager.add_tomb(block, player.unique_id)
            
            x, y, z = int(location.x), int(location.y), int(location.z)
            player.send_message(f"§c[Tombstone]§7 You died! Your inventory has been secured in a chest at: §eX:{x} Y:{y} Z:{z}")
        else:
            self.plugin.logger.error("Failed to place a container at death location!")

    @event_handler(priority=EventPriority.HIGH)
    def on_block_break(self, event: BlockBreakEvent):
        block = event.block
        if self.manager.is_tomb(block):
            event.cancelled = True
            event.player.send_message("§c[Tombstone]§7 This tombstone chest is indestructible!")

    @event_handler(priority=EventPriority.HIGH)
    def on_player_interact(self, event: PlayerInteractEvent):
        block = event.block
        if not block:
            return
            
        if self.manager.is_tomb(block):
            owner_uuid = self.manager.get_tomb_owner(block)
            if str(event.player.unique_id) != owner_uuid:
                event.cancelled = True
                event.player.send_message("§c[Tombstone]§7 This tombstone chest does not belong to you!")
