import asyncio
import discord
import async_timeout
from wavelink import Player


class WebPlayer(Player):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.queue = asyncio.Queue()
        self.loop = "NONE"  # CURRENT, PLAYLIST
        self.currently_playing = None
        self.bound_channel = None
        self.controller_message = None
        self.player_is_invoking = False

    async def destroy(self, *, force: bool = False) -> None:
        player_message = self.controller_message

        if player_message:
            try:
                await player_message.delete()
            except:
                pass

        return await super().destroy(force=force)

    async def do_next(self) -> None:
        if self.is_playing:
            return

        try:
            self.waiting = True
            with async_timeout.timeout(300):
                track = await self.queue.get()
        except asyncio.TimeoutError:
            # No music has been played for 5 minutes, cleanup and disconnect...
            return await self.destroy()

        self.currently_playing = track
        await self.play(track)
        await self.invoke_player()

    async def invoke_player(self) -> None:
        if self.player_is_invoking:
            return

        self.player_is_invoking = True

        player_message = self.controller_message

        if player_message:
            try:
                await player_message.delete()
            except:
                pass

        track = self.current

        embed = discord.Embed(
            title=track.title, url=track.uri, color=discord.Color(0x2F3136)
        )

        embed.set_author(
            name=track.author, url=track.uri, icon_url=self.bot.user.avatar_url
        )

        embed.set_thumbnail(url=track.thumb)
        embed.add_field(
            name="Length",
            value=f"{int((self.position / 1000) // 60)}:{int((self.position / 1000) % 60)}/{int((track.length / 1000) // 60)}:{int((track.length / 1000) % 60)}",
        )
        embed.add_field(name="Looping", value=self.loop)
        embed.add_field(name="Volume", value=self.volume)

        next_song = ""

        if self.loop == "CURRENT":
            next_song = self.current.title
        else:
            if len(self.queue._queue) > 0:
                next_song = self.queue._queue[0].title

        if next_song:
            embed.add_field(name="Next Song", value=next_song, inline=False)

        self.controller_message = await self.bound_channel.send(embed=embed)
        self.bot.after_controller = 0
        self.player_is_invoking = False
