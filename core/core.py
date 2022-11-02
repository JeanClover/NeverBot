from os import listdir, environ

from disnake.ext.commands import Bot
from jishaku.modules import find_extensions_in
from jishaku import Flags as JFlags


class INeverBot(Bot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.load_extension('jishaku')

        # change jishaku Flags
        JFlags.NO_UNDERSCORE = True
        JFlags.FORCE_PAGINATOR = True
        JFlags.NO_DM_TRACEBACK = True
        environ['JISHAKU_EMBEDDED_JSK'] = 'true'

        # load extensions
        for folder in listdir('cogs'):
            for cog in find_extensions_in(f'cogs/{folder}'):
                    try:
                        self.load_extension(cog)
                    except Exception as cog_error:
                        print(f'{cog}: {cog_error}')

    async def on_ready(self):
        print(f'{self.user.name} is running')
