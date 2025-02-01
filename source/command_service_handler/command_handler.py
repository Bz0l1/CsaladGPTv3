from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

from source.command_service_handler.command_service import CommandService
from source.file_service_handler.file_reader import LocalFileReader

### KONSTANSOK ###
FILE_READER: LocalFileReader = LocalFileReader()


##################

class CommandHandler:
    def __init__(self, *, bot: commands.Bot) -> None:
        self._bot: commands.Bot = bot
        self.register_commands()

    def register_commands(self) -> None:
        ##### RENDSZER PARANCSOK #####
        @app_commands.command(name="ping", description="Ping parancs")
        async def ping(interaction: discord.Interaction) -> None:
            """
            Ping parancs

            :param interaction: discord.Interaction - Az interakció objektum
            :return:
            """
            command_service: CommandService = CommandService(interaction=interaction)
            await command_service.ping()

        @app_commands.command(name="help", description="Parancsok listázása")
        @app_commands.choices(command=[
            app_commands.Choice(name="ping", value="ping"),
            app_commands.Choice(name="gogu", value="gogu"),
            app_commands.Choice(name="ima", value="ima"),
            app_commands.Choice(name="percek", value="percek"),
            app_commands.Choice(name="setperc", value="setperc"),
            app_commands.Choice(name="javaslat", value="javaslat"),

        ])
        async def help(interaction: discord.Interaction, *, command: Optional[str] = None) -> None:
            """
            Parancsok listázása

            :param interaction: discord.Interaction - Az interakció objektum
            :param command: str - A parancs neve (opcionális)
            :return:
            """
            command_service: CommandService = CommandService(interaction=interaction)
            await command_service.help(command=command)

        ############################

        ##### STREAM PARANCSOK #####
        @app_commands.command(name="gogu", description="Étesítést küld ha Gogu streamel")
        async def gogu(interaction: discord.Interaction) -> None:
            """
            Étesítést küld ha Gogu streamel

            :param interaction: discord.Interaction - Az interakció objektum
            :return:
            """
            cha_id: int = int(FILE_READER.get_token(token_name="DISCORD_TEST_STREAM_CHANNEL_ID"))
            channel_id: discord.TextChannel = self._bot.get_channel(cha_id)

            if interaction.channel.id == channel_id.id:
                command_service: CommandService = CommandService(interaction=interaction)

                await command_service.gogu()
            else:
                await interaction.response.send_message(
                    content=f"Ezt a parancsot csak a <#{cha_id}> szobában használhatod.\n"
                            "```/help gogu```", delete_after=10, ephemeral=True)

        ############################

        ##### IDÉZÉS PARANCSOK #####
        @app_commands.command(name="ima", description="Bibliai idézetet mond")
        async def ima(interaction: discord.Interaction, *, nyelv: Optional[str] = None) -> None:
            """
            Bibliai idézetet mond

            :param interaction: discord.Interaction - Az interakció objektum
            :param nyelv: str - A nyelv kódja (opcionális)
            :return:
            """
            chat_id: int = int(FILE_READER.get_token(token_name="DISCORD_TEST_IMA_CHANNEL_ID"))
            channel_id: discord.TextChannel = self._bot.get_channel(chat_id)

            if interaction.channel_id == channel_id.id:
                command_service: CommandService = CommandService(interaction=interaction)
                await command_service.ima(nyelv=nyelv)
            else:
                await interaction.response.send_message(
                    content=f"Ezt a parancsot csak a <#{chat_id}> szobában használhatod.\n"
                            "```/help ima```", delete_after=10, ephemeral=True)
                return

        @ima.autocomplete("nyelv")  # Ima parancs
        async def nyelv_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
            available_languages = [
                {"name": "Magyar", "value": "hu"},
                {"name": "Angol", "value": "en"},
                {"name": "Japán", "value": "jp"},
                {"name": "Spanyol", "value": "es"},
            ]
            return [
                app_commands.Choice(name=lang["name"], value=lang["value"])
                for lang in available_languages
                if current.lower() in lang["name"].lower()
            ]

        ############################

        ##### PERC PARANCSOK #####
        @app_commands.command(name="percek", description="Kiírja a jelenlegi perceket")
        async def percek(interaction: discord.Interaction) -> None:
            """
            Kiírja a jelenlegi perceket

            :param interaction: discord.Interaction - Az interakció objektum
            :return:
            """
            command_service: CommandService = CommandService(interaction=interaction)
            await command_service.percek()

        @app_commands.command(name="setperc", description="Beállítja a percek számát")
        async def setperc(interaction: discord.Interaction, *, amount: str) -> None:
            """
            Beállítja a percek számát

            :param interaction: discord.Interaction - Az interakció objektum
            :param amount: str - A percek száma
            :return:
            """
            command_service: CommandService = CommandService(interaction=interaction)

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

        ############################

        ##### ÉRTESÍTÉS PARANCSOK #####
        @app_commands.command(name="javaslat", description="Javaslatot küld a bot vagy a szerver fejlesztésére")
        @app_commands.choices(suggestion=[
            app_commands.Choice(name="Bot fejlesztése", value="bot"),
            app_commands.Choice(name="Szerver fejlesztése", value="szerver"),
        ])
        async def javaslat(interaction: discord.Interaction, *, suggestion: str) -> None:
            command_service: CommandService = CommandService(interaction=interaction, bot=self._bot)
            await command_service.javaslat(theme=suggestion)

        ##############################

        ##### SAY PARANCSOK #####
        @app_commands.command(name="say", description="CsaládGPT az AI segítségével válaszol neked")
        async def say(interaction: discord.Interaction, *, role: Optional[str] = None, message: str) -> None:
            await interaction.response.defer()
            command_service: CommandService = CommandService(interaction=interaction)
            await command_service.say(role=role, prompt=message, author=interaction.user)

        @app_commands.command(name="szerepek", description="Szerepek listázása")
        async def roles(interaction: discord.Interaction) -> None:
            pass

        @app_commands.command(name="új_szerep", description="Szerep hozzáadása")
        async def new_role(interaction: discord.Interaction, *, role: str) -> None:
            pass

        @app_commands.command(name="szerep_törlése", description="Szerep törlése")
        async def delete_role(interaction: discord.Interaction, *, role: str) -> None:
            pass

        @app_commands.command(name="szerep_módosítása", description="Szerep módosítása")
        async def modify_role(interaction: discord.Interaction, *, role: str) -> None:
            pass

        ############################
        discord_commands: list = [ping, help, gogu, ima, percek, setperc, javaslat, say]
        for command in discord_commands:
            self._bot.tree.add_command(command)
