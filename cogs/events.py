import wavelink
from essentials.player import WebPlayer
from discord.ext import commands


class MusicEvents(commands.Cog, wavelink.WavelinkMixin):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.bot.players = {}
        self.bot.voice_users = {}
        self.bot.after_controller = 0

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        player: WebPlayer = self.bot.wavelink.get_player(
            message.guild.id, cls=WebPlayer
        )

        if not player.is_playing:
            return

        if player.bound_channel != message.channel:
            return

        self.bot.after_controller += 1

        if self.bot.after_controller > 5:
            if player.is_connected and player.is_playing:
                player_message = player.controller_message
                if not player_message:
                    return

                await player.invoke_player()

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        player: WebPlayer = self.bot.wavelink.get_player(member.guild.id, cls=WebPlayer)

        if member.id == self.bot.user.id:
            if before.channel and after.channel:
                if before.channel != after.channel:
                    await player.destroy()
                    await player.connect(after.channel.id)

        if after.channel:
            for voice_member in after.channel.members:
                self.bot.voice_users[voice_member.id] = {
                    "channel": after.channel.id,
                    "player": player,
                }
        else:
            try:
                self.bot.voice_users.pop(member.id)
            except:
                pass

    @wavelink.WavelinkMixin.listener("on_track_stuck")
    @wavelink.WavelinkMixin.listener("on_track_end")
    @wavelink.WavelinkMixin.listener("on_track_exception")
    async def on_player_stop(self, node: wavelink.Node, payload):
        if payload.player.loop == "CURRENT":
            return await payload.player.play(payload.player.currently_playing)

        if payload.player.loop == "PLAYLIST":
            await payload.player.queue.put(payload.player.currently_playing)

        await payload.player.do_next()


def setup(bot):
    bot.add_cog(MusicEvents(bot))
