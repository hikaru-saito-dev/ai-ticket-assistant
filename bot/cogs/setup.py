"""Setup cog for Discord bot."""

import logging
import discord
from discord import app_commands
from discord.ext import commands

logger = logging.getLogger(__name__)


class SetupCog(commands.Cog):
    """Cog for bot setup commands."""

    def __init__(self, bot: commands.Bot) -> None:
        """Initialize the setup cog."""
        self.bot = bot

    @app_commands.command(name="setup", description="Set up the bot for this server")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup(self, interaction: discord.Interaction) -> None:
        """
        Set up the bot for the server.

        Creates a "Tickets" category if it doesn't exist.
        This command requires administrator permissions.
        """
        if not interaction.guild:
            await interaction.response.send_message(
                "This command can only be used in a server.", ephemeral=True
            )
            return

        try:
            # Check if "Tickets" category already exists
            tickets_category = None
            for category in interaction.guild.categories:
                if category.name.lower() == "tickets":
                    tickets_category = category
                    break

            # Create category if it doesn't exist
            if not tickets_category:
                tickets_category = await interaction.guild.create_category("Tickets")
                logger.info(
                    f"Created 'Tickets' category in guild {interaction.guild.id}"
                )

            # Check if support role exists, create if not
            support_role = None
            for role in interaction.guild.roles:
                if role.name.lower() == "support":
                    support_role = role
                    break

            if not support_role:
                support_role = await interaction.guild.create_role(
                    name="Support",
                    mentionable=True,
                    reason="Auto-created by AI Ticket Assistant bot",
                )
                logger.info(
                    f"Created 'Support' role in guild {interaction.guild.id}"
                )

            await interaction.response.send_message(
                f"✅ Setup complete! The bot is ready to create tickets.\n"
                f"- Tickets category: {tickets_category.mention}\n"
                f"- Support role: {support_role.mention}",
                ephemeral=True,
            )
            logger.info(f"Setup completed successfully for guild {interaction.guild.id}")

        except app_commands.MissingPermissions:
            logger.warning(f"User {interaction.user.id} attempted setup without admin permissions")
            await interaction.response.send_message(
                "❌ You need administrator permissions to use this command.",
                ephemeral=True,
            )
        except Exception as e:
            logger.error(f"Error during setup: {e}", exc_info=True)
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "❌ An error occurred during setup. Please check bot permissions.",
                    ephemeral=True,
                )


async def setup(bot: commands.Bot) -> None:
    """Add the setup cog to the bot."""
    await bot.add_cog(SetupCog(bot))
    logger.info("SetupCog loaded")

