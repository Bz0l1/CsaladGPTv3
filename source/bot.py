import time
import asyncio  # Add this import
import discord
from discord import Message
from discord.ext import commands

from file_service_handler.file_reader import get_token
from command_service_handler.command_handler import CommandHandler
from command_service_handler.command_service import CommandService


class Bot(commands.Bot):
    def __init__(self, intents: discord.Intents) -> None:
        super().__init__(command_prefix='!', intents=intents, help_command=None)
        self.guild: discord.Object = discord.Object(id=int(get_token("DISCORD_TEST_GUILD_ID")))
        self.command_handler: CommandHandler | None = None

    async def setup_hook(self) -> None:
        self.command_handler = CommandHandler(bot=self)
        self.tree.copy_global_to(guild=self.guild)
        await self.tree.sync(guild=self.guild)

    async def on_ready(self) -> None:
        print(f"{self.user} csatlakozott!")
        channel: discord.TextChannel = self.get_channel(int(get_token("DISCORD_TEST_MAIN_CHANNEL_ID")))
        await self.change_presence(activity=discord.Game(name="/help | z0l1"))
        await channel.send("Szia Család!")

        await self.loop.create_task(self.youtube_automatization())

    async def on_interaction(self, interaction: discord.Interaction) -> None:
        pass

    async def on_message(self, message: discord.Message, /) -> None:
        await self.process_commands(message)

    async def youtube_automatization(self) -> None:
        command_service: CommandService = CommandService(bot=self)
        while True:
            await command_service.gogu()
            await asyncio.sleep(350)


if __name__ == '__main__':
    intents: discord.Intents = discord.Intents.default()
    intents.messages = True
    intents.guilds = True
    intents.reactions = True
    intents.members = True
    intents.message_content = True
    bot = Bot(intents)
    bot.run(get_token("DISCORD_TEST_TOKEN"))