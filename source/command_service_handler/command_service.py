import random
import time

import discord
from discord.ext import commands
from datetime import datetime

from typing_extensions import Optional

from source.submode_services_handler.youtube_api import LiveStreamStatus, check_channel_status
from source.submode_services_handler.quoting import BibleVerse
from source.submode_services_handler.ai_chat import AIChatAPIs
from source.file_service_handler.file_writer import LocalFileWriter
from source.file_service_handler.file_reader import LocalFileReader

######### KONSTANSOK #########
FILE_READER: LocalFileReader = LocalFileReader()
FILE_WRITER: LocalFileWriter = LocalFileWriter()


##############################


def create_embed(*, title: Optional[str] = None, description: Optional[str] = None, image_url: Optional[str] = None,
                 thumbnail_url: Optional[str] = None,
                 color: Optional[int] = 0x000000, timestamp: Optional[datetime] = None,
                 footer_text: Optional[str] = None) -> discord.Embed:
    embed: discord.Embed = discord.Embed(color=color)

    if title: embed.title = title
    if description: embed.description = description
    if image_url: embed.set_image(url=image_url)
    if thumbnail_url: embed.set_thumbnail(url=thumbnail_url)
    if timestamp: embed.timestamp = timestamp
    if footer_text: embed.set_footer(text=footer_text)
    return embed


class CommandService:
    def __init__(self, *, interaction: Optional[discord.Interaction] = None,
                 bot: Optional[commands.Bot] = None) -> None:
        self.interaction: Optional[discord.Interaction] = interaction  # amikor parancsot kap a bot
        self.bot_client: Optional[discord.Client] = (interaction.client if interaction is not None else None)
        self._commands_bot: Optional[commands.Bot] = bot  # amikor a bot valamelyik parancsot maga futtatja
        self.bot_for_automatization: Optional[commands.Bot] = bot  # amikor a bot automatikusan fut

    async def ping(self) -> None:
        start_time: float = time.time()
        color: int = random.randint(0, 0xFFFFFF)

        loading_embed: discord.Embed = create_embed(
            title="🏓 Számolás...",
            color=color
        )

        await self.interaction.response.send_message(embed=loading_embed)

        latency: int = round((time.time() - start_time) * 1000)
        api_latency: int = round(self.bot_client.latency * 1000)

        status_color: int = 0x44FF44 if api_latency < 100 else 0xFFD700 if api_latency < 300 else 0xFF0000

        messages: list[str] = [
            "Jobb, mint a NASA szerverei! 🚀",
            "A ping olyan gyors, mint a villám! ⚡"
        ]

        result_embed: discord.Embed = create_embed(
            title="📶 Bot Statisztikák",
            color=status_color,
            footer_text=random.choice(messages)
        )

        result_embed.add_field(name="**⌛ Válaszidő**", value=f"```{latency}ms```", inline=True)
        result_embed.add_field(name="**🌐 Websocket**", value=f"```{api_latency}ms```", inline=True)

        message: discord.Message = await self.interaction.original_response()
        await message.edit(embed=result_embed)

    async def help(self, *, command: str | None = None) -> discord.Embed | None:
        data: dict = FILE_READER.read_json(file_name="help")

        if command is None:
            commands_list: list[str] = []
            common_commands: list = data.get("common", {}).get("commands", [])

            for cmd in common_commands:
                command_entry = f"**{cmd['name']}** - {cmd['short_description']}\n"
                commands_list.append(command_entry)

            embed = create_embed(
                title="__Elérhető parancsok:__",
                description="".join(commands_list),
                color=0x630099,
                timestamp=datetime.now(),
                footer_text="Használd a `/help <parancs>` parancsot a részletes leírásért."
            )

        else:
            common_commands = data.get("common", {}).get("commands", [])
            command_data = None

            for cmd in common_commands:
                if cmd["name"].lower().strip("/") == command.lower().strip("/"):
                    command_data = cmd
                    break

            if command_data is None:
                return None

            embed = create_embed(
                title=f"__{command_data['name']}__",
                description=command_data['description'],
                color=0x630099,
                timestamp=datetime.now(),
                footer_text="Használd a `/help` parancsot a parancsok listázásához."
            )

        await self.interaction.response.send_message(embed=embed)

    async def gogu(self) -> None:
        is_command: bool = self.interaction is not None and self.bot_for_automatization is None
        url_object: LiveStreamStatus = check_channel_status(is_command=is_command)
        url: str | None = url_object.url
        is_live: bool = url is not None

        # Automatizálás esetén, ha a válasz a cache-ből származik, ne küldj értesítést.
        if self.bot_for_automatization is not None and url_object.cached:
            return

        if not is_live:
            title: str = "**NINCS STREAM**"
            description: str = "Sajnos Gogu még mindig távol van.\n||Lement tejért a dohányboltba.||"
            color: int = 0xf50000
            timestamp: datetime = datetime.now()
            footer_text: str = "STREAM"
            thumbnail_url: str = "https://cdn.discordapp.com/emojis/1151964870787481722.webp?size=96"
        else:
            title: str = "**STREAM VAN**"
            description: str = f"Megjött Fater\nGyere, csatlakozz:\n{url}"
            color: int = 0x00f510
            timestamp: datetime = datetime.now()
            footer_text: str = "STREAM"
            thumbnail_url: str = "https://cdn.discordapp.com/emojis/1151964914274013274.webp?size=160&quality=lossless"

        if self.interaction is not None:
            if is_live:
                await self.interaction.response.send_message(
                    content="@everyone",
                    embed=create_embed(
                        title=title,
                        description=description,
                        color=color,
                        timestamp=timestamp,
                        footer_text=footer_text,
                        thumbnail_url=thumbnail_url
                    )
                )
            else:
                await self.interaction.response.send_message(
                    embed=create_embed(
                        title=title,
                        description=description,
                        color=color,
                        timestamp=timestamp,
                        footer_text=footer_text,
                        thumbnail_url=thumbnail_url
                    )
                )
        elif self.bot_for_automatization is not None:
            if is_live:
                channel: discord.TextChannel = self.bot_for_automatization.get_channel(
                    int(FILE_READER.get_token(token_name="DISCORD_TEST_STREAM_CHANNEL_ID"))
                )
                await channel.send(content="@everyone")
                await channel.send(
                    embed=create_embed(
                        title=title,
                        description=description,
                        color=color,
                        timestamp=timestamp,
                        footer_text=footer_text,
                        thumbnail_url=thumbnail_url
                    )
                )
                await channel.send(content="https://tenor.com/view/alert-siren-warning-light-gif-15160785")

    async def ima(self, nyelv: str | None) -> None:
        is_command: bool = self.interaction is not None and self.bot_for_automatization is None
        biblia: BibleVerse = BibleVerse(lang=nyelv)

        if not is_command:
            date_from_file: str | datetime = FILE_READER.read_txt(file_name="ima_date_time")
            date_str = date_from_file.strip()
            date_from_file = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%f")

            if (datetime.now() - date_from_file).days < 1:
                return

        verse, lang = biblia.read_bible()

        title: str = "🙏 Ima 🙏" if is_command else "🙏 Napi Ima 🙏"
        description: str = verse
        color: int = random.randint(0, 0xFFFFFF)
        timestamp: datetime = datetime.now()
        footer_text: str = "Ámen 🙏" if lang == "hu" else "Amen 🙏" if lang in ("en", "es") else "アーメン 🙏"
        thumbnail_url: str = "https://cdn.discordapp.com/attachments/1205275317682442320/1239558620471885825/aacbe7e2c0844e43a3009cef9a89d899.jpg?ex=66435c6d&is=66420aed&hm=25d8ae669bd928cb45ed6268883217606c2c6e6ecce68815fe06d7b8a1b4bf2f&"

        if not is_command:
            FILE_WRITER.save_ima_date_time(time=timestamp.isoformat())
            channel: discord.TextChannel = self.bot_for_automatization.get_channel(
                int(FILE_READER.get_token(token_name="DISCORD_TEST_IMA_CHANNEL_ID")))
            await channel.send(
                embed=create_embed(title=title, description=description, color=color, timestamp=timestamp,
                                   footer_text=footer_text, thumbnail_url=thumbnail_url))
        else:
            await self.interaction.response.send_message(
                embed=create_embed(title=title, description=description, color=color, timestamp=timestamp,
                                   footer_text=footer_text, thumbnail_url=thumbnail_url))

    async def percek(self) -> None:
        data: str = FILE_READER.read_txt(file_name="percek")
        embed: discord.Embed = create_embed(title=f"{data} perc")

        to_day: int = int(data) // (24 * 60)
        to_hour: int = (int(data) // 60) % 24
        to_video: int = int(int(data) // (51 + (33 / 60)))

        embed.add_field(value=f"{to_day} nap", inline=True, name="")
        embed.add_field(value=f"{to_hour} óra", inline=True, name="")
        embed.add_field(value=f"{to_video} [Selchris videó](https://youtu.be/tdiGFvMFLMs?si=LUnAQ6N3DewteLzZ)",
                        inline=False, name="")
        await self.interaction.response.send_message(embed=embed)

    async def setperc(self, amount: str) -> None:
        FILE_WRITER.save_percek(time=amount)
        await self.interaction.response.send_message(
            embed=create_embed(title=f"A perc számláló módosítva: {amount} percre"))

    async def javaslat(self, *, theme: str) -> None:
        class JavaslatModal(discord.ui.Modal):
            javaslat: discord.ui.TextInput = discord.ui.TextInput(
                label='Javaslat',
                placeholder='Írd ide a javaslatod',
                style=discord.TextStyle.long,
                required=True
            )
            kuldo: discord.ui.TextInput = discord.ui.TextInput(
                label='Küldő',
                placeholder='Írd ide a neved (nem kötelező)',
                required=False
            )

            def __init__(self, bot_client: commands.Bot, is_forbot=None):
                super().__init__(title='Javaslat beküldése')
                self.bot_client = bot_client
                self.is_forbot = is_forbot

            async def on_submit(self, interaction: discord.Interaction):
                javaslat_szoveg = self.javaslat.value
                kudo_szoveg = self.kuldo.value or "Egy névtelen családtag"

                if self.is_forbot is None:
                    channel_id = int(FILE_READER.get_token(token_name="DISCORD_TEST_SUGGESTION_CHANNEL_ID"))
                    channel = self.bot_client.get_channel(channel_id)

                    if channel:
                        embed = create_embed(
                            title="Új javaslat érkezett!",
                            description=f"**Javaslat:** {javaslat_szoveg}\n\n**Küldő:** {kudo_szoveg}",
                            color=0x00FF00,
                            timestamp=datetime.now()
                        )
                        try:
                            await channel.send(embed=embed)
                            await interaction.response.send_message("Javaslat sikeresen elküldve!", ephemeral=True,
                                                                    delete_after=5)
                        except Exception as e:
                            await interaction.response.send_message(f"Hiba történt a javaslat elküldésekor: {e}",
                                                                    ephemeral=True, delete_after=5)
                    else:
                        await interaction.response.send_message("Nem találtam a javaslatok csatornáját.",
                                                                ephemeral=True, delete_after=5)
                else:
                    user = await self.bot_client.fetch_user(int(FILE_READER.get_token(token_name="DEV_USER_ID")))
                    if user:
                        embed = create_embed(
                            title="Új javaslat érkezett!",
                            description=f"**Javaslat:** {javaslat_szoveg}\n\n**Küldő:** {kudo_szoveg}",
                            color=0x00FF00,
                            timestamp=datetime.now()
                        )
                        try:
                            await user.send(embed=embed)
                            await interaction.response.send_message("Javaslat sikeresen elküldve!", ephemeral=True,
                                                                    delete_after=5)
                        except discord.Forbidden:
                            await interaction.response.send_message(
                                "Nem tudtam DM-et küldeni a fejlesztőnek. Lehet, hogy le van tiltva.", ephemeral=True,
                                delete_after=5)
                        except Exception as e:
                            await interaction.response.send_message(f"Hiba történt a DM küldésekor: {e}",
                                                                    ephemeral=True,
                                                                    delete_after=5)

        if theme == "bot":
            user_id = int(FILE_READER.get_token(token_name="DEV_USER_ID"))
            user = await self.bot_client.fetch_user(user_id)
            if user:
                try:
                    modal = JavaslatModal(self._commands_bot)
                    await modal.start(interaction=self.interaction)
                except discord.Forbidden:
                    await self.interaction.response.send_message(
                        "Nem tudtam DM-et küldeni a fejlesztőnek. Lehet, hogy le van tiltva.", ephemeral=True)
                except Exception as e:
                    await self.interaction.response.send_message(f"Hiba történt a DM küldésekor: {e}", ephemeral=True)
            else:
                await self.interaction.response.send_message("Nem találtam a fejlesztőt.", ephemeral=True)

        elif theme == "szerver":
            modal = JavaslatModal(self._commands_bot)
            await self.interaction.response.send_modal(modal)

    async def say(self, *, role: Optional[str], prompt: str, author: discord.Interaction.user, model: str) -> None:
        aichat: AIChatAPIs = AIChatAPIs()
        response: str = await aichat.text_response(prompt=prompt, role=role, model=model)
        await self.interaction.followup.send(response)

    async def roles(self, *, role: Optional[str] = None) -> None:
        data: dict = FILE_READER.read_json(file_name="roles")

        if role is None:
            role_author_list: list = [(role, details["author_id"]) for role, details in data.items()]

            title: str = "Elérhető szerepek"
            description: str = "\n".join(
                [f"{role} - Készítő: {self.bot_client.get_user(int(author)).display_name}" for role, author in
                 role_author_list])

            color: int = random.randint(0, 0xFFFFFF)
            timestamp: datetime = datetime.now()
            footer_text: str = (
                "Használd a ``/say`` parancsot a szerepek használatához.\n"
                "Használd a ``/szerepek <szerep>`` parancsot a szerep promptjának lekéréséhez.\n"
                "Használd a ``/új_szerep <szerep> <prompt>`` parancsot új szerep hozzáadásához.\n"
                "Használd a ``/szerep_törlése <szerep>`` parancsot szerep törléséhez.\n"
                "Használd a ``/szerep_módosítása <szerep>`` parancsot szerep módosításához."
            )

            embed: discord.Embed = create_embed(title=title, description=description, color=color, timestamp=timestamp,
                                                footer_text=footer_text)
        else:
            if role not in data:
                title: str = "Hiba"
                description: str = f"A '{role}' szerep nem található."
                color: int = random.randint(0, 0xFFFFFF)
                timestamp: datetime = datetime.now()
                footer_text: str = "Ellenőrizd az elérhető szerepeket a `/szerepek` parancs segítségével."
                embed: discord.Embed = create_embed(title=title, description=description, color=color,
                                                    timestamp=timestamp, footer_text=footer_text)
            else:
                title: str = role
                description: str = data[role]["prompt"]
                color: int = random.randint(0, 0xFFFFFF)
                timestamp: datetime = datetime.now()
                footer_text: str = "Használd a `/say` parancsot a szerep használatához."
                embed: discord.Embed = create_embed(title=title, description=description, color=color,
                                                    timestamp=timestamp, footer_text=footer_text)

        await self.interaction.response.send_message(embed=embed)

    async def new_role(self, *, role: str, author: discord.Interaction.user) -> None:
        class NewRoleModal(discord.ui.Modal):
            def __init__(self, *, bot_client: commands.Bot):
                super().__init__(title='Új szerep hozzáadása')
                self.bot_client = bot_client

                self.role_name_input = discord.ui.TextInput(
                    label='Szerep neve:',
                    default=role,
                    max_length=100,
                    style=discord.TextStyle.long,
                    required=True
                )
                self.prompt_input = discord.ui.TextInput(
                    label='Szerep:',
                    placeholder='Írd ide a szerep leírását',
                    style=discord.TextStyle.long,
                    required=True,
                    max_length=340
                )
                self.add_item(self.role_name_input)
                self.add_item(self.prompt_input)

            async def on_submit(self, interaction: discord.Interaction):
                role_name = self.role_name_input.value
                role_prompt = self.prompt_input.value

                data: dict = FILE_READER.read_json(file_name="roles")
                data[role_name] = {"name": role_name, "prompt": role_prompt, "author_id": str(interaction.user.id)}
                FILE_WRITER.save_json(filename="roles", data=data)

                await interaction.response.send_message(f"A '{role_name}' szerep sikeresen hozzáadva!", ephemeral=True)

        modal = NewRoleModal(bot_client=self._commands_bot)
        await self.interaction.response.send_modal(modal)

    async def delete_role(self, *, role: str) -> None:
        data: dict = FILE_READER.read_json(file_name="roles")

        if role in data:
            del data[role]
            FILE_WRITER.save_json(filename="roles", data=data)
            await self.interaction.response.send_message(f"A '{role}' szerep sikeresen törölve!", ephemeral=True)
        else:
            await self.interaction.response.send_message(f"A '{role}' szerep nem található.", ephemeral=True)