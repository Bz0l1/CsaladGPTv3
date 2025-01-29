import random
import time

import discord
from discord.ext import commands
from datetime import datetime

from source.file_service_handler.file_reader import read_json
from source.submode_services_handler.youtube_api import is_channel_live
from source.submode_services_handler.quoting import read_bible
from source.file_service_handler.file_writer import save_ima_date_time, save_percek
from source.file_service_handler.file_reader import get_token, read_txt


def create_embed(*, title: str = None, description: str = None, image_url: str = None, thumbnail_url: str = None,
                 color: int = 0x000000, timestamp: datetime = None, footer_text: str = None) -> discord.Embed:
    embed: discord.Embed = discord.Embed(color=color)

    if title: embed.title = title
    if description: embed.description = description
    if image_url: embed.set_image(url=image_url)
    if thumbnail_url: embed.set_thumbnail(url=thumbnail_url)
    if timestamp: embed.timestamp = timestamp
    if footer_text: embed.set_footer(text=footer_text)
    return embed


class CommandService:
    def __init__(self, *, interaction: discord.Interaction | None = None, bot: commands.Bot | None = None) -> None:
        self.interaction: discord.Interaction | None = interaction
        self.bot_client: discord.Client | None = (interaction.client if interaction is not None else None)
        self._commands_bot = bot
        self.bot_for_automatization: commands.Bot | None = bot

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
        data: dict = read_json("help")

        if command is None:
            print(data)
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
        print(is_command)
        url: str | None = is_channel_live(is_command=is_command)
        is_live: bool = url is not None

        if not is_live:
            title: str = "**NINCS STREAM**"
            description: str = "Sajnos Gogu még mindig távol van.\n||Lement tejért a dohányboltba.||"
            color: int = 0xf50000
            timestamp: datetime = datetime.now()
            footer_text: str = "STREAM"
            thumbnail_url: str = "https://cdn.discordapp.com/emojis/1151964870787481722.webp?size=96"
        else:
            title: str = "**STREAM VAN**"
            description: str = f"Megjött Fater/\nGyere, csatlakozz:\n{url}"
            color: int = 0x00f510
            timestamp: datetime = datetime.now()
            footer_text: str = "STREAM"
            thumbnail_url: str = "https://cdn.discordapp.com/emojis/1151964914274013274.webp?size=160&quality=lossless"

        if self.interaction is not None:
            await self.interaction.response.send_message(
                embed=create_embed(title=title, description=description, color=color, timestamp=timestamp,
                                   footer_text=footer_text, thumbnail_url=thumbnail_url))
        elif self.bot_for_automatization is not None:
            if is_live:
                channel: discord.TextChannel = self.bot_for_automatization.get_channel(
                    int(get_token("DISCORD_TEST_STREAM_CHANNEL_ID")))
                await channel.send(
                    embed=create_embed(title=title, description=description, color=color, timestamp=timestamp,
                                       footer_text=footer_text, thumbnail_url=thumbnail_url))

    async def ima(self, nyelv: str | None) -> None:
        is_command: bool = self.interaction is not None and self.bot_for_automatization is None
        if not is_command:
            date_from_file: str | datetime = read_txt("ima_date_time")
            date_str = date_from_file.strip()
            date_from_file = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%f")

            if (datetime.now() - date_from_file).days < 1:
                return

        verse, lang = read_bible(lang=nyelv)

        title: str = "🙏 Ima 🙏" if is_command else "🙏 Napi Ima 🙏"
        description: str = verse
        color: int = random.randint(0, 0xFFFFFF)
        timestamp: datetime = datetime.now()
        footer_text: str = "Ámen 🙏" if lang == "hu" else "Amen 🙏" if lang in ("en", "es") else "アーメン 🙏"
        thumbnail_url: str = "https://cdn.discordapp.com/attachments/1205275317682442320/1239558620471885825/aacbe7e2c0844e43a3009cef9a89d899.jpg?ex=66435c6d&is=66420aed&hm=25d8ae669bd928cb45ed6268883217606c2c6e6ecce68815fe06d7b8a1b4bf2f&"
        print(str(timestamp))

        if not is_command:
            save_ima_date_time(time=timestamp.isoformat())
            channel: discord.TextChannel = self.bot_for_automatization.get_channel(
                int(get_token("DISCORD_TEST_IMA_CHANNEL_ID")))
            await channel.send(
                embed=create_embed(title=title, description=description, color=color, timestamp=timestamp,
                                   footer_text=footer_text, thumbnail_url=thumbnail_url))
        else:
            await self.interaction.response.send_message(
                embed=create_embed(title=title, description=description, color=color, timestamp=timestamp,
                                   footer_text=footer_text, thumbnail_url=thumbnail_url))

    async def percek(self) -> None:
        data: str = read_txt("percek")
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
        save_percek(amount)
        await self.interaction.response.send_message(
            embed=create_embed(title=f"A perc számláló módosítva: {amount} percre"))

    async def javaslat(self, *, theme: str) -> None:
        if theme == "bot":
            user_id = int(get_token("DEV_USER_ID"))
            user = await self.bot_client.fetch_user(user_id)
            if user:
                try:
                    await user.send("Új javaslat érkezett a botról!")
                    await self.interaction.response.send_message("Javaslat elküldve a fejlesztőnek DM-ben!",
                                                                 ephemeral=True)  # Visszajelzés a felhasználónak
                except discord.Forbidden:
                    await self.interaction.response.send_message(
                        "Nem tudtam DM-et küldeni a fejlesztőnek. Lehet, hogy le van tiltva.", ephemeral=True)
                except Exception as e:
                    await self.interaction.response.send_message(f"Hiba történt a DM küldésekor: {e}", ephemeral=True)
            else:
                await self.interaction.response.send_message("Nem találtam a fejlesztőt.", ephemeral=True)

        elif theme == "szerver":
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

                def __init__(self, bot_client: commands.Bot):
                    super().__init__(title='Javaslat beküldése')
                    self.bot_client = bot_client

                async def on_submit(self, interaction: discord.Interaction):
                    javaslat_szoveg = self.javaslat.value
                    kudo_szoveg = self.kuldo.value or "Egy névtelen családtag"

                    channel_id = int(get_token("DISCORD_TEST_SUGGESTION_CHANNEL_ID"))
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

            modal = JavaslatModal(self._commands_bot)
            await self.interaction.response.send_modal(modal)


"""
async def convert(self, from_currency: str, amount: int) -> str:
    if from_currency == "perc":
        forint_value = amount * 200
        formatted_forint = f'{forint_value:,}'.replace(',', '.')
        return f"{formatted_forint} gulden"

    else:
        minute_value = amount / 200
        hour_value = minute_value / 60
        return f'{amount} gulden = {minute_value:.2f} perc = {hour_value:.2f} óra'
"""

"""
async def insult(self, *, user: discord.Member | None = None, role: discord.Role | None = None, author) -> str:
    if user is None and role is None:
        return (f"{self.interaction.user.mention} megsértette saját magát:\n"
                f"> te egy {self.quoting.read_insult(False)}")

    if user is not None:
        author: discord.Member = author
        start_insult: list[str] = [
            "hogy rohadnál meg te ",
            "te kis ",
            "te ",
            "te nagy ",
            "te büdös "
        ]

        return (f"{author.mention} megsértett téged {user.mention}:\n"
                f"> {user.mention} {random.choice(start_insult)} {self.quoting.read_insult(False)}")

    if role is not None:
        start_insult: list[str] = [
            "ti büdös ",
            "ti kis ",
            "ti ",
            "ti nagy ",
        ]

        if role.is_default():
            return (f"{author.mention} megsértett mindenkit:\n"
                    f"> @everyone {random.choice(start_insult)}{self.quoting.read_insult(True)}")

        return (f"{author.mention} megsértett titeket, {role.mention}-k:\n"
                f"> {role.mention} {random.choice(start_insult)}{self.quoting.read_insult(True)}")

async def jimmy(self) -> str:
    return self.quoting.read_jimmy()
"""

"""
async def say(self, *, role: str, prompt: str = "", model: str = "gpt3") -> str | bool:
    if self.gpt.get_gpt(role) == {}:
        return False

    if prompt == "":
        return "Meow/ 🐱"

    return await self.gpt.say(model=model, role=role, prompt=prompt)

async def list_roles(self) -> discord.Embed:
    desc: str = "\n".join(
        [f"**{role['gpt-role']} - {role['summary'] if role['summary'] != '' else 'Nincs leírás'}**"
         for role in self.gpt.gpts.values()])
    return create_embed(title="Elérhető szerepek:", description=desc, color=0x630099, timestamp=datetime.now(),
                        footer_text="Használd a `/say <szerep> <prompt>` parancsot a szerepek használatához.")

async def newrole(self, *, name: str, prompt: str, user_id: str, summary: str | None = None) -> (str, bool):
    if self.gpt.new_roles(name=name, prompt=prompt, user_id=user_id, summary=summary):
        return f"Sikeresen hozzáadtad a `{name}` szerepet!", True
    return f"A `{name}` szerep már létezik!", False

async def delete_role(self, *, name: str, user_id: str) -> (str, bool):
    gpt: dict = self.gpt.get_gpt(name)
    moderator_id: str = file_handler.get_token("MODERATOR_TEST_ROLE_ID")

    if gpt == {}:
        return f"A `{name}` szerep nem található!", False

    if (user_id or moderator_id) not in gpt["user_id"]:
        return "🚫 Nincs jogosultságod a szerep törléséhez/ 🚫", False

    if self.gpt.remove_roles(name=name):
        return f"{name} sikeresen törölve", True

    return f"{name} törlése sikertelen", False

async def bejelentes(self, *, title: str, description: str, author: str) -> discord.Embed | None:
    embed = create_embed(title=title, description=description, color=0x00f510, timestamp=datetime.now(),
                         footer_text=f"{author}")

    return embed

async def get_xp(self, member: discord.Member) -> str:
    return await self.xp.get_user_level(member)

"""
