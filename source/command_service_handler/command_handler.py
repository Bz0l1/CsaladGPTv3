import discord
from discord import app_commands
from discord.ext import commands

from source.command_service_handler.command_service import CommandService
from source.file_service_handler.file_reader import get_token


class CommandHandler:
    def __init__(self, bot: commands.Bot) -> None:
        self._bot: commands.Bot = bot
        self.register_commands()

    def register_commands(self) -> None:
        @app_commands.command(name="ping", description="Ping parancs")
        async def ping(interaction: discord.Interaction) -> None:
            command_service: CommandService = CommandService(interaction=interaction)
            await command_service.ping()

        @app_commands.command(name="help", description="Parancsok listázása")
        async def help(interaction: discord.Interaction, command: str | None = None) -> None:
            command_service: CommandService = CommandService(interaction=interaction)
            await command_service.help(command=command)

        @app_commands.command(name="gogu", description="Étesítést küld ha Gogu streamel")
        async def gogu(interaction: discord.Interaction) -> None:
            cha_id: int = int(get_token("DISCORD_STREAM_CHANNEL_ID"))
            message: discord.Message = interaction.message
            channel_id: discord.TextChannel = self._bot.get_channel(cha_id)

            if interaction.channel.id == channel_id.id:
                command_service: CommandService = CommandService(interaction=interaction)

                await command_service.gogu()
            else:
                await interaction.response.send_message(
                    content=f"Ezt a parancsot csak a <#{cha_id}> szobában használhatod.\n"
                            "```/help gogu```", delete_after=10, ephemeral=True)

        @app_commands.command(name="ima", description="Bibliai idézetet mond")
        @app_commands.choices(nyelv=[
            app_commands.Choice(name="Magyar", value="hu"),
            app_commands.Choice(name="Angol", value="en"),
            app_commands.Choice(name="Japán", value="jp"),
            app_commands.Choice(name="Spanyol", value="es"),
        ])
        async def ima(interaction: discord.Interaction, *, nyelv: str | None = None) -> None:
            chat_id: int = int(get_token("DISCORD_IMA_CHANNEL_ID"))
            message: discord.Message = interaction.message
            channel_id: discord.TextChannel = self._bot.get_channel(chat_id)

            if interaction.channel_id == channel_id.id:
                command_service: CommandService = CommandService(interaction=interaction)
                await command_service.ima(nyelv=nyelv)
            else:
                await interaction.response.send_message(
                    content=f"Ezt a parancsot csak a <#{chat_id}> szobában használhatod.\n"
                            "```/help ima```", delete_after=10, ephemeral=True)
                return

        """
        @app_commands.command(name="insult", description="Sértést mond")
        async def insult(interaction: discord.Interaction, *,
                         mention: discord.Member | discord.Role | None = None) -> None:
            command_service: CommandService = CommandService(interaction)
            message: discord.Message = interaction.message

            if mention is None:
                await interaction.response.send_message(await command_service.insult(author=interaction.user))
            elif isinstance(mention, discord.Member):
                await interaction.response.send_message(
                    await command_service.insult(user=mention, author=interaction.user))
            elif isinstance(mention, discord.Role):
                await interaction.response.send_message(
                    await command_service.insult(role=mention, author=interaction.user))

        @app_commands.command(name="jimmy", description="Zámbó Jimmy idézetet mond")
        async def jimmy(interaction: discord.Interaction) -> None:
            command_service: CommandService = CommandService(interaction)
            await interaction.response.send_message(await command_service.jimmy())
        """

        @app_commands.command(name="percek", description="Kiírja a jelenlegi perceket")
        async def percek(interaction: discord.Interaction) -> None:
            command_service: CommandService = CommandService(interaction=interaction)
            await command_service.percek()

        """
        @app_commands.command(name="convert", description="Pénzt vagy percet vált át")
        async def convert(interaction: discord.Interaction, *, currency: str = "perc", amount: int = 1) -> None:
            command_service: CommandService = CommandService(interaction)
            message: discord.Message = interaction.message

            if currency in ("perc", "gulden"):
                if amount == "":
                    await interaction.response.send_message(content="Nem adtál meg mennyiséget.", delete_after=10,
                                                            ephemeral=True)
                    return
                if amount == "∞":
                    await interaction.response.send_message(content="Álmok Léteznek/"[::-1], ephemeral=True)
                    return

                try:
                    amount = int(amount)
                    if int(amount) <= 0:
                        await interaction.response.send_message(content="A szám nem lehet nulla vagy negatív.",
                                                                ephemeral=True, delete_after=10)
                        return

                    await interaction.response.send_message(
                        content=await command_service.convert(from_currency=currency, amount=int(amount)))
                except TypeError:
                    await interaction.response.send_message(content="Nem jól használtad a parancsot.\n"
                                                                    "```/help convert```", delete_after=10,
                                                            ephemeral=True)

            else:
                await interaction.response.send_message(content="Nem jól használtad a parancsot.\n"
                                                                "```/help convert```", delete_after=10, ephemeral=True)
        """

        @app_commands.command(name="setperc", description="Beállítja a percek számát")
        async def setperc(interaction: discord.Interaction, amount: str) -> None:
            command_service: CommandService = CommandService(interaction=interaction)
            message: discord.Message = interaction.message

            if amount == "":
                await interaction.response.send_message(content="Nem adtál meg mennyiséget.", delete_after=10,
                                                        ephemeral=True)
                return

            if amount == "∞":
                await interaction.response.send_message(content="Álmok Léteznek/"[::-1], ephemeral=True)
                return

            try:
                amount = int(amount)
                if int(amount) <= 0:
                    await interaction.response.send_message(content="A szám nem lehet nulla vagy negatív.",
                                                            ephemeral=True, delete_after=10)
                    return

            except ValueError:
                await interaction.response.send_message(content="Nem jól használtad a parancsot.\n"
                                                                "```/help setperc```", delete_after=10, ephemeral=True)
                return
            await command_service.setperc(amount=str(amount))

        @app_commands.command(name="javaslat", description="Javaslatot küld a bot vagy a szerver fejlesztésére")
        @app_commands.choices(javaslat=[
            app_commands.Choice(name="Bot fejlesztése", value="bot"),
            app_commands.Choice(name="Szerver fejlesztése", value="szerver"),
        ])
        async def javaslat(interaction: discord.Interaction, javaslat: str) -> None:
            command_service: CommandService = CommandService(interaction=interaction, bot=self._bot)
            await command_service.javaslat(theme=javaslat)

        """
        @app_commands.command(name="say", description="Egy megadott szerepben válaszol a bot",
                              extras={"model": "gpt3 vagy gpt4"})
        async def say(interaction: discord.Interaction, *, model: str | None = None, szerep: str, uzenet: str) -> None:
            command_service: CommandService = CommandService(interaction)
            message: discord.Message = interaction.message
            author_id: int = interaction.user.id
            # TODO: rank system for GPT4 and/or vision

            if model is None:
                gpt_response: str | bool = await command_service.say(role=szerep, prompt=uzenet)
            else:
                gpt_response: str | bool = await command_service.say(role=szerep, prompt=uzenet, model=model)

            if not gpt_response:
                await interaction.response.send_message(content="Nem található ilyen szerep.\n"
                                                                "```/help say```", delete_after=10, ephemeral=True)
                return

            await interaction.response.send_message(content=gpt_response)

        @app_commands.command(name="roles", description="Szerepek listázása")
        async def roles(interaction: discord.Interaction) -> None:
            command_service: CommandService = CommandService(interaction)
            await interaction.response.send_message(embed=await command_service.list_roles())

        @app_commands.command(name="newrole", description="Új szerepet hoz létre")
        async def newrole(interaction: discord.Interaction, name: str, description: str,
                          list_description: str | None = None) -> None:
            command_service: CommandService = CommandService(interaction)
            author_id: int = interaction.user.id
            create_response, is_created = await command_service.newrole(name=name, prompt=description,
                                                                        summary=list_description,
                                                                        user_id=str(author_id))

            if is_created:
                await interaction.response.send_message(content=create_response)
                return

            await interaction.response.send_message(content=create_response, ephemeral=True, delete_after=10)

        @app_commands.command(name="deleterole", description="Töröl egy szerepet")
        async def deleterole(interaction: discord.Interaction, role_name: str) -> None:
            command_service: CommandService = CommandService(interaction)
            author_id: int = interaction.user.id
            delete_response, is_deleted = await command_service.delete_role(name=role_name, user_id=str(author_id))

            if is_deleted:
                await interaction.response.send_message(content=delete_response)
                return

            await interaction.response.send_message(content=delete_response, ephemeral=True, delete_after=10)

        @app_commands.command(name="bejelentes", description="Bejelentést küld")
        async def bejelentes(interaction: discord.Interaction):

            class ReportModal(discord.ui.Modal):
                def __init__(self):
                    super().__init__(title="Bejelentés")
                    self.game_service: CommandService = CommandService(interaction)

                    self.title_input = discord.ui.TextInput(
                        label="Cím",
                        placeholder="Add meg a címet...",
                        required=True
                    )
                    self.add_item(self.title_input)

                    self.description_input = discord.ui.TextInput(
                        label="Leírás",
                        placeholder="Add meg a leírást...",
                        required=True,
                        style=discord.TextStyle.long
                    )
                    self.add_item(self.description_input)

                    self.author_input = discord.ui.TextInput(
                        label="Író",
                        placeholder="Ki írta...",
                        required=False
                    )
                    self.add_item(self.author_input)

                async def on_submit(self, interaction: discord.Interaction):
                    title = self.title_input.value
                    description = self.description_input.value
                    author = self.author_input.value

                    embed: discord.Embed = await self.game_service.bejelentes(title=title, description=description,
                                                                              author=author)
                    embed.set_author(name=author if author else "Anonim")

                    channel_id = int(get_token("NOTIFICATION_CHANNEL_ID"))
                    channel = interaction.client.get_channel(channel_id)
                    await channel.send(embed=embed)
                    await interaction.response.send_message("Bejelentés elküldve!", ephemeral=True, delete_after=5)

            view = ReportModal()
            await interaction.response.send_modal(view)

        @app_commands.command(name="xp", description="Megmondja mennyi xp-d van")
        async def xp(interaction: discord.Interaction) -> None:
            author: discord.Member = interaction.user
            command_service: CommandService = CommandService(interaction)
            await interaction.response.send_message(content=await command_service.get_xp(author), ephemeral=True)
            
        """

        discord_commands = [ping, help, gogu, ima, percek, setperc, javaslat]
        for command in discord_commands:
            self._bot.tree.add_command(command)
