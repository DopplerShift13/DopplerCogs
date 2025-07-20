import discord
from redbot.core import commands, Config
import logging
from discord import app_commands
from discord.ext import commands

log = logging.getLogger("red.anonymousform")

class AnonymousForm(commands.Cog):
    """Allows users to submit anonymous feedback via modal."""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=87654321)
        default_guild = {
            "log_channel": None,
            "allowed_role": None  # New: role ID that is allowed to submit
        }
        self.config.register_guild(**default_guild)

    @commands.group(name="anonformset")
    @commands.guild_only()
    @commands.admin()
    async def anonformset(self, ctx):
        """Configure the Anonymous Form system."""
        pass

    @anonformset.command()
    async def channel(self, ctx, channel: discord.TextChannel):
        """Set the channel where anonymous feedback is sent."""
        await self.config.guild(ctx.guild).log_channel.set(channel.id)
        await ctx.send(f"✅ Anonymous form submissions will be sent to {channel.mention}")

    @anonformset.command()
    async def role(self, ctx, role: discord.Role):
        """Set the role allowed to use the anonymous form."""
        await self.config.guild(ctx.guild).allowed_role.set(role.id)
        await ctx.send(f"✅ Only members with the **{role.name}** role can submit feedback.")

    @app_commands.command(name="anonform", description="Submit anonymous feedback via a modal.")
    async def anonform(self, interaction: discord.Interaction):
        """Submit anonymous feedback via a modal."""

        # Permission check
        allowed_role_id = await self.config.guild(interaction.guild).allowed_role()
        if allowed_role_id:
            member = interaction.user
            role = discord.utils.get(member.roles, id=allowed_role_id)
            if not role:
                return await interaction.response.send_message(
                    "🚫 You don't have permission to use this command.", ephemeral=True)

        log_channel_id = await self.config.guild(interaction.guild).log_channel()
        if not log_channel_id:
            return await interaction.response.send_message("❌ Feedback channel not set.", ephemeral=True)

        class FeedbackModal(discord.ui.Modal, title="Anonymous Feedback Form"):
            feedback = discord.ui.TextInput(
                label="Your Feedback",
                placeholder="Write your message here...",
                style=discord.TextStyle.long,
                max_length=1000,
                required=True
            )

            async def on_submit(self, modal_interaction: discord.Interaction):
                log_channel = interaction.guild.get_channel(log_channel_id)
                if log_channel:
                    embed = discord.Embed(
                        title="📩 New Anonymous Feedback",
                        description=self.feedback.value,
                        color=discord.Color.blue()
                    )
                    await log_channel.send(embed=embed)
                await modal_interaction.response.send_message(
                    "✅ Your feedback has been submitted anonymously!", ephemeral=True)

        await interaction.response.send_modal(FeedbackModal())
