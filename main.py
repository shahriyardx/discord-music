import os
import wavelink
from discord.ext import commands
from discord import Intents
from essentials.player import WebPlayer
from dotenv import load_dotenv

load_dotenv(".env")

os.environ["JISHAKU_NO_DM_TRACEBACK"] = "true"


class MusicBot(commands.AutoShardedBot):
    def __init__(self, command_prefix, **options):
        super().__init__(command_prefix, **options)

        self.can_function = False
        self.error_message = (
            "Bot is not ready to listen your commands. Please try after a few moments."
        )

        if not hasattr(self, "wavelink"):
            self.wavelink = wavelink.Client(bot=self)

        self.loop.create_task(self.start_nodes())

    async def on_message(self, message):
        await self.process_commands(message)

    async def on_ready(self):
        print(f"{self.user} is ready to play musics")

    async def start_nodes(self):
        await self.wait_until_ready()

        await self.wavelink.initiate_node(
            host="127.0.0.1",
            port=2333,
            rest_uri="http://127.0.0.1:2333",
            password="youshallnotpass",
            identifier="MAIN",
            region="singapore",
        )

        for guild in self.guilds:
            if guild.me.voice:
                player: WebPlayer = self.wavelink.get_player(guild.id, cls=WebPlayer)
                try:
                    await player.connect(guild.me.voice.channel.id)
                    print(f"Connected to existing voice -> {guild.me.voice.channel.id}")
                except Exception as e:
                    print(e)

        self.can_function = True


intents = Intents.default()
intents.members = True

PREFIX = os.getenv("PREFIX")
bot = MusicBot(command_prefix=PREFIX, intents=intents)

bot.load_extension("cogs.music")
bot.load_extension("cogs.events")
bot.load_extension("cogs.help")
bot.load_extension("cogs.error_handler")

bot.load_extension("jishaku") # uncomment this if you want to debug
bot.load_extension("cog_reloader") # Uncomment this if you want to hot reload extensions whenever they get editted

TOKEN = os.getenv("TOKEN")
bot.run(TOKEN)
