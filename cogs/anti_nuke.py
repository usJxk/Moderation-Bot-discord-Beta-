from datetime import datetime, timezone
import discord
from discord.ext import commands


class AntiNuke(commands.Cog):

  def __init__(self, bot: commands.Bot):
    self.bot = bot
    self.on = False  # Main system toggle

    self.history_ban = {}
    self.history_channels = {}
    self.TIME_WINDOW = 2.5

  @commands.command(name="antinuke", aliases=["active", "an"])
  @commands.has_permissions(administrator=True)
  async def toggle_antinuke(self, ctx, status: str = None):
    """Enables/disables AntiNuke or resets tracking notes."""
    if status and status.lower() in ["reset", "clear", "delete"]:
      self.history_ban.clear()
      self.history_channels.clear()

      embed = discord.Embed(
          title="🧹 Tracking Notes Cleared",
          description="All active history and time records have been deleted.",
          color=discord.Color.orange(),
          timestamp=datetime.now(timezone.utc),
      )
      await ctx.send(embed=embed)
      return

    if status is None:
      current_status = "Active 🟢" if self.on else "Disabled 🔴"
      embed = discord.Embed(
          title="🛡️ AntiNuke System Status",
          description=(
              f"Status: **{current_status}**\n\n- Use `!antinuke on` to"
              " activate.\n- Use `!antinuke off` to deactivate.\n- Use"
              " `!antinuke reset` to clear history."
          ),
          color=discord.Color.blue(),
          timestamp=datetime.now(timezone.utc),
      )
      await ctx.send(embed=embed)
      return

    status = status.lower()
    if status in ["on", "active", "true"]:
      self.on = True
      embed = discord.Embed(
          title="🛡️ AntiNuke Activated",
          description="The system is protecting against fast bans and channel nukes.",
          color=discord.Color.green(),
          timestamp=datetime.now(timezone.utc),
      )
      await ctx.send(embed=embed)
    elif status in ["off", "desactive", "false"]:
      self.on = False
      embed = discord.Embed(
          title="⚠️ AntiNuke Deactivated",
          description="System protection has been turned off.",
          color=discord.Color.red(),
          timestamp=datetime.now(timezone.utc),
      )
      await ctx.send(embed=embed)
    else:
      await ctx.send(
          "❌ Correct usage: `!antinuke on`, `!antinuke off`, or `!antinuke"
          " reset`"
      )

  @commands.command(name="cloneserver", aliases=["rebuild", "restore"])
  @commands.has_permissions(administrator=True)
  async def clone_server(self, ctx, source_guild_id: int):
    """Clones all categories and channels from a source guild ID to fix/rebuild this server."""
    source_guild = self.bot.get_guild(source_guild_id)
    target_guild = ctx.guild

    if not source_guild:
      await ctx.send(
          "❌ Error: The bot is not in the source server or the ID is invalid."
      )
      return

    msg = await ctx.send(
        "🔄 **Starting server restoration...** Wiping current channels and"
        " rebuilding structure. Please wait..."
    )

    try:
      # 1. Delete all current channels and categories in the target guild
      for channel in target_guild.channels:
        try:
          await channel.delete(reason="AntiNuke Server Restoration/Rebuild")
        except discord.HTTPException:
          pass

      # 2. Dictionary to map old category objects to new category objects
      category_mapping = {}

      # 3. First, recreate categories and channels without a category (orphans)
      # Categories first
      for cat in source_guild.categories:
        new_cat = await target_guild.create_category(
            name=cat.name,
            overwrites=cat.overwrites,
            position=cat.position,
            reason="AntiNuke Clone Category",
        )
        category_mapping[cat.id] = new_cat

      # 4. Recreate channels that do NOT belong to any category
      for channel in source_guild.channels:
        if channel.category is None:
          if isinstance(channel, discord.TextChannel):
            await target_guild.create_text_channel(
                name=channel.name,
                overwrites=channel.overwrites,
                topic=channel.topic,
                slowmode_delay=channel.slowmode_delay,
                nsfw=channel.nsfw,
                position=channel.position,
                reason="AntiNuke Clone Text Channel",
            )
          elif isinstance(channel, discord.VoiceChannel):
            await target_guild.create_voice_channel(
                name=channel.name,
                overwrites=channel.overwrites,
                bitrate=channel.bitrate,
                user_limit=channel.user_limit,
                position=channel.position,
                reason="AntiNuke Clone Voice Channel",
            )

      # 5. Recreate channels inside categories
      for cat in source_guild.categories:
        new_cat = category_mapping.get(cat.id)
        if not new_cat:
          continue

        for channel in cat.channels:
          if isinstance(channel, discord.TextChannel):
            await target_guild.create_text_channel(
                name=channel.name,
                category=new_cat,
                overwrites=channel.overwrites,
                topic=channel.topic,
                slowmode_delay=channel.slowmode_delay,
                nsfw=channel.nsfw,
                position=channel.position,
                reason="AntiNuke Clone Categorized Text Channel",
            )
          elif isinstance(channel, discord.VoiceChannel):
            await target_guild.create_voice_channel(
                name=channel.name,
                category=new_cat,
                overwrites=channel.overwrites,
                bitrate=channel.bitrate,
                user_limit=channel.user_limit,
                position=channel.position,
                reason="AntiNuke Clone Categorized Voice Channel",
            )

      embed = discord.Embed(
          title="✅ Server Structure Restored",
          description=(
              f"Successfully cloned all categories and channels from"
              f" **{source_guild.name}**."
          ),
          color=discord.Color.green(),
          timestamp=datetime.now(timezone.utc),
      )
      await msg.edit(content=None, embed=embed)

    except discord.Forbidden:
      await ctx.send(
          "❌ Error: Missing permissions to manage channels in this server."
      )
    except Exception as e:
      await ctx.send(f"❌ An unexpected error occurred during cloning: `{e}`")

  @commands.Cog.listener()
  async def on_audit_log_entry_create(self, entry: discord.AuditLogEntry):
    if not self.on:
      return

    guild = entry.guild
    moderator = entry.user
    now = datetime.now(timezone.utc)

    if not moderator or moderator.id == self.bot.user.id:
      return

    member_moderator = guild.get_member(moderator.id)
    if not member_moderator:
      return

    # Fast Bans Detection
    if entry.action == discord.AuditLogAction.ban:
      if moderator.id in self.history_ban:
        previous_time = self.history_ban[moderator.id]
        difference = (now - previous_time).total_seconds()

        if 0.001 <= difference <= self.TIME_WINDOW:
          await self.punish_attacker(
              guild,
              member_moderator,
              f"Mass bans detected in {difference * 1000:.1f}ms",
          )
          self.history_ban.pop(moderator.id, None)
          return

      self.history_ban[moderator.id] = now

    # Fast Channel Deletions Detection
    elif entry.action == discord.AuditLogAction.channel_delete:
      if moderator.id in self.history_channels:
        previous_time = self.history_channels[moderator.id]
        difference = (now - previous_time).total_seconds()

        if 0.001 <= difference <= self.TIME_WINDOW:
          await self.punish_attacker(
              guild,
              member_moderator,
              f"Mass channel deletion detected in {difference * 1000:.1f}ms",
          )
          self.history_channels.pop(moderator.id, None)
          return

      self.history_channels[moderator.id] = now

  async def punish_attacker(
      self, guild: discord.Guild, member: discord.Member, reason: str
  ):
    """Bans the attacker and sends a professional embed log."""
    try:
      if guild.me.top_role > member.top_role and guild.owner != member:
        await guild.ban(
            member,
            reason=f"Automated AntiNuke: {reason}",
            delete_message_days=1,
        )

        embed = discord.Embed(
            title="🚨 ANTINUKE TRIGGERED - ATTACKER NEUTRALIZED",
            description=(
                f"**Attacker:** {member.mention} (`{member.id}`)\n**Reason:**"
                f" `{reason}`\n**Action:** Automatically banned from the"
                " server."
            ),
            color=discord.Color.dark_red(),
            timestamp=datetime.now(timezone.utc),
        )
        embed.set_footer(text="AntiNuke Security System")

        for channel in guild.text_channels:
          if (
              channel.permissions_for(guild.me).send_messages
              and "log" in channel.name.lower()
          ):
            await channel.send(embed=embed)
            break
      else:
            print(f"[AntiNuke] Could not punish {member} due to role hierarchy rules.")

    except discord.Forbidden:
      print(f"[AntiNuke] Error: Missing permissions to ban {member}.")
    except discord.HTTPException:
      print("[AntiNuke] HTTP error encountered while trying to process emergency ban.")


async def setup(bot):
  await bot.add_cog(AntiNuke(bot))