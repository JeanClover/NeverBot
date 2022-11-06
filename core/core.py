from os import listdir, environ

from disnake.ext.commands import Bot
from jishaku.modules import find_extensions_in
from jishaku import Flags as JFlags


class NeverBot(Bot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.load_extension('jishaku')

        # change jishaku Flags
        JFlags.NO_UNDERSCORE = True
        JFlags.FORCE_PAGINATOR = True
        JFlags.NO_DM_TRACEBACK = True
        environ['JISHAKU_EMBEDDED_JSK'] = 'true'

        # load extensions
        for cog in find_extensions_in('cogs'):
                try:
                    self.load_extension('cogs.commands')
                except Exception as cog_error:
                    print(f'{cog}: {cog_error}')
                else:
                    print(f'{cog} loaded')

    async def on_ready(self):
        print(f'{self.user.name} is running')
