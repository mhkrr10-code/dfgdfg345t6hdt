import discord
from discord import app_commands
from discord.ext import commands
import asyncio
from flask import Flask
from threading import Thread

# --- Keep Alive System ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- Bot Configuration ---
TOKEN = 'YOUR_BOT_TOKEN_HERE'
OWNERS = [1389628859225473277]  # Replace with your ID

class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()
        print(f"Global Slash Commands Synced.")

bot = MyBot()

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    # Set Streaming status: By BuWael
    await bot.change_presence(
        activity=discord.Streaming(name="By BuWael", url="https://twitch.tv/HeiL")
    )

# --- High-Speed Broadcast Logic ---
class BroadcastView(discord.ui.View):
    def __init__(self, interaction, message_text):
        super().__init__(timeout=60)
        self.message_text = message_text

    async def fast_send(self, member):
        """Helper function for individual high-speed sending."""
        if member.bot: return
        try:
            # Auto-mention feature
            await member.send(f"{self.message_text}\n{member.mention}")
            return True
        except:
            return False

    async def start_broadcast(self, interaction, member_list):
        await interaction.response.send_message(f"🚀 **Initiating High-Speed Broadcast** to {len(member_list)} members...", ephemeral=True)
        
        success = 0
        failed = 0
        
        # Process members in batches for speed
        for i in range(0, len(member_list), 5): 
            batch = member_list[i:i+5]
            tasks = [self.fast_send(m) for m in batch]
            results = await asyncio.gather(*tasks)
            
            success += results.count(True)
            failed += results.count(False)
            
            # Small delay to prevent instant global rate limit
            await asyncio.sleep(0.4) 
        
        await interaction.channel.send(
            f"✅ **Broadcast Completed**\n"
            f"👤 **Target:** {len(member_list)}\n"
            f"🟢 **Success:** {success}\n"
            f"🔴 **Failed:** {failed}"
        )

    @discord.ui.button(label="All Members", style=discord.ButtonStyle.gray, emoji="🌍")
    async def send_all(self, interaction: discord.Interaction, button: discord.ui.Button):
        members = interaction.guild.members
        await self.start_broadcast(interaction, members)
        self.stop()

    @discord.ui.button(label="Online Only", style=discord.ButtonStyle.green, emoji="⚡")
    async def send_online(self, interaction: discord.Interaction, button: discord.ui.Button):
        members = [m for m in interaction.guild.members if m.status != discord.Status.offline]
        await self.start_broadcast(interaction, members)
        self.stop()

    @discord.ui.button(label="Offline Only", style=discord.ButtonStyle.danger, emoji="💤")
    async def send_offline(self, interaction: discord.Interaction, button: discord.ui.Button):
        members = [m for m in interaction.guild.members if m.status == discord.Status.offline]
        await self.start_broadcast(interaction, members)
        self.stop()

# --- Slash Command ---

@bot.tree.command(name="bc", description="Send a high-speed broadcast message (No Cooldown)")
@app_commands.describe(message="The message to broadcast")
async def bc(interaction: discord.Interaction, message: str):
    if interaction.user.id not in OWNERS:
        return await interaction.response.send_message("❌ **Access Denied.**", ephemeral=True)

    # Cooldown check removed as requested

    embed = discord.Embed(
        title="Broadcast Control Center",
        description=f"**Message:** {message}\n\nSelect the target audience below:",
        color=0x2f3136
    )
    embed.set_footer(text="System by BuWael")
    
    view = BroadcastView(interaction, message)
    await interaction.response.send_message(embed=embed, view=view)

# Run Keep Alive
keep_alive()

# Run Bot
try:
    bot.run(TOKEN)
except Exception as e:
    print(f"Error: {e}")