import discord

from discord.ext import commands

from automation_service_handler.automation import AutomationService
from file_service_handler.file_reader import LocalFileReader
from command_service_handler.command_handler import CommandHandler


from datetime import timedelta

######### KONSTANSOK #########
FILE_READER: LocalFileReader = LocalFileReader()


##############################

class Bot(commands.Bot):
    def __init__(self, *, intents: discord.Intents) -> None:
        super().__init__(
            command_prefix='!',
            intents=intents,
            help_command=None,
        )
        self._configure_environment()
        self.command_handler: CommandHandler = CommandHandler(bot=self)
        self.automation: AutomationService = AutomationService(bot=self)

    def _configure_environment(self) -> None:
        """
        A környezeti változók beállításáért felelős metódus.

        :return:
        """
        self.guild: discord.Object = discord.Object(id=int(FILE_READER.get_token(token_name="DISCORD_GUILD_ID")))
        self.main_channel_id: int = int(FILE_READER.get_token(token_name="DISCORD_MAIN_CHANNEL_ID"))
        self.bot_channel_id: int = int(FILE_READER.get_token(token_name="DISCORD_BOT_CHANNEL_ID"))

    async def _sync_commands(self) -> None:
        """
        A parancsok szinkronizálásáért felelős metódus.

        :return:
        """
        self.tree.copy_global_to(guild=self.guild)
        await self.tree.sync(guild=self.guild)

    async def _start_automations(self) -> None:
        """
        Az automatizációk indításáért felelős metódus.

        :return:
        """
        self.automation.youtube_automatization.start()
        self.automation.ima_automatization.start()

    async def setup_hook(self) -> None:
        await self._sync_commands()
        await self._start_automations()

    async def on_ready(self) -> None:
        print(f"{self.user} csatlakozott!")
        await self.change_presence(activity=discord.Game(name="/help | z0l1"))
        channel = self.get_channel(self.main_channel_id)
        await channel.send("Szia Család!")
        await self.update_notification()

    async def on_interaction(self, interaction: discord.Interaction) -> None:
        """
        Az interakciókra való reagálásért felelős metódus.

        :param interaction: discord.Interaction objektum - Az interakció, amire a bot reagál.
        :return:
        :note: Az interakciókra való reagálás még nincs implementálva még.
        :todo: tervezés alatt
        """
        pass

    async def on_message(self, message: discord.Message, /) -> None:
        """
        Az üzenetekre való reagálásért felelős metódus.

        :param message: discord.Message objektum - Az üzenet, amire a bot reagál.
        :return:
        :todo: az XP rendszer implementálása valahol itt...
        """
        await self.process_commands(message)
        print(f"{message.author}: {message.content}")

    async def update_notification(self) -> None:
        """
        Update értesítéséért felelős metódus.

        :return:
        """
        notification: str = FILE_READER.read_txt(file_name="update")
        channel: discord.TextChannel = self.get_channel(self.bot_channel_id)
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
    bot = Bot(intents=intents)
    bot.run(FILE_READER.get_token(token_name="DISCORD_TOKEN"))
