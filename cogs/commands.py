import disnake.ui
from disnake.ext import commands
from disnake import Embed, Color, ApplicationCommandInteraction, MessageInteraction, ButtonStyle, Message

from core.db import random_question


class SelectModeButtons(disnake.ui.View):
    def __init__(self, author_id: int):
        super().__init__(timeout=10.0)
        self.author_id = author_id
        self.mode = None

    @disnake.ui.button(label='Обычные вопросы', style=ButtonStyle.secondary)
    async def general_questions_button(self, button: disnake.ui.Button, interaction: MessageInteraction):
        if interaction.author.id == self.author_id:
            await interaction.send('Вы выбрали **Обычные вопросы**')

            self.mode = False
            self.stop()
        else:
            await interaction.send('Категорию вопросов может выбрать только тот кто начал игру', ephemeral=True)

    @disnake.ui.button(label='Вопросы для взрослых (18+)', style=ButtonStyle.danger)
    async def nsfw_questions_button(self, button: disnake.ui.Button, interaction: MessageInteraction):
        if interaction.author.id == self.author_id:
            await interaction.send('Вы выбрали **NSFW вопросы (18+)**')

            self.nsfw = True
            self.stop()
        else:
            await interaction.send('Категорию вопросов может выбрать только тот кто начал игру', ephemeral=True)


class Game(disnake.ui.View):

    def __init__(self, question: str, channel, nsfw: bool = False):
        super().__init__(timeout=10.0)
        self.mode = nsfw
        self.channel = channel
        self.true_users = []
        self.false_users = []
        self.game_embed = Embed(title='Я никогда не...', description=question, color=Color.purple())

    async def on_timeout(self):
        self.clear_items()

        if len(self.true_users) == 0 and len(self.false_users) == 0:
            return self.stop()
        else:
            await self.next_game()
            return self.stop()

    async def next_game(self):
        question = await random_question(self.mode)
        next_game = Game(question['text'], self.mode)
        await self.channel.send(embed=next_game.game_embed, view=next_game)

    # Game buttons
    @disnake.ui.button(label='Правда', style=ButtonStyle.success)
    async def true_button(self, button: disnake.ui.Button, interaction: MessageInteraction):
        if interaction.author not in self.true_users and interaction.author not in self.false_users:
            self.true_users.append(interaction.author)

            await interaction.send('Ответ успешно зарегестрирован', ephemeral=True)

    @disnake.ui.button(label='Ложь', style=ButtonStyle.success)
    async def false_button(self, button: disnake.ui.Button, interaction: MessageInteraction):
        if interaction.author not in self.true_users and interaction.author not in self.false_users:
            self.false_users.append(interaction.author)
            
            await interaction.send('Ответ успешно зарегестрирован', ephemeral=True)


class GameCommands(commands.Cog):

    @commands.slash_command(description='Начать игру')
    async def start(self, interaction: ApplicationCommandInteraction):
        embed = Embed(title='Выберите категорию вопросов', color=Color.purple())
        mode_view = SelectModeButtons(interaction.author.id)

        select_message = await interaction.send(embed=embed, view=mode_view)
        await mode_view.wait()

        if mode_view.mode is None:
            return await select_message.delete()
        else:
            question = await random_question(mode_view.mode)
            game = Game(question['text'], interaction.channel, mode_view.mode)

            del mode_view

            await interaction.send(embed=game.game_embed, view=game)


def setup(bot):
    bot.add_cog(GameCommands(bot))
