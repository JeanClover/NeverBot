from typing import Union

import disnake.ui
from disnake.ext import commands
from disnake import Embed, Color, ApplicationCommandInteraction, MessageInteraction, ButtonStyle

from core.db import random_question


class SelectModeButtons(disnake.ui.View):
    def __init__(self, author_id: int):
        super().__init__(timeout=30.0)
        self.author_id = author_id
        self.mode = None

    async def on_timeout(self):
        if self.mode is None:
            self.general_questions_button.disabled = True
            self.nsfw_questions_button.disabled = True
            self.stop()

    @disnake.ui.button(label='Обычные вопросы', style=ButtonStyle.secondary)
    async def general_questions_button(self, button: disnake.ui.Button, interaction: MessageInteraction):
        if interaction.author.id == self.author_id:
            self.general_questions_button.disabled = True
            self.nsfw_questions_button.disabled = True
            await interaction.send('Вы выбрали **Обычные вопросы**')

            self.mode = False
            self.stop()
        else:
            await interaction.send('Категорию вопросов может выбрать только тот кто начал игру', ephemeral=True)

    @disnake.ui.button(label='Вопросы для взрослых (18+)', style=ButtonStyle.danger)
    async def nsfw_questions_button(self, button: disnake.ui.Button, interaction: MessageInteraction):
        if interaction.author.id == self.author_id:
            self.general_questions_button.disabled = True
            self.nsfw_questions_button.disabled = True
            await interaction.send('Вы выбрали **NSFW вопросы (18+)**')

            self.mode = True
            self.stop()
        else:
            await interaction.send('Категорию вопросов может выбрать только тот кто начал игру', ephemeral=True)


class Game(disnake.ui.View):

    def __init__(self, bot: Union[commands.Bot, commands.AutoShardedBot], question: str, interaction, nsfw: bool = False):
        super().__init__(timeout=15.0)
        self.bot = bot
        self.mode = nsfw
        self.interaction = interaction
        self.true_users = []
        self.false_users = []
        self.game_embed = Embed(title='Я никогда не...', description=question, color=Color.purple())
        self.game_embed.set_thumbnail(url='attachment://assets/avatar_emoji.png')

    async def on_timeout(self) -> None:
        if len(self.true_users) == 0 and len(self.false_users) == 0:
            await self.interaction.send('**Никто из участников не нажал на кнопки в течении 15 секунд, поэтому игра была принудительно остановлена.**')
            return self.stop()
        else:
            next_view = disnake.ui.View(timeout=60.0)
            next_button = disnake.ui.Button(label='Продолжить игру', custom_id='next_button', style=ButtonStyle.green)
            stop_button = disnake.ui.Button(label='Стоп', custom_id='stop_button', style=ButtonStyle.danger)
            next_view.add_item(next_button)
            next_view.add_item(stop_button)

            users_embed = Embed(title='Ответы пользователей', color=Color.green())
            users_embed.add_field(name='Правда', value='\n'.join(self.true_users) or '**Нет пользователей которые выбрали этот ответ.**')
            users_embed.add_field(name='Ложь', value='\n'.join(self.false_users) or '**Нет пользователей которые выбрали этот ответ.**')

            next_button_message = await self.interaction.send(embed=users_embed, view=next_view)
            responce = await self.bot.wait_for('button_click', check=lambda inter: inter.component.custom_id == 'next_button' and inter.interaction_id == self.interaction.id)

            next_view.children[0].disabled = True

            await responce.reply(f'**{responce.author}** продолжил игру.')
            await next_button_message.edit(embed=users_embed, view=next_view)
            await self.next_game()
            return self.stop()

    async def next_game(self):
        question = await random_question(self.mode)
        next_game = Game(self.bot, question['text'], self.interaction, self.mode)
        await self.interaction.send(embed=next_game.game_embed, view=next_game)

    # Game buttons
    @disnake.ui.button(label='Правда', style=ButtonStyle.success)
    async def true_button(self, button: disnake.ui.Button, interaction: MessageInteraction):
        if str(interaction.author) not in self.true_users and (interaction.author) not in self.false_users:
            self.true_users.append(str(interaction.author))
            await interaction.send('Вы выбрали вариант ответа: **Правда**', ephemeral=True)
        else:
            await interaction.send('Вы не можете изменить свой вариант ответа.', ephemeral=True)

    @disnake.ui.button(label='Ложь', style=ButtonStyle.success)
    async def false_button(self, button: disnake.ui.Button, interaction: MessageInteraction):
        if str(interaction.author) not in self.true_users and (interaction.author) not in self.false_users:
            self.false_users.append(str(interaction.author))

            await interaction.send('Вы выбрали вариант ответа: **Ложь**', ephemeral=True)
        else:
            await interaction.send('Вы не можете изменить свой вариант ответа.', ephemeral=True)


class GameCommands(commands.Cog):

    @commands.slash_command(description='Начать игру')
    @commands.cooldown(1, 15, commands.BucketType.guild)
    async def start(self, interaction: ApplicationCommandInteraction):
        embed = Embed(title='Выберите категорию вопросов',
                        description='**Примечание:** Вы должны отвечать на вопросы в течении 15 секунд, в противном случае игра будет принудительно остановлена', 
                        color=Color.purple())
        embed.add_field(name='Ссылки:', value='• По вопросам и предложениям сюда -> **[Сервер поддержки](https://discord.gg/VbW78syZSa)** \
                                                \n• Оцените бота на мониторингах, это поможет в продвижении -> **[Список мониторингов](https://neverbot.ml/monitorings)**')

        mode_view = SelectModeButtons(interaction.author.id)

        await interaction.send(embed=embed, view=mode_view)
        await mode_view.wait()

        question = await random_question(mode_view.mode)
        game = Game(interaction.bot, question['text'], interaction, mode_view.mode)

        await interaction.send(embed=game.game_embed, view=game)
        await interaction.edit_original_message(embed=embed, view=mode_view)


def setup(bot):
    bot.add_cog(GameCommands(bot))
