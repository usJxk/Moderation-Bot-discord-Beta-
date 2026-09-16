import datetime
from datetime import timedelta

import discord
from discord.ext import commands


class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.data_warns: list = []

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def purge(self, ctx, number: int, channel: discord.TextChannel = None, *, reason: str = "No reason provided"):  # type: ignore
        if number <= 0 or number is None or number == "":
            await ctx.send("I cant delete 0 messages")
            return
        target_channel = channel or ctx.channel

        try:
            embed = discord.Embed(title="Purgered Channel")
            embed.add_field(name="Channel", value=target_channel.mention)
            embed.add_field(name="Messagges purgered", value=number)
            embed.add_field(name="Reason", value=reason)

            await target_channel.purge(limit=number)  # type: ignore
            await ctx.send(embed=embed, delete_after=5)

        except Exception:
            pass

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def warn(self, ctx, member: discord.Member = None, *, reason: str = "No reason provided"):  # type: ignore
        if member is None:
            await ctx.send("Please, mention an user")
            return

        if member == self.bot.user:
            await ctx.send("Bruh")
            return

        count = sum(1 for w in self.data_warns if w.get("User ID") == member.id)
        sintaxis = {"Username": member.display_name, "Warn": reason, "User ID": member.id, "Number Warns": count}

        self.data_warns.append(sintaxis)
        try:
            embed = discord.Embed(title="Warn User", color=discord.Color.red())
            embed.add_field(name="User", value=member.mention, inline=False)
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Total Warns", value=str(count), inline=False)

            await ctx.send(embed=embed)
        except Exception:
            pass

    @commands.command()
    async def warned(self, ctx, member: discord.Member = None):  # type: ignore
        if member is None:
            member = ctx.author

        user_warns = [w for w in self.data_warns if w.get("User ID") == member.id]
        count = len(user_warns)

        embed = discord.Embed(title=f"Member's Warn {member.display_name}", color=discord.Color.orange())
        embed.add_field(name="Total Warn", value=str(count), inline=False)

        if count > 0:
            reasons_text = "\n".join([f"• {w.get('Warn', 'No reason provided')}" for w in user_warns[-5:]])
            embed.add_field(name="Reason", value=reasons_text, inline=False)
        else:
            embed.add_field(name="Status", value="Has no warns provided", inline=False)

        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def mute(self, ctx, member: discord.Member = None, timelapse: float = 1, *, reason: str = "No reason provided"):  # type: ignore
        if member is None:
            await ctx.send("Please, mention a member")
            return

        if member is self.bot.user:
            await ctx.send("You cant muted me :v")
            return

        try:
            calc = timedelta(minutes=timelapse)
            timeout_until = datetime.datetime.now(datetime.timezone.utc) + calc

            await member.timeout(timeout_until, reason=reason)

            embed = discord.Embed(title="Command Mute", description=None, color=discord.Color.red())
            embed.add_field(name="User", value=member.mention)
            embed.add_field(name="Duration", value=str(calc))
            embed.add_field(name="Reason", value=reason)
            embed.add_field(name="Timeout", value=timeout_until, inline=False)
            await ctx.send(embed=embed)
        except discord.Forbidden:
            await ctx.send("Unkown Permissions")
        except discord.HTTPException as e:
            await ctx.send(f"Error HTTP: {str(e)}")

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        if member == ctx.author or member == self.bot.user:
            return await ctx.send("Bruh")

        embed = discord.Embed(title="Kick", description=None, color=discord.Color.red())
        embed.add_field(name="User", value=member, inline=True)
        embed.add_field(name="User id", value=member.id, inline=True)
        embed.add_field(name="Reason", value=reason, inline=False)

        try:
            await member.kick(reason=reason)  # type: ignore
            await ctx.send(embed=embed)
        except discord.Forbidden:
            await ctx.send("Unexped permissions")
        except discord.HTTPException as e:
            await ctx.send(f"Error HTTP: {str(e)}")

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        if member == ctx.author or member == self.bot.user:
            return await ctx.send("Bruh")

        embed = discord.Embed(title="Ban", color=discord.Color.red())
        embed.add_field(name="User", value=member.mention, inline=True)
        embed.add_field(name="User id", value=member.id, inline=True)
        embed.add_field(name="Reason", value=reason, inline=False)

        try:
            await member.ban(reason=reason, delete_message_days=2)  # type: ignore
            await ctx.send(embed=embed)

        except discord.Forbidden:
            await ctx.send("Insufficient permissions")
        except discord.HTTPException as e:
            await ctx.send(f"HTTP error: {e}")

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user_id: int, *, reason: str = "No reason provided"):
        embed = discord.Embed(title="Unban", color=discord.Color.green())
        embed.add_field(name="User", value=f"<@{user_id}>", inline=False)
        embed.add_field(name="Reason", value=reason, inline=False)

        try:
            await ctx.guild.unban(discord.Object(id=user_id))
            await ctx.send(embed=embed)
        except discord.Forbidden:
            await ctx.send("Insufficient permissions")
        except discord.HTTPException as e:
            await ctx.send(f"HTTP error: {e}")


async def setup(bot: commands.Bot):
    await bot.add_cog(Moderation(bot))
