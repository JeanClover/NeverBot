from typing import Union

from disnake import Embed, Color, Guild
from disnake.ext import commands


class Events(commands.Cog):

    def __init__(self, bot: Union[commands.Bot, commands.AutoShardedBot]):
        self.bot = bot
        self.logs_channel_ids = {'guilds-log': 1039613327141257306}

    @commands.Cog.listener()
    async def on_guild_join(self, guild: Guild):
        channel = await self.bot.fetch_channel(self.logs_channel_ids['guilds-log'])
        embed = Embed(title=f'Бота добавили на сервер  `{guild.owner}`',
                    description=f'Общее количество серверов у бота: **{len(self.bot.guilds)}**',
                    color=Color.green())

        embed.set_author(name=str(guild.name), icon_url=guild.icon.url)
        embed.add_field(name='Количество участников сервера:', value=guild.member_count, inline=True)

        await channel.send(embed=embed)


def setup(bot):
    bot.add_cog(Events(bot))
