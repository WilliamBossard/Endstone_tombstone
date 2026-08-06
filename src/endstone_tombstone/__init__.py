from endstone.plugin import Plugin
from .listener import TombstoneListener
from .manager import TombstoneManager

class TombstonePlugin(Plugin):
    api_version = "0.11"
    prefix = "Tombstone"

    def __init__(self):
        super().__init__()
        self.manager = None

    def on_enable(self):
        self.logger.info("Enabling Tombstone Plugin...")
        self.manager = TombstoneManager(self)
        self.register_events(TombstoneListener(self, self.manager))
        self.logger.info("Tombstone Plugin enabled successfully!")

    def on_disable(self):
        self.logger.info("Disabling Tombstone Plugin...")
        if self.manager:
            self.manager.save_data()
        self.logger.info("Tombstone Plugin disabled!")
