import discord
from discord import app_commands
import os

# Configuration
TOKEN = ''
FILE_PATH = './discord.db'

class MyClient(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()
        print("✅ Commandes slash synchronisées")

    async def on_ready(self):
        print(f'✅ Bot connecté en tant que {self.user}')

client = MyClient()

@client.tree.command(name="search", description="Recherche dans le fichier discord.db")
@app_commands.describe(terme="Le terme à rechercher")
async def search(interaction: discord.Interaction, terme: str):
    await interaction.response.defer()
    
    try:
        # Vérifier si le fichier existe
        if not os.path.exists(FILE_PATH):
            await interaction.followup.send("❌ Fichier discord.db introuvable")
            return
        
        # Lire le fichier
        with open(FILE_PATH, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        # Rechercher les lignes correspondantes
        matching_lines = []
        for line_num, line in enumerate(lines, 1):
            if terme.lower() in line.lower():
                matching_lines.append(f"Ligne {line_num}: {line.strip()}")
        
        if not matching_lines:
            await interaction.followup.send(f"❌ Aucune ligne trouvée pour: `{terme}`")
            return
        
        # Préparer la réponse
        response = f"🔍 **Résultats pour `{terme}`** ({len(matching_lines)} ligne(s)):\n```"
        
        for match in matching_lines:
            if len(response + match + "\n") > 1900:
                response += "```"
                await interaction.followup.send(response)
                response = f"```{match}\n"
            else:
                response += f"{match}\n"
        
        response += "```"
        await interaction.followup.send(response)
        
    except Exception as e:
        print(f"Erreur recherche: {e}")
        await interaction.followup.send("❌ Erreur lors de la lecture du fichier")

@client.tree.command(name="drop", description="Envoie le fichier discord.db complet")
async def drop(interaction: discord.Interaction):
    await interaction.response.defer()
    
    try:
        # Vérifier si le fichier existe
        if not os.path.exists(FILE_PATH):
            await interaction.followup.send("❌ Fichier discord.db introuvable")
            return
        
        # Vérifier la taille du fichier
        file_size = os.path.getsize(FILE_PATH)
        if file_size == 0:
            await interaction.followup.send("📭 Le fichier discord.db est vide")
            return
        
        # Envoyer le fichier
        await interaction.followup.send(
            content="📁 **Fichier discord.db complet:**",
            file=discord.File(FILE_PATH)
        )
        
    except Exception as e:
        print(f"Erreur drop: {e}")
        await interaction.followup.send("❌ Erreur lors de l'envoi du fichier")

# Lancement du bot
if __name__ == "__main__":
    print("🚀 Démarrage du bot...")
    client.run(TOKEN)