from .version import __version__
from .config_reader import JsonConfigReader
from .logger import Logger

try:
    from version import __version__ as bot_version
except:
    bot_version = "Not set"
