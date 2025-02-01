from discord.ext import commands, tasks

from source.command_service_handler.command_service import CommandService


class AutomationService:
    """
    Az automatizálásért felelős osztály.

    Ide tartozik majd:
    - YouTube API automatizálás
    - Napi ima automatizálás
    - :todo: Update értesítés automatizálás (ha lesz update)
    - :todo: XP automatizálás
    - :todo: polls automatizálás
    - :todo: giveaway automatizálás
    - :todo: pet automatizálás
    """

    def __init__(self, *, bot: commands.Bot) -> None:
        """

        :param bot: commands.Bot objektum - A bot objektum.
        """
        self.bot: commands.Bot = bot
        self.command_service: CommandService | None = None

    async def _initialize(self) -> None:
        await self.bot.wait_until_ready()
        self.command_service = CommandService(bot=self.bot, interaction=None)

    @tasks.loop(seconds=350)
    async def youtube_automatization(self) -> None:
        """
        A YouTube API automatizálásáért felelős metódus.
        :loop: 5 percenként fut le a stream állapotának lekérdezése.
        :return:
        """
        if not self.command_service:
            await self._initialize()

        try:
            await self.command_service.gogu()
        except Exception as e:
            print(e)

    @tasks.loop(seconds=5000)
    async def ima_automatization(self) -> None:
        """
        Napi ima automatizálásáért felelős metódus.

        :loop: 1 óránként fut le a napi ima lekérdezése.
        :return:
        """
        if not self.command_service:
            await self._initialize()

        try:
            await self.command_service.ima(nyelv=None)
        except Exception as e:
            print(e)
