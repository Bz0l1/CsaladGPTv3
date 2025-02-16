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
    """
    A parancsokat kezelő osztály.

    :argument bot: commands.Bot - A bot objektum.
    :argument _gpt_roles: dict - A GPT szerepek az adatbázisban.

    :function register_commands - A parancsok regisztrálása.
    """

    def __init__(self, *, bot: commands.Bot) -> None:
        self._bot: commands.Bot = bot
        self.register_commands()
        self._gpt_roles: dict = FILE_READER.read_json(file_name="roles")

    def register_commands(self) -> None:
        """
        A parancsok regisztrálása.

        :function: ping - Ping parancs.
        :function: help - Parancsok listázása. TODO: kiegészíteni
        :function: gogu - Étesítést küld ha Gogu streamel.
        :function: ima - Bibliai idézetet mond.
        :function: percek - Kiírja a jelenlegi perceket.
        :function: setperc - Beállítja a percek számát.
        :function: javaslat - Javaslatot küld a bot vagy a szerver fejlesztésére. TODO: DM
        :function: say - CsaládGPT az AI segítségével válaszol neked. TODO: Privát üzenet, DeepSeek
        :function: roles - Szerepek listázása.
        :function: new_role - Szerep hozzáadása.
        :function: delete_role - Szerep törlése.
        :function: modify_role - Szerep módosítása.
        :function: generate_image - Kép generátor. TODO: DALL-E, Flux

        :return:
        """

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
            cha_id: int = int(FILE_READER.get_token(token_name="DISCORD_STREAM_CHANNEL_ID"))
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
            chat_id: int = int(FILE_READER.get_token(token_name="DISCORD_IMA_CHANNEL_ID"))
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
        @app_commands.choices(model=[
            app_commands.Choice(name="gpt4o", value="gpt-4o-mini"),
            app_commands.Choice(name="gpt-o3", value="o3-mini"),
            app_commands.Choice(name="gemini 1.5 Flash", value="gemini-1.5-flash"),
        ])
        async def say(interaction: discord.Interaction, *, model: str = "gpt-4o-mini",
                      role: Optional[str] = None, message: str) -> None:
            """
            CsaládGPT az AI segítségével válaszol

            :param interaction:
            :param model:
            :param role:
            :param message:
            :return:
            """
            await interaction.response.defer()
            command_service: CommandService = CommandService(interaction=interaction)
            await command_service.say(role=role, prompt=message, author=interaction.user, model=model)

        @say.autocomplete("role")  # say parancs
        async def role_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
            roles_data = FILE_READER.read_json(file_name="roles")
            roles = [
                role.get("name", "ismeretlen szerep")
                for role in roles_data.values()
            ]
            return [
                app_commands.Choice(name=role, value=role)
                for role in roles
                if current.lower() in role.lower()
            ]

        @app_commands.command(name="szerepek", description="Szerepek listázása")
        async def roles(interaction: discord.Interaction, *, szerep: Optional[str] = None) -> None:
            """
            Szerepek listázása

            :param szerep: str - A szerep neve (opcionális)
            :param interaction: discord.Interaction - Az interakció objektum
            :return:
            """
            command_service: CommandService = CommandService(interaction=interaction)
            await command_service.roles(role=szerep)

        @roles.autocomplete("szerep")
        async def role_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
            roles_data = FILE_READER.read_json(file_name="roles")
            roles = [
                role.get("name", "ismeretlen szerep")
                for role in roles_data.values()
            ]
            return [
                app_commands.Choice(name=role, value=role)
                for role in roles
                if current.lower() in role.lower()
            ]

        @app_commands.command(name="új_szerep", description="Szerep hozzáadása")
        async def new_role(interaction: discord.Interaction, *, role: str) -> None:
            """
            Szerep hozzáadása

            :param interaction: discord.Interaction - Az interakció objektum
            :param role: str - A szerep neve
            :return:
            """
            roles: dict = FILE_READER.read_json(file_name="roles")

            if role in roles:
                await interaction.response.send_message(content="Ez a szerep már létezik.", ephemeral=True,
                                                        delete_after=10)
                return

            command_service: CommandService = CommandService(interaction=interaction)
            await command_service.new_role(role=role, author=interaction.user)
            self._gpt_roles = FILE_READER.read_json(file_name="roles")

        @app_commands.command(name="szerep_törlése", description="Szerep törlése")
        async def delete_role(interaction: discord.Interaction, *, role: str) -> None:
            """
            Szerep törlése

            :param interaction: discord.Interaction - Az interakció objektum
            :param role: str - A szerep neve
            :return:
            """
            roles: dict = FILE_READER.read_json(file_name="roles")
            author_id: int = interaction.user.id

            if role not in roles:
                await interaction.response.send_message(content="Ez a szerep nem létezik.", ephemeral=True,
                                                        delete_after=10)
                return

            if roles[role]["author_id"] != str(author_id):
                await interaction.response.send_message(content="Nincs jogod törölni ezt a szerepet.", ephemeral=True,
                                                        delete_after=10)
                return

            command_service: CommandService = CommandService(interaction=interaction)
            await command_service.delete_role(role=role)

        @delete_role.autocomplete("role")
        async def role_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
            roles_data = FILE_READER.read_json(file_name="roles")
            user_id = str(interaction.user.id)
            roles = [
                role.get("name", "ismeretlen szerep")
                for role in roles_data.values()
                if role.get("author_id") == user_id
            ]

            return [
                app_commands.Choice(name=role, value=role)
                for role in roles
                if current.lower() in role.lower()
            ]

        @app_commands.command(name="szerep_módosítása", description="Szerep módosítása")
        async def modify_role(interaction: discord.Interaction, *, role: str) -> None:
            """
            Szerep módosítása

            :param interaction: discord.Interaction - Az interakció objektum
            :param role: str - A szerep neve
            :return:
            """
            roles: dict = FILE_READER.read_json(file_name="roles")
            author_id: int = interaction.user.id

            if role not in roles:
                await interaction.response.send_message(content="Ez a szerep nem létezik.", ephemeral=True,
                                                        delete_after=10)
                return

            if roles[role]["author_id"] != str(author_id):
                await interaction.response.send_message(content="Nincs jogod módosítani ezt a szerepet.",
                                                        ephemeral=True,
                                                        delete_after=10)
                return

            command_service: CommandService = CommandService(interaction=interaction)
            await command_service.modify_role(role=role)

        @modify_role.autocomplete("role")
        async def role_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
            roles_data = FILE_READER.read_json(file_name="roles")
            user_id = str(interaction.user.id)
            roles = [
                role.get("name", "ismeretlen szerep")
                for role in roles_data.values()
                if role.get("author_id") == user_id
            ]

            return [
                app_commands.Choice(name=role, value=role)
                for role in roles
                if current.lower() in role.lower()
            ]

        ##### IMAGE GENERATOR #####
        @app_commands.command(name="meme", description="Mém generátor")
        async def meme(interaction: discord.Interaction, *, text: str) -> None:
            """
            Mém generátor
            TODO - Mém generátor

            :param interaction: discord.Interaction - Az interakció objektum
            :param text: TODO - kitalálni, API keresés
            :return:
            """
            pass

        @app_commands.command(name="kép_generálás", description="Kép generátor")
        @app_commands.choices(model=[
            app_commands.Choice(name="imagen3 (Gemini)", value="imagen"),
            app_commands.Choice(name="DALL-E (OpenAI) (NEM ELÉRHETŐ)", value="imagen"),
        ])
        async def generate_image(interaction: discord.Interaction, *, prompt: str,
                                 model: Optional[str] = "imagen") -> None:
            """
            Kép generátor

            :param interaction: discord.Interaction - Az interakció objektum
            :param prompt: str - A kép generálásához szükséges szöveg
            :param model: str - A modell neve (opcionális) TODO: DALL-E, Flux
            :return:
            """

            cha_id: int = int(FILE_READER.get_token(token_name="DISCORD_IMAGEN_CHANNEL_ID"))
            channel_id: discord.TextChannel = self._bot.get_channel(cha_id)

            if interaction.channel.id == channel_id.id:
                command_service: CommandService = CommandService(interaction=interaction)
                await command_service.generate_image(prompt=prompt, model=model)
            else:
                await interaction.response.send_message(
                    content=f"Ezt a parancsot csak a <#{cha_id}> szobában használhatod.\n"
                            "```/help kép_generálás```", delete_after=10, ephemeral=True)
                return

        ############################
        ############################
        discord_commands: list = [ping, help, gogu, ima, percek, setperc, javaslat, say, roles, new_role, delete_role,
                                  modify_role, generate_image]
        for command in discord_commands:
            self._bot.tree.add_command(command)
