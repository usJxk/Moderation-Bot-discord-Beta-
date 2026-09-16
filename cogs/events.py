from discord.ext import commands

class Events(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Logged in as: {self.bot.user}")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please pass in all requirements :rolling_eyes:.")
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You dont have all the requirements :angry:")


async def setup(bot: commands.Bot):
    await bot.add_cog(Events(bot))
