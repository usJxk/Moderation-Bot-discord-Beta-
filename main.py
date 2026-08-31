import os
import discord
import datetime
import random as r

from datetime import timedelta
from discord.ext import commands
from dotenv import load_dotenv

# Carga las variables del archivo .env
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
if TOKEN is None:
    raise ValueError("La variable de entorno DISCORD_TOKEN no está definida.")

intents = discord.Intents.all()

bot = commands.Bot(command_prefix="S", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as: {bot.user}")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Please pass in all requirements :rolling_eyes:.')
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You dont have all the requirements :angry:")

data_work = []
user_data = {}

@bot.command()
async def work(ctx):
    user_id = str(ctx.author.id)

    if user_id not in user_data:
        user_data[user_id] = {"bank": 0}

    worlds = ["Chef", "Airsoft Player", "COD Player", "Gamer", "YouTuber", "Tiktoker"] # Limpié un poco los extras :v
    random_job = r.choice(worlds)
    random_cash = r.randint(0, 5000)

    user_data[user_id]["bank"] += random_cash
    current_bank = user_data[user_id]["bank"]

    embed = discord.Embed(title="Work Simulation", color=discord.Color.green())
    embed.add_field(name="Job", value=random_job, inline=True)
    embed.add_field(name="Cash Earned", value=f"${random_cash}", inline=True)
    embed.add_field(name="Total in Bank", value=f"${current_bank}", inline=False)

    await ctx.send(embed=embed)
    

@bot.command()
@commands.has_permissions(kick_members=True)
async def purge(ctx, number: int, channel: discord.TextChannel = None, *, reason: str = "No reason provided"):#type:ignore
    if number <= 0 or number == None or number == "":
        await ctx.send("I cant delete 0 messages")
        return
    target_channel = channel or ctx.channel

    try:
        embed = discord.Embed(title="Purgered Channel")
        embed.add_field(name="Channel", value=target_channel.mention)
        embed.add_field(name="Messagges purgered", value=number)
        embed.add_field(name="Reason", value=reason)

        await target_channel.purge(limit=number)#type:ignore
        await ctx.send(embed=embed, delete_after=5)

    except:
        pass

data_warns = []

@bot.command()
@commands.has_permissions(kick_members=True)
async def warn(ctx, member: discord.Member = None, *, reason: str = "No reason provided"):#type:ignore
    if member is None:
        await ctx.send("Please, mention an user")
        return

    if member == bot.user:
        await ctx.send("Bruh")
        return

    count = sum(1 for w in data_warns if w.get("User ID") == member.id)
    sintaxis = {"Username": member.display_name, "Warn": reason, "User ID": member.id, "Number Warns": count}

    data_warns.append(sintaxis)
    try:
        embed = discord.Embed(title="Warn User", color=discord.Color.red())
        embed.add_field(name="User", value=member.mention, inline=False)
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Total Warns", value=str(count), inline=False)

        await ctx.send(embed=embed)
    except Exception:
        pass

@bot.command()
async def warned(ctx, member: discord.Member = None):#type:ignore
    if member is None:
        member = ctx.author

    user_warns = [w for w in data_warns if w.get("User ID") == member.id]
    count = len(user_warns)

    embed = discord.Embed(title=f"Member's Warn {member.display_name}", color=discord.Color.orange())
    embed.add_field(name="Total Warn", value=str(count), inline=False)

    if count > 0:
        reasons_text = "\n".join([f"• {w.get('Warn', 'No reason provided')}" for w in user_warns[-5:]])
        embed.add_field(name="Reason", value=reasons_text, inline=False)
    else:
        embed.add_field(name="Status", value="Has no warns provided", inline=False)

    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(kick_members=True)
async def mute(ctx, member: discord.Member = None, timelapse: float = 1, *, reason: str = "No reason provided"):#type:ignore
    if member is None:
        await ctx.send("Please, mention a member")
        return

    if member is bot.user:
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

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member=discord.Member, *, reason:str="No reason provided"):
    if member == ctx.author or member == bot.user:
        return await ctx.send("Bruh")

    embed = discord.Embed(title="Kick", description=None, color=discord.Color.red())
    embed.add_field(name="User", value=member, inline=True)
    embed.add_field(name="User id", value=member.id, inline=True)
    embed.add_field(name="Reason", value=reason, inline=False)

    try:
        await member.kick(reason=reason)#type:ignore
        await ctx.send(embed=embed)
    except discord.Forbidden:
        await ctx.send("Unexped permissions")
    except discord.HTTPException as e:
        await ctx.send(f"Error HTTP: {str(e)}")

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason: str = "No reason provided"):
    if member == ctx.author or member == bot.user:
        return await ctx.send("Bruh")

    embed = discord.Embed(title="Ban", color=discord.Color.red())
    embed.add_field(name="User", value=member.mention, inline=True)
    embed.add_field(name="User id", value=member.id, inline=True)
    embed.add_field(name="Reason", value=reason, inline=False)

    try:
        await member.ban(reason=reason, delete_message_days=2)  # type:ignore
        await ctx.send(embed=embed)

    except discord.Forbidden:
        await ctx.send("Insufficient permissions")
    except discord.HTTPException as e:
        await ctx.send(f"HTTP error: {e}")

@bot.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, user_id: int, *, reason: str = "No reason provided"):
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

try:
    bot.run(TOKEN)
except discord.errors.PrivilegedIntentsRequired as exc:
    print("Error: se requieren privileged intents que no están habilitados en el portal de Discord.")
    print("Detalle:", exc)
    print("Opciones para resolver:")
    print("- Ve a https://discord.com/developers/applications, selecciona tu aplicación, luego 'Bot' y habilita los 'Privileged Gateway Intents' necesarios (Server Members / Message Content / Presence) si tu bot los necesita.")
    print("- O ajusta el código para no solicitar intents privilegiados. Por ejemplo, no uses Intents.all() y evita `message_content` y `members` si no son necesarios.")
    print("Si quieres que lo haga por ti, dime qué intents necesita el bot y lo ajusto.")
    raise