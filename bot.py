# bot.py
import discord
from discord import app_commands
from discord.ext import commands
import os
import uuid
from core.loader import load_plugins
from dotenv import load_dotenv
load_dotenv()

# Discord Bot Setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Load plugins
plugins = load_plugins()
print(f"Loaded Plugins for Discord Bot: {plugins}")


class ConversionSelect(discord.ui.Select):
    def __init__(self, file_path: str, original_filename: str, available_plugins: list):
        self.file_path = file_path
        self.original_filename = original_filename
        self.available_plugins = available_plugins

        options = [
            discord.SelectOption(
                label=plugin["name"],
                description=f"{plugin['input']} → {plugin['output']}",
                value=plugin["module"].__name__,
            )
            for plugin in available_plugins
        ]

        super().__init__(
            placeholder="Choose a conversion...",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()

        selected_module_name = self.values[0]
        plugin = next(
            (p for p in self.available_plugins if p["module"].__name__ == selected_module_name),
            None,
        )

        if not plugin:
            await interaction.followup.send("❌ Invalid plugin selected.", ephemeral=True)
            if os.path.exists(self.file_path):
                os.remove(self.file_path)
            return

        try:
            output_file = plugin["module"].convert(self.file_path)

            name, ext_in = os.path.splitext(self.original_filename)
            ext_in = ext_in.lstrip(".")
            output_ext = plugin["output"]

            if output_ext == ext_in:
                attachment_filename = f"{name}_converted.{output_ext}"
            else:
                attachment_filename = f"{name}.{output_ext}"

            await interaction.channel.send(
                f"✅ Converted **{self.original_filename}** ({plugin['input']} → {plugin['output']})",
                file=discord.File(output_file, filename=attachment_filename),
            )

            if os.path.exists(self.file_path):
                os.remove(self.file_path)
            if os.path.exists(output_file):
                os.remove(output_file)

            await interaction.followup.send("✅ Conversion complete!", ephemeral=True)

        except Exception as e:
            await interaction.followup.send(f"❌ Error during conversion: {str(e)}", ephemeral=True)
            if os.path.exists(self.file_path):
                os.remove(self.file_path)


class ConversionView(discord.ui.View):
    def __init__(self, file_path: str, original_filename: str, available_plugins: list):
        super().__init__(timeout=300)  
        self.add_item(ConversionSelect(file_path, original_filename, available_plugins))


@bot.event
async def on_ready():
    print(f"✅ Bot logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")


@bot.tree.command(name="convert", description="Convert a file to another format")
@app_commands.describe(file="The file to convert")
async def convert(interaction: discord.Interaction, file: discord.Attachment):
    ext = file.filename.split(".")[-1].lower()

    compatible_plugins = [p for p in plugins if p["input"] == ext]

    if not compatible_plugins:
        await interaction.response.send_message(
            f"❌ No conversions available for `.{ext}` files.",
            ephemeral=True,
        )
        return

    os.makedirs("uploads", exist_ok=True)

    filename = f"{uuid.uuid4()}.{ext}"
    file_path = os.path.join("uploads", filename)

    try:
        await file.save(file_path)
    except Exception as e:
        await interaction.response.send_message(
            f"❌ Failed to download file: {str(e)}",
            ephemeral=True,
        )
        return

    view = ConversionView(file_path, file.filename, compatible_plugins)
    await interaction.response.send_message(
        f"**{file.filename}** uploaded! Choose a conversion:",
        view=view,
        ephemeral=True,
    )

@bot.tree.command(name="conversions", description="List all available file conversions")
async def conversions(interaction: discord.Interaction):
    if not plugins:
        await interaction.response.send_message(
            "❌ No conversion plugins available.",
            ephemeral=True,
        )
        return

    conversions_dict = {}
    for plugin in plugins:
        input_fmt = plugin["input"].upper()
        output_fmt = plugin["output"].upper()
        if input_fmt not in conversions_dict:
            conversions_dict[input_fmt] = []
        conversions_dict[input_fmt].append(output_fmt)

    embed = discord.Embed(
        title="Available Conversions",
        description="Here are all the file conversions supported:",
        color=discord.Color.blue()
    )

    for input_fmt in sorted(conversions_dict.keys()):
        outputs = ", ".join(sorted(conversions_dict[input_fmt]))
        embed.add_field(
            name=f"**{input_fmt}** →",
            value=outputs,
            inline=False
        )

    embed.set_footer(text=f"Total: {len(plugins)} conversion(s) available")

    await interaction.response.send_message(embed=embed, ephemeral=True)

if __name__ == "__main__":
    TOKEN = os.getenv("DISCORD_BOT_TOKEN")

    bot.run(TOKEN)