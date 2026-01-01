import discord
from discord.ext import commands

TOKEN = ""
TICKET_CATEGORY_NAME = "tickets"
STAFF_ROLE_NAME = "+"

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


# 🎯 Ticket sebep seçimi
class TicketReasonSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Destek", emoji="🛠️"),
            discord.SelectOption(label="Şikayet", emoji="⚠️"),
            discord.SelectOption(label="Başvuru", emoji="📄"),
            discord.SelectOption(label="Diğer", emoji="❓")
        ]

        super().__init__(
            placeholder="Ticket sebebini seçin",
            options=options,
            custom_id="ticket_reason"
        )

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        category = discord.utils.get(guild.categories, name=TICKET_CATEGORY_NAME)
        staff_role = discord.utils.get(guild.roles, name=STAFF_ROLE_NAME)

        if not category or not staff_role:
            await interaction.response.send_message(
                "Ticket sistemi yapılandırılmamış.", ephemeral=True
            )
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            staff_role: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }

        channel = await guild.create_text_channel(
            name=f"ticket-{interaction.user.name}",
            category=category,
            overwrites=overwrites
        )

        embed = discord.Embed(
            title="🎟️ Ticket Açıldı",
            description=(
                f"**Sebep:** {self.values[0]}\n\n"
                f"{interaction.user.mention} lütfen detayları yazın.\n"
                "Yetkililer sizinle ilgilenecektir."
            ),
            color=0x2ecc71
        )

        await channel.send(embed=embed, view=CloseTicketView())
        await interaction.response.send_message(
            f"Ticket oluşturuldu: {channel.mention}", ephemeral=True
        )


class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketReasonSelect())


# 🔒 SADECE YETKİLİ KAPATABİLİR
class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="🔒 Ticket Kapat",
        style=discord.ButtonStyle.red,
        custom_id="ticket_close"
    )
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        staff_role = discord.utils.get(interaction.guild.roles, name=STAFF_ROLE_NAME)

        if staff_role not in interaction.user.roles:
            await interaction.response.send_message(
                "Bu ticketi sadece yetkililer kapatabilir.", ephemeral=True
            )
            return

        await interaction.channel.delete()


@bot.event
async def on_ready():
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Game("🎟️ Ticket Sistemi")
    )

    bot.add_view(TicketView())
    bot.add_view(CloseTicketView())
    print(f"{bot.user} aktif!")


@bot.command()
async def ticket(ctx):
    embed = discord.Embed(
        title="🎟️ Destek Sistemi",
        description="Aşağıdan ticket sebebinizi seçiniz.",
        color=0x3498db
    )
    await ctx.send(embed=embed, view=TicketView())


bot.run(TOKEN)