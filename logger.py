from bot_framework import JsonConfigReader

class _Logger():
    def __init__(self, bot):
        self.bot = bot
        self.config = JsonConfigReader('framework_data.json')

class Logger():
    _instance = None

    @staticmethod
    def initialize(bot):
        Logger._instance = _Logger(bot)

    @staticmethod
    async def log(msg):
        if not Logger._instance:
            return
        for channel_id in Logger._instance.config.log_channels:
            channel = Logger._instance.bot.get_channel(channel_id)
            await channel.send(msg)

    @staticmethod
    def update_logging():
        if not Logger._instance:
            return
        Logger._instance.config.update()
