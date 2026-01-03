import discord
from discord.ext import commands
from discord.ui import View, Button
from flask import Flask
from threading import Thread

# ================= CONFIGURAÇÕES =================

TOKEN = "MTQ1Njc3MzU2ODUyMzE0NTI0MQ.GwOAAn.z1LZ8YC5RDQONKK8wZDItSE2-9D8siRhZt2zJ0"  # Token do bot
ADMIN_ID = 123456789012345678  # COLE SEU ID DO DISCORD AQUI
PIX_CHAVE = "aquamatynho@gmail.com"

# ================= KEEP ALIVE (RENDER) =================

app = Flask("keep_alive")

@app.route("/")
def home():
    return "Bot Online"

def run_flask():
    app.run(host="0.0.0.0", port=8080)

Thread(target=run_flask).start()

# ================= BOT =================

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ================= CARRINHO =================

class ProdutoView(View):
    def __init__(self):
        super().__init__(timeout=None)

        self.add_item(Button(label="💎 Diamante", style=discord.ButtonStyle.primary, custom_id="diamante"))
        self.add_item(Button(label="👑 VIP", style=discord.ButtonStyle.success, custom_id="vip"))
        self.add_item(Button(label="🔥 Nitro", style=discord.ButtonStyle.danger, custom_id="nitro"))

class PixView(View):
    def __init__(self, cliente, produto):
        super().__init__(timeout=None)

        self.cliente = cliente
        self.produto = produto

        self.add_item(Button(label="✅ Já fiz o Pix", style=discord.ButtonStyle.success, custom_id="pago"))

# ================= EVENTOS =================

@bot.event
async def on_ready():
    print("Bot ligado com sucesso!")

@bot.command()
async def setup(ctx):
    embed = discord.Embed(
        title="🛒 Loja Oficial",
        description="Escolha um produto abaixo:",
        color=0x00ff00
    )
    await ctx.send(embed=embed, view=ProdutoView())

@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type != discord.InteractionType.component:
        return

    user = interaction.user
    guild = interaction.guild

    # ===== PRODUTO SELECIONADO =====
    if interaction.data["custom_id"] in ["diamante", "vip", "nitro"]:
        produto = interaction.data["custom_id"]

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True),
            guild.me: discord.PermissionOverwrite(view_channel=True)
        }

        canal = await guild.create_text_channel(
            name=f"🛒-{user.name}",
            overwrites=overwrites
        )

        embed = discord.Embed(
            title="🧾 Carrinho Criado",
            description=(
                f"**Produto:** {produto.upper()}\n\n"
                f"💰 **Pix para pagamento:**\n`{PIX_CHAVE}`\n\n"
                "Após pagar, clique no botão abaixo."
            ),
            color=0x00ff00
        )

        await canal.send(embed=embed, view=PixView(user, produto))
        await interaction.response.send_message("Carrinho criado com sucesso!", ephemeral=True)

    # ===== CLIENTE CLICOU EM PAGUEI =====
    elif interaction.data["custom_id"] == "pago":
        admin = await bot.fetch_user(ADMIN_ID)

        embed = discord.Embed(
            title="💰 Novo Pagamento",
            description=(
                f"👤 Cliente: {interaction.user.mention}\n"
                f"📦 Produto: **{interaction.channel.name}**"
            ),
            color=0xffff00
        )

        view = View()
        view.add_item(Button(label="✔ Aprovar", style=discord.ButtonStyle.success, custom_id=str(interaction.channel.id)))

        await admin.send(embed=embed, view=view)
        await interaction.response.send_message("Pagamento enviado para aprovação!", ephemeral=True)

    # ===== ADMIN APROVOU =====
    elif interaction.user.id == ADMIN_ID:
        canal_id = int(interaction.data["custom_id"])
        canal = bot.get_channel(canal_id)

        if canal:
            embed = discord.Embed(
                title="✅ Pagamento Aprovado",
                description=(
                    "Pagamento confirmado!\n\n"
                    "**Produto entregue com sucesso.**\n"
                    "Obrigado pela compra!"
                ),
                color=0x00ff00
            )
            await canal.send(embed=embed)
            await interaction.response.send_message("Produto entregue com sucesso!", ephemeral=True)

# ================= START =================

bot.run(TOKEN)
