import discord
from redbot.core import commands, Config
import logging

log = logging.getLogger("red.anonymousform")

class AnonymousForm(commands.Cog):
    """Allows users to submit anonymous feedback via modal."""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=87654321)
        default_guild = {"log_channel": None}
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

    @commands.command(name="anonform")
    @commands.guild_only()
    async def anonform(self, ctx: commands.Context):
        """Submit anonymous feedback via modal."""

        # Attempt to delete the command message for privacy
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass  # Bot doesn't have permission to delete the message

        log_channel_id = await self.config.guild(ctx.guild).log_channel()
        if not log_channel_id:
            return await ctx.send("❌ Feedback channel not set. Please contact an admin.")

        class FeedbackModal(discord.ui.Modal, title="Anonymous Feedback Form"):
            feedback = discord.ui.TextInput(
                label="Your Feedback",
                placeholder="Write your message here...",
                style=discord.TextStyle.long,
                max_length=1000,
                required=True
            )

            async def on_submit(self, interaction: discord.Interaction):
                log_channel = ctx.guild.get_channel(log_channel_id)
                if log_channel:
                    embed = discord.Embed(
                        title="📩 New Anonymous Feedback",
                        description=self.feedback.value,
                        color=discord.Color.blue()
                    )
                    await log_channel.send(embed=embed)
                await interaction.response.send_message("✅ Your feedback has been submitted anonymously!", ephemeral=True)

        await ctx.send_modal(FeedbackModal())