# Tombstone Plugin for Endstone

A simple and robust death chest plugin for Endstone (Minecraft Bedrock servers).

When a player dies, instead of dropping their items on the ground where they might despawn or get stolen, this plugin securely stores their entire inventory (including armor and off-hand items) in a virtual chest at their exact death location.

## Features
- Secure: Only the player who died can open or break their tombstone chest.
- Indestructible: Other players and admins cannot break the tombstone block.
- Auto-cleanup: Once the owner interacts with the chest to take their items, the chest automatically disappears.
- Coordinates: The player receives a private message with the exact X, Y, Z coordinates of their death.

## Virtual Tombstone System
Due to current Endstone API limitations (v0.11), the chest block itself does not contain the items. The items are securely stored in the server's memory.
- When you click on your tombstone, the items will instantly pop out and the chest will disappear.
- If the server restarts or stops normally, all active tombstones will safely drop their items on the ground so nothing is lost.

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
