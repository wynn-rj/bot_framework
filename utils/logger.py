from utils import YAMLConfigReader

class _Logger():
    def __init__(self, bot, log_channel_file='/config/administration.yml'):
        self.bot = bot
        self.config = YAMLConfigReader(log_channel_file, defaults={
            'log_channels': []
        })

class Logger():
    _instance = None

    @staticmethod
    def initialize(bot):
        Logger._instance = _Logger(bot)

    @staticmethod
    async def log(msg):
        if not Logger._instance:
            return
        for channel_id in Logger._instance.config.data.log_channels:
            channel = Logger._instance.bot.get_channel(channel_id)
            if channel:
                await channel.send(msg)
        print(msg)

    @staticmethod
    def update_logging():
        if not Logger._instance:
            return
        Logger._instance.config.update()
