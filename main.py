import os, logging
import discord
from dotenv import load_dotenv

# Basic setup
load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("bot.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)
logger.info("Logging started")
intents = discord.Intents.all()
bot = discord.Bot(intents=intents)
purple_color = discord.Color.from_rgb(94, 32, 216)


@bot.event
async def on_ready():
    logger.info(f"Bot is ready. Logged in as {bot.user}")


@bot.command(description="List of commands")
async def help(ctx: discord.ApplicationContext):
    embed = discord.Embed(
        title="Chronos Helper", description="List of commands", color=purple_color
    )
    embed.add_field(
        name="**/application**", value="Start a new application.", inline=False
    )
    embed.set_footer(text="Chronos Helper | Made by 𝝌𝘾𝗵𝗶ỺỺ𝝌 and wavefire_")
    embed.set_author(
        name=bot.user.name, icon_url=bot.user.avatar.url if bot.user.avatar else None
    )
    await ctx.send_response(embed=embed, ephemeral=True)


@bot.event
async def on_member_join(member: discord.Member):
    logger.info(f"New member {member.name}({member.id}) joined.")
    await member.send(
        f"Welcome to Chronos SMP, {member.mention}! Please use /application or click the button to start a new application.",
        view=ApplicationView(),
    )


class ApplicationModal(discord.ui.Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.add_item(
            discord.ui.InputText(
                label="What is your Minecraft username?", max_length=16
            )
        )
        self.add_item(
            discord.ui.InputText(
                label="Tell us a little bit about yourself.",
                style=discord.InputTextStyle.multiline,
                max_length=500,
            )
        )
        self.add_item(
            discord.ui.InputText(
                label="What is your time zone and your age?",
                style=discord.InputTextStyle.short,
                max_length=50,
            )
        )
        self.add_item(
            discord.ui.InputText(
                label="How long have you been playing Minecraft?",
                style=discord.InputTextStyle.short,
                max_length=50,
            )
        )
        self.add_item(
            discord.ui.InputText(
                label="What type of playstyle are you?",
                style=discord.InputTextStyle.short,
                placeholder="E.g redstone, villager farming, building etc.",
                max_length=200,
            )
        )

    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title=f"{interaction.user.name}'s Application", color=purple_color
        )
        embed.add_field(name=self.children[0].label, value=self.children[0].value)
        embed.add_field(name=self.children[1].label, value=self.children[1].value)
        embed.add_field(name=self.children[2].label, value=self.children[2].value)
        embed.add_field(name=self.children[3].label, value=self.children[3].value)
        embed.add_field(name=self.children[4].label, value=self.children[4].value)
        embed.set_footer(text="Chronos Helper | Made by 𝝌𝘾𝗵𝗶ỺỺ𝝌 and wavefire_")
        embed.set_author(
            name=bot.user.name,
            icon_url=bot.user.avatar.url if bot.user.avatar else None,
        )

        channel_id = os.getenv("APPLICATION_CHANNEL_ID")
        channel = bot.get_channel(channel_id)
        if channel:
            logger.info("New application created")
            logger.info(embed.to_dict())
            await channel.send(
                embeds=[embed], view=DecisionView(user_id=interaction.user.id)
            )

        await interaction.response.send_message(
            "Thanks for filling out the application!", ephemeral=True
        )


class ApplicationView(discord.ui.View):
    @discord.ui.button(label="Start Application")
    async def button_callback(self, button, interaction):
        await interaction.response.send_modal(ApplicationModal(title="Application"))


class DecisionView(discord.ui.View):
    def __init__(self, user_id) -> None:
        super().__init__()
        self.user_id = user_id

    async def disable_buttons(self):
        for item in self.children:
            if isinstance(item, discord.ui.Button):
                item.disabled = True

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green)
    async def confirm_button_callback(self, button, interaction):
        guild: discord.Guild = interaction.guild
        user = guild.get_member(self.user_id)
        role = discord.utils.get(guild.roles, name="Member")

        if role and user:
            await user.add_roles(role)
            await user.send("Thank you for applying! You have been accepted.")
            await interaction.response.send_message(f"{user.name} has been accepted.")
        else:
            await interaction.response.send_message("User or role not found.")

        await self.disable_buttons()
        await interaction.message.edit(view=self)

    @discord.ui.button(label="Reject", style=discord.ButtonStyle.red)
    async def reject_button_callback(self, button, interaction):
        user = bot.get_user(self.user_id)
        await user.send(
            "Thank you for applying! Unfortunately, your application has been rejected."
        )
        await interaction.response.send_message(f"{user.name} has been rejected.")

        await self.disable_buttons()
        await interaction.message.edit(view=self)


@bot.command(description="Start a new application.")
async def application(ctx: discord.ApplicationContext):
    modal = ApplicationModal(title="Application")
    await ctx.send_modal(modal)


bot.run(os.getenv("TOKEN"))
