import logging
import discord
from discord.ui.item import Item
from discord.ext import commands
from dotenv import load_dotenv
from config import *
from utils import *
from database import *

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
EMBED_COLOR = discord.Color.from_rgb(51, 46, 185)


@bot.event
async def on_ready():
    logger.info(f"Bot is ready. Logged in as {bot.user}")


@bot.command(description="List of commands")
async def help(ctx: discord.ApplicationContext):
    embed = discord.Embed(
        title="Chronos Helper", description="List of commands.", color=EMBED_COLOR
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
        view=ApplicationView(timeout=None),
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
            title=f"{interaction.user.name}'s Application", color=EMBED_COLOR
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

        mc_username = self.children[0].value

        if await check_minecraft_user(mc_username):
            application_document = {
                "username": mc_username,
                "about": self.children[1].value,
                "timezone-age": self.children[2].value,
                "playtime": self.children[1].value,
                "playstyle": self.children[1].value,
                "discord-id": interaction.user.id,
            }

            create_application(application_document)

            channel = bot.get_channel(APPLICATION_CHANNEL_ID)
            if channel:
                logger.info("New application created")
                logger.info(embed.to_dict())
                await channel.send(
                    embeds=[embed],
                    view=DecisionView(
                        user_id=interaction.user.id, mc_username=mc_username
                    ),
                )

                await interaction.response.send_message(
                    "Thanks for filling out the application!", ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    "Something went wrong. Please contact staff for help.",
                    ephemeral=True,
                )
        else:
            await interaction.response.send_message(
                "Minecraft username was invalid. Please fill out the application again.",
                ephemeral=True,
            )


class ApplicationView(discord.ui.View):
    @discord.ui.button(label="Start Application")
    async def button_callback(self, button, interaction):
        await interaction.response.send_modal(ApplicationModal(title="Application"))


class DecisionView(discord.ui.View):
    def __init__(self, user_id, mc_username) -> None:
        super().__init__()
        self.user_id = user_id
        self.mc_username = mc_username

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
            await whitelist_user(self.mc_username)

            await user.add_roles(role)
            await user.send(
                f"Thank you for applying! You have been accepted and added to the whitelist. The IP address of the server is `{RCON_HOST}`"
            )
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


@bot.command(description="List all usernames in applications.")
@commands.has_permissions(administrator=True)
async def view_applications(ctx: discord.ApplicationContext):
    usernames = get_users()
    if usernames:
        await ctx.response.send_message(
            view=ApplicationSelectionView(usernames=usernames)
        )
    else:
        await ctx.response.send_message("No applicants found.")


@view_applications.error
async def view_applications_error(ctx: discord.ApplicationContext, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.response.send_message(
            "You do not have permission to use this command.", ephemeral=True
        )


class ApplicationSelection(discord.ui.Select):
    def __init__(self, usernames: dict):
        self.usernames = usernames
        select_options = [
            discord.SelectOption(
                label=str(bot.get_user(user_id).name),
                value=str(user_id),
                description=username,
            )
            for user_id, username in usernames.items()
        ]

        super().__init__(
            placeholder="Select an application",
            min_values=1,
            max_values=1,
            options=select_options,
        )

    async def callback(self, interaction: discord.Interaction):
        user_id = int(self.values[0])
        mc_username = self.usernames[user_id]
        res: dict = get_application_by_mc(mc_username)["documents"][0]
        logger.info(res)

        embed = discord.Embed(title=f"{mc_username}'s Application", color=EMBED_COLOR)
        embed_data = {
            "What is your Minecraft username?": res["username"],
            "Tell us a little bit about yourself.": res["about"],
            "What is your time zone and your age?": res["timezone-age"],
            "How long have you been playing Minecraft?": res["playtime"],
            "What type of playstyle are you?": res["playstyle"],
        }

        for name, value in embed_data.items():
            embed.add_field(name=name, value=value)

        embed.set_footer(text="Chronos Helper | Made by 𝝌𝘾𝗵𝗶ỺỺ𝝌 and wavefire_")
        embed.set_author(
            name=bot.user.name,
            icon_url=bot.user.avatar.url if bot.user.avatar else None,
        )

        await interaction.response.send_message(
            embeds=[embed],
            view=DecisionView(
                user_id=user_id,
                mc_username=mc_username,
            ),
        )


class ApplicationSelectionView(discord.ui.View):
    def __init__(self, usernames):
        super().__init__()
        self.add_item(ApplicationSelection(usernames))


bot.run(TOKEN)
