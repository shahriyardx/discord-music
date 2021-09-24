from discord.ext import commands
from essentials.errors import MustBeSameChannel, NotConnectedToVoice, PlayerNotConnected


class Errorhandler(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"`{error.param.name}` is a required argument.")

        if isinstance(error, commands.CommandNotFound):
            pass

        if isinstance(error, commands.NotOwner):
            pass

        if isinstance(error, commands.MissingPermissions):
            if len(error.missing_perms) > 1:
                sorno = "permissions"
                isare = "are"
            else:
                sorno = "permission"
                isare = "is"

            perms = ", ".join(error.missing_perms)
            await ctx.send(
                f"{perms.replace('_', ' ').replace('guild', 'server').title()} {sorno} {isare} required for you."
            )

        if isinstance(error, commands.BotMissingPermissions):
            if len(error.missing_perms) > 1:
                sorno = "permissions"
                isare = "are"
            else:
                sorno = "permission"
                isare = "is"

            perms = ", ".join(error.missing_perms)
            await ctx.send(
                f"{perms.replace('_', ' ').replace('guild', 'server').title()} {sorno} {isare} required for bot."
            )

        if isinstance(error, commands.MaxConcurrencyReached):
            await ctx.send(
                "You are trying to run same command multiple time at once. Please stop. If you are keep getting this problem report in the support server"
            )

        if isinstance(error, PlayerNotConnected):
            await ctx.send("Player is not connected to any voice channel.")

        if isinstance(error, MustBeSameChannel):
            await ctx.send("Please join to the channel where bot is connected.")

        if isinstance(error, NotConnectedToVoice):
            await ctx.send("You are not connected to any voice channel.")


def setup(bot):
    bot.add_cog(Errorhandler(bot))
