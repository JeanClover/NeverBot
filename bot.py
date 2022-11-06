from os import getenv

from disnake.flags import Intents
from dotenv import load_dotenv

from core import NeverBot


bot = NeverBot(
    command_prefix='i!',
    owner_ids=[1035682590906130522],
    case_insensitive=True,
    strip_after_prefix=True,
    intents=Intents.all(),
    sync_commands=True,
    test_guilds=[1038384627808739328]
)


if __name__ == '__main__':
    load_dotenv()
    bot.run(getenv('token'))
