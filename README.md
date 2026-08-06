# Tombstone Plugin for Endstone

A simple and robust death chest plugin for Endstone (Minecraft Bedrock servers).

When a player dies, instead of dropping their items on the ground where they might despawn or get stolen, this plugin securely stores their entire inventory (including armor and off-hand items) as well as their Experience (XP) in a virtual chest at their exact death location.

## Features
- Secure: Only the player who died can open or break their tombstone chest.
- Indestructible: Other players and admins cannot break the tombstone block.
- Auto-cleanup: Once the owner interacts with the chest to take their items, the chest automatically disappears.
- XP Recovery: The player's exact amount of XP is saved in the tomb and fully restored upon collection.
- Configurable Expiration: Tombstones can optionally expire after a certain amount of time, allowing any player to loot them.
- Death Compass (Optional): Players can receive a special compass upon respawning with the exact coordinates of their death to help them find their tomb.

## Planned Features
- Floating Text (Hologram): A hologram above the tombstone indicating the owner's name and the remaining time before expiration (temporarily disabled due to an Endstone API crash).

## Virtual Tombstone System
Due to current Endstone API limitations (v0.11), the chest block itself does not contain the items. The items and XP are securely stored in the server's memory.
- When you click on your tombstone, the items will instantly drop at your feet, your XP will be restored, and the chest will disappear.
- If the server restarts or stops normally, all active tombstones will safely drop their items on the ground so nothing is lost.

## Configuration
When you run the plugin for the first time, a `config.json` file is generated in the plugin's data folder.
- `expiration_seconds`: The time in seconds before a tombstone loses its owner protection. (Set to `0` for infinite protection). Once expired, any player can click the chest to loot it!
- `give_death_compass`: Set to `true` to give the player a special compass pointing to their death coordinates when they respawn. The compass is automatically removed from their inventory when they recover their tomb.

## Installation & Requirements

### 1. Install the Plugin
Download the latest .whl release from Releases or EndGit.
Place the file in your server's plugins directory (or install it via pip install depending on your server panel like Pterodactyl).

### 2. CRITICAL: Enable KeepInventory (Required)
This plugin requires the keepinventory gamerule to be enabled on your server.

If keepinventory is false, the server will drop the items on the ground before the plugin can catch them.

To make the plugin work, you MUST type this command in your server console:
gamerule keepinventory true
(Or /gamerule keepinventory true in-game if you are an operator).

The plugin will automatically simulate the death penalty by taking the items from the player's inventory, saving them in the virtual tombstone, and clearing the player's inventory so they respawn with nothing.

## Compatibility
- Endstone API: v0.11+
- Python: 3.14+

## Credits
Created by William Bossard for the Endstone community.
