from SafoneAPI import SafoneAPI

from KNMusic.core.bot import KNBot
from KNMusic.core.dir import dirr
from KNMusic.core.git import git
from KNMusic.core.userbot import Userbot
from KNMusic.misc import dbb, heroku, sudo

from .logging import LOGGER

# Directories
dirr()

# Check Git Updates
git()

# Initialize Memory DB
dbb()

# Heroku APP
heroku()

# Load Sudo Users from DB
sudo()
api = SafoneAPI()
# Bot Client
app = KNBot()

# Assistant Client
userbot = Userbot()

from .platforms import *

YouTube = YouTubeAPI()
Carbon = CarbonAPI()
Spotify = SpotifyAPI()
Apple = AppleAPI()
Resso = RessoAPI()
SoundCloud = SoundAPI()
Telegram = TeleAPI()
HELPABLE = {}
