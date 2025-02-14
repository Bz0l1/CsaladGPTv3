import random
import time
import asyncio
import uuid
from pathlib import Path

import discord
from discord.ext import commands
from datetime import datetime

from typing_extensions import Optional

from source.file_service_handler.file_reader import LocalFileReader
from source.file_service_handler.file_writer import LocalFileWriter
from source.submode_services_handler.image_gen import ImagenAPIs
from source.submode_services_handler.ai_chat import AIChatAPIs
from source.submode_services_handler.youtube_api import LiveStreamStatus, check_channel_status
from source.submode_services_handler.quoting import BibleVerse

### KONSTANSOK ###
FILE_READER: LocalFileReader = LocalFileReader()
FILE_WRITER: LocalFileWriter = LocalFileWriter()


#################

def create_embed(*, title: Optional[str] = None, description: Optional[str] = None, image_url: Optional[str] = None,
                 thumbnail_url: Optional[str] = None,
                 color: Optional[int] = 0x000000, timestamp: Optional[datetime] = None,
                 footer_text: Optional[str] = None) -> discord.Embed:
    """
    Discord embed készítése.

    :param title: str - cím
    :param description: str - leírás
    :param image_url: str - kép URL
    :param thumbnail_url: str - thumbnail URL
    :param color: int - szín
    :param timestamp: datetime - időbélyeg
    :param footer_text: str - footer szöveg
    :return: discord.Embed - a generált embed
    """
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
        """
        A parancskezelő kódja

        :param interaction: discord.Interaction - az interakció (ha a user parancsot ad)
        :param bot: commands.Bot - a bot (ha a bot maga futtatja a parancsot)

        :argument interaction: Optional[discord.Interaction] - amikor parancsot kap a bot
        :argument bot: Optional[commands.Bot] - amikor a bot valamelyik parancsot maga futtatja
        :argument bot_for_automatization: Optional[commands.Bot] - amikor a bot automatikusan fut

        :function: ping - A bot válaszidejének mérése.
        :function: help - Segítség a parancsokhoz.
        :function: gogu - Gogu streamjének ellenőrzése.
        :function: ima - Napi ima.
        :function: percek - Percek a következő videóig.
        :function: setperc - Percek beállítása.
        :function: javaslat - Javaslatok.
        :function: say - Szöveggenerálás.
        :function: roles - Szerepek.
        :function: new_role - Új szerep hozzáadása.
        :function: delete_role - Szerep törlése.
        :function: modify_role - Szerep módosítása.
        :function: generate_image - Kép generálása.
        """
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
                kuldo_szoveg = self.kuldo.value or "Egy névtelen családtag"

                if self.is_forbot is None:
                    channel_id = int(FILE_READER.get_token(token_name="DISCORD_TEST_SUGGESTION_CHANNEL_ID"))
                    channel = self.bot_client.get_channel(channel_id)

                    if channel:
                        embed = create_embed(
                            title="Új javaslat érkezett!",
                            description=f"**Javaslat:** {javaslat_szoveg}\n\n**Küldő:** {kuldo_szoveg}",
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
                            description=f"**Javaslat:** {javaslat_szoveg}\n\n**Küldő:** {kuldo_szoveg}",
                            color=0x00FF00,
                            timestamp=datetime.now()
                        )
                        try:
                            await user.send(embed=embed)
                            await interaction.response.send_message("Javaslat sikeresen elküldve!", ephemeral=True,
                                                                    delete_after=5)
                            FILE_WRITER.save_json(filename="javaslat",
                                                  data={"javaslat": javaslat_szoveg, "kuldo": kuldo_szoveg})


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
                    await self.interaction.response.send_modal(modal)
                except Exception as e:
                    await self.interaction.response.send_message(
                        f"Hiba történt a DM küldésekor: {e}", ephemeral=True)
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

    async def modify_role(self, *, role: str) -> None:
        data: dict = FILE_READER.read_json(file_name="roles")

        class ModifyRoleModal(discord.ui.Modal):
            def __init__(self, *, bot_client: commands.Bot, data: dict):
                super().__init__(title="szerep módosítása")
                self.bot_client = bot_client
                self.data: dict = data

                self.role_name_input = discord.ui.TextInput(
                    label='Szerep neve:',
                    default=role,
                    max_length=999,
                    style=discord.TextStyle.long,
                    required=True
                )

                self.prompt_input = discord.ui.TextInput(
                    label='Szerep:',
                    default=data[role]["prompt"],
                    style=discord.TextStyle.long,
                    required=True,
                    max_length=999
                )

                self.add_item(self.role_name_input)
                self.add_item(self.prompt_input)

            async def on_submit(self, interaction: discord.Interaction):
                new_role_name = self.role_name_input.value.strip()
                new_role_prompt = self.prompt_input.value.strip()

                if new_role_name == role:
                    self.data[role]["prompt"] = new_role_prompt
                    self.data[role]["author_id"] = str(interaction.user.id)
                else:
                    self.data[new_role_name] = {
                        "name": new_role_name,
                        "prompt": new_role_prompt,
                        "author_id": str(interaction.user.id)
                    }
                    del self.data[role]

                FILE_WRITER.save_json(filename="roles", data=self.data)
                await interaction.response.send_message(f"A '{new_role_name}' szerep sikeresen módosítva!",
                                                        ephemeral=True)

        if role in data:
            modal = ModifyRoleModal(bot_client=self._commands_bot, data=data)
            await self.interaction.response.send_modal(modal)

    _variation_cache: dict = {}

    async def generate_image(self, *, model: Optional[str], prompt: str) -> None:
        """
        Kép generálása.

        :param model: str - a modell
        :param prompt: str - a prompt
        :return:
        """
        await self.interaction.response.defer()

        status_msg: Optional[discord.Message] = None
        animation_task: Optional[asyncio.Task] = None

        async def animate_dots(message: discord.Message) -> None:
            dots: int = 0
            while True:
                dots = (dots % 3) + 1
                content: str = f"🎨 A kép éppen készül{'.' * dots}"
                try:
                    await message.edit(content=content)
                except (discord.NotFound, discord.Forbidden):
                    break
                except Exception as e:
                    print(f"Hiba az üzenet frissítésekor: {e}")
                    break
                await asyncio.sleep(0.5)

        try:
            status_msg = await self.interaction.followup.send("🎨A kép éppen készül.", wait=True)
            animation_task = asyncio.create_task(animate_dots(status_msg))

            loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
            imagen: ImagenAPIs = ImagenAPIs()
            path: str = await loop.run_in_executor(
                None,
                lambda: imagen.imagen_response(model=model, prompt=prompt)
            )

        except Exception as err:
            print(f"HIBA (CommandService.generate_image): {err}")
            if animation_task:
                animation_task.cancel()
            if status_msg:
                try:
                    await status_msg.delete()
                except Exception as e:
                    print(f"Hiba az üzenet törlésekor: {e}")
            return

        finally:
            if animation_task:
                animation_task.cancel()
            if status_msg:
                try:
                    await status_msg.delete()
                except Exception as e:
                    print(f"Hiba az üzenet törlésekor: {e}")

        if not path:
            await self.interaction.followup.send("Nem sikerült a kép generálása.")
            return

        try:
            filename: str = Path(path).stem
            img_file = FILE_READER.read_img(file_name=filename)

            if not img_file:
                await self.interaction.followup.send("Nem sikerült a kép generálása.")
                return

        except Exception as err:
            print(f"HIBA (CommandService.generate_image): {err}")
            return

        embed: discord.Embed = create_embed(
            description=prompt,
            color=random.randint(0, 0xFFFFFF),
            image_url=f"attachment://{img_file.filename}"
        )

        uuid_str: str = str(uuid.uuid4())
        CommandService._variation_cache[uuid_str] = prompt

        class VariationView(discord.ui.View):
            """
            A kép megtekintésének a view-ja. A gomb miatt van szükség rá.

            :param uuid_str: str - az azonosító
            :param cache: dict - a cache

            :function: variation_btn - A gomb lenyomásának a kezelése.
            :function: on_timeout - A view timeout-ja.
            """
            def __init__(self, *, uuid_str: str, cache: dict):
                super().__init__(timeout=300)
                self.uuid_str: str = uuid_str
                self.cache: dict = cache

            @discord.ui.button(label="🔄", style=discord.ButtonStyle.primary)
            async def variation_btn(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
                """
                A gomb lenyomásának a kezelése.

                :param interaction: discord.Interaction - az interakció objektum
                :param button: discord.ui.Button - a gomb objektum
                :return:
                """
                prompt: Optional[str] = self.cache.get(self.uuid_str)
                if not prompt:
                    await interaction.response.send_message("Nem található a kép.", ephemeral=True, delete_after=5)
                    return

                cmd_service: CommandService = CommandService(interaction=interaction)
                await cmd_service.generate_image(model=model, prompt=prompt)

            async def on_timeout(self) -> None:
                if self.uuid_str in self.cache:
                    del self.cache[self.uuid_str]

        view: VariationView = VariationView(uuid_str=uuid_str, cache=CommandService._variation_cache)

        embed.set_author(name=f"{self.interaction.user.display_name}", icon_url=self.interaction.user.avatar.url)
        await self.interaction.followup.send(
            embed=embed,
            view=view,
            file=img_file
        )

        try:
            Path(path).unlink()
        except Exception as err:
            print(f"HIBA (CommandService.generate_image): {err}")

