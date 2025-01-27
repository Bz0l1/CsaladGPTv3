import discord
from discord.ext import commands

from file_service_handler.file_handler import get_token


class Bot(commands.Bot):
    def __init__(self, intents: discord.Intents) -> None:
        super().__init__(command_prefix='!', intents=intents, help_command=None)

    async def setup_hook(self) -> None:
        guild: discord.Object = discord.Object(id=int(get_token('DISCORD_TEST_GUILD_ID')))

        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)

    async def on_ready(self) -> None:
        print(f"{self.user} csatlakozott!")
        channel: discord.TextChannel = self.get_channel(int(get_token('DISCORD_TEST_MAIN_CHANNEL_ID')))
        await self.change_presence(activity=discord.Game(name="/help | z0l1"))
        await channel.send("Szia Család!")

if __name__ == '__main__':
    intents: discord.Intents = discord.Intents.default()
    intents.messages = True
    intents.guilds = True
    intents.reactions = True
    intents.members = True
    intents.message_content = True
    bot = Bot(intents)
    bot.run(get_token("DISCORD_TEST_TOKEN"))