from os import getenv

from disnake.flags import Intents
from dotenv import load_dotenv

from core import NeverBot


intents = Intents.default()
intents.guilds = True


bot = NeverBot(
    command_prefix='i!',
    owner_ids=[1035682590906130522],
    case_insensitive=True,
    strip_after_prefix=True,
    intents=intents,
    sync_commands=True
)


if __name__ == '__main__':
    load_dotenv()
    bot.run(getenv('token'))
