import time
import asyncio  # Add this import
import discord

import random
from discord import Message
from discord.ext import commands
from googleapiclient.channel import notification_from_headers

from file_service_handler.file_reader import get_token, read_txt
from command_service_handler.command_handler import CommandHandler
from command_service_handler.command_service import CommandService


class Bot(commands.Bot):
    def __init__(self, intents: discord.Intents) -> None:
        super().__init__(command_prefix='!', intents=intents, help_command=None)
        self.guild: discord.Object = discord.Object(id=int(get_token("DISCORD_GUILD_ID")))
        self.command_handler: CommandHandler | None = None

    async def setup_hook(self) -> None:
        self.command_handler = CommandHandler(bot=self)
        self.tree.copy_global_to(guild=self.guild)
        await self.tree.sync(guild=self.guild)

    async def on_ready(self) -> None:
        print(f"{self.user} csatlakozott!")
        channel: discord.TextChannel = self.get_channel(int(get_token("DISCORD_MAIN_CHANNEL_ID")))
        await self.change_presence(activity=discord.Game(name="/help | z0l1"))
        await channel.send("Szia Család!")
        # await self.update_notification()

        self.loop.create_task(self.youtube_automatization())
        self.loop.create_task(self.ima_automatization())

    async def on_interaction(self, interaction: discord.Interaction) -> None:
        pass

    async def on_message(self, message: discord.Message, /) -> None:
        await self.process_commands(message)

    async def youtube_automatization(self) -> None:
        command_service: CommandService = CommandService(bot=self)
        while True:
            await command_service.gogu()
            await asyncio.sleep(350)

    async def ima_automatization(self) -> None:
        commands_service: CommandService = CommandService(bot=self)
        while True:
            await commands_service.ima(nyelv=None)
            await asyncio.sleep(5000)

    async def update_notification(self) -> None:
        notification: str = read_txt("update")
        channel: discord.TextChannel = self.get_channel(int(get_token("DISCORD_BOT_CHANNEL_ID")))
        embed: discord.Embed = discord.Embed(title="**CsaládGPT UPDATE!!**", description=notification,
                                             color=discord.Color.green())
        await channel.send(embed=embed)


if __name__ == '__main__':
    intents: discord.Intents = discord.Intents.default()
    intents.messages = True
    intents.guilds = True
    intents.reactions = True
    intents.members = True
    intents.message_content = True
    bot = Bot(intents)
    bot.run(get_token("DISCORD_TOKEN"))
