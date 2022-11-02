from disnake.ext import commands
from disnake import ApplicationCommandInteraction


class GameCommands(commands.Cog):

    @commands.slash_command(description='Начать игру')
    async def start(self, interaction: ApplicationCommandInteraction):
        ...


def setup(bot):
    bot.add_cog(GameCommands)
