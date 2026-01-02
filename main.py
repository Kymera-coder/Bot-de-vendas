import discord
import os
from discord.ext import commands
from discord.ui import Button, View
from flask import Flask
from threading import Thread

# --- CÓDIGO PARA ENGANAR O RENDER (LIGA UM SITE FALSO) ---
app = Flask('')

@app.route('/')
def home():
    return "O Bot está vivo!"

def run():
  app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()
# ---------------------------------------------------------

# --- CONFIGURAÇÕES ---
TOKEN = os.environ.get("DISCORD_TOKEN")
CHAVE_PIX = "aquamatynho@gmail.com"
NOME_DO_PIX = "Vendedor"

PRODUTOS = {
    "diamante": "💎 Código Diamante: ABCD-1234-TESTE",
    "vip": "👑 Cargo VIP: Envie seu nick para eu ativar!",
    "nitro": "🚀 Nitro Link: https://discord.gift/codigo_exemplo"
}

# --- BOT ---
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

class PainelAdmin(View):
    def __init__(self, produto_key):
        super().__init__(timeout=None)
        self.produto_key = produto_key

    @discord.ui.button(label="✅ Aprovar Pagamento", style=discord.ButtonStyle.green)
    async def aprovar(self, interaction: discord.Interaction, button: Button):
        conteudo = PRODUTOS.get(self.produto_key)
        await interaction.response.send_message(f"✅ **Pagamento Confirmado!**\n\n{conteudo}")
        await interaction.channel.send(f"{interaction.user.mention} liberou o produto! Este carrinho será fechado em breve.")
        button.disabled = True
        await interaction.message.edit(view=self)

    @discord.ui.button(label="❌ Cancelar", style=discord.ButtonStyle.red)
    async def cancelar(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("❌ Venda cancelada.")
        await interaction.channel.delete()

class BotaoPagar(View):
    def __init__(self, produto_key):
        super().__init__(timeout=None)
        self.produto_key = produto_key

    @discord.ui.button(label="💸 Já fiz o Pix", style=discord.ButtonStyle.blurple)
    async def confirmar_pagamento(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message(f"🔔 {interaction.user.mention} avisou que pagou! Aguarde a verificação.", allowed_mentions=discord.AllowedMentions(users=True))
        await interaction.channel.send("👑 **ADMIN:** O Pix chegou? Se sim, libere o produto abaixo:", view=PainelAdmin(self.produto_key))
        button.disabled = True
        await interaction.message.edit(view=self)

class MenuSelecao(discord.ui.Select):
    def __init__(self):
        opcoes = [
            discord.SelectOption(label="Diamantes", description="R$ 10,00", value="diamante", emoji="💎"),
            discord.SelectOption(label="VIP", description="R$ 20,00", value="vip", emoji="👑"),
            discord.SelectOption(label="Nitro", description="R$ 30,00", value="nitro", emoji="🚀")
        ]
        super().__init__(placeholder="Selecione um produto...", min_values=1, max_values=1, options=opcoes)

    async def callback(self, interaction: discord.Interaction):
        produto_escolhido = self.values[0]
        guild = interaction.guild
        categoria = discord.utils.get(guild.categories, name="🛒 Carrinhos")
        
        if not categoria:
            categoria = await guild.create_category("🛒 Carrinhos")

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True)
        }

        canal = await guild.create_text_channel(f"compra-{interaction.user.name}", category=categoria, overwrites=overwrites)
        await interaction.response.send_message(f"Seu carrinho foi aberto em {canal.mention}!", ephemeral=True)

        embed = discord.Embed(title="Pagamento Pix", description=f"Produto: **{produto_escolhido.upper()}**", color=0x00ff00)
        embed.add_field(name="Chave Pix (E-mail)", value=f"`{CHAVE_PIX}`", inline=False)
        embed.set_footer(text="Ao pagar, clique no botão abaixo.")
        await canal.send(f"{interaction.user.mention}", embed=embed, view=BotaoPagar(produto_escolhido))

class ViewLoja(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(MenuSelecao())

@bot.event
async def on_ready():
    print(f'Bot Online! Logado como {bot.user}')

@bot.command()
async def setup(ctx):
    embed = discord.Embed(title="🛒 Loja do Bot", description="Escolha seu produto no menu abaixo:", color=0x0000ff)
    await ctx.send(embed=embed, view=ViewLoja())

# --- LIGA TUDO ---
if TOKEN:
    keep_alive() # Liga o site falso
    bot.run(TOKEN) # Liga o bot
else:
    print("ERRO: Token não encontrado!")
