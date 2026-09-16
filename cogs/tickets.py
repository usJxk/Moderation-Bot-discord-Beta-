import discord
from discord.ext import commands

# 1. El Modal (la ventana emergente con el cuadro de texto)
class TicketModal(discord.ui.Modal, title="Create Ticket"):
    # Campo de texto donde el usuario escribe su problema
    problema = discord.ui.TextInput(
        label="Whats your problem?",
        style=discord.TextStyle.paragraph, # Cuadro de texto grande
        placeholder="Whats happening?",
        required=True,
        max_length=1000
    )

    async def on_submit(self, interaction: discord.Interaction):
        guild = interaction.guild
        member = interaction.user
        
        # Obtenemos lo que escribió el usuario
        descripcion_problema = self.problema.value

        # (Opcional) Configuramos permisos para que solo el usuario y los admins vean el canal
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            member: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }

        # Creamos un nombre limpio para el canal basado en el usuario
        nombre_canal = f"ticket-{member.name}"
        
        # 2. Creamos el canal de texto privado
        nuevo_canal = await guild.create_text_channel(
            name=nombre_canal,
            overwrites=overwrites,
            topic=f"Ticket created by {member.name}. Problem: {descripcion_problema}"
        )

        # 3. Le respondemos al usuario de forma privada (ephemeral) avisándole que su canal está listo
        await interaction.response.send_message(
            f"Channel: {nuevo_canal.mention}",
            ephemeral=True
        )

        # 4. Mandamos un mensaje dentro del nuevo canal con el problema que escribió
        embed = discord.Embed(
            title=f"Ticket {member.name}'s",
            description=f"**Report:**\n{descripcion_problema}",
            color=0x101010
        )
        embed.set_footer(text=f"ID: {member.id}")
        
        await nuevo_canal.send(content=f"{member.mention} <@&ID_ROL_STAFF>", embed=embed) # Opcional: menciona al staff


# 2. La vista que contiene el botón que abre el Modal
class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None) # El botón no expira

    @discord.ui.button(label="Create", style=discord.ButtonStyle.green, emoji="🎟️", custom_id="open_ticket_button")
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Al hacer clic, mostramos el Modal configurado arriba
        await interaction.response.send_modal(TicketModal())


# 3. El Cog para registrar el comando que despliega el panel de tickets
print_ticket = None # Placeholder por si acaso

class TicketCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="panel_ticket")
    @commands.has_permissions(administrator=True)
    async def panel_ticket(self, ctx):
        embed = discord.Embed(
            title="System Tickets",
            description="Just click on the button if you have a problem with the website.",
            color=0x101010
        )
        # Enviamos el mensaje con el botón integrado
        await ctx.send(embed=embed, view=TicketView())

async def setup(bot):
    await bot.add_cog(TicketCog(bot))