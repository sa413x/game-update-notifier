from discord_webhook import DiscordEmbed, DiscordWebhook
from platforms import PlatformGameInterface
from notifiers import NotifierInterface


class DiscordNotifier(NotifierInterface):
    def __init__(self, webhook_url):
        self._webhook_url = webhook_url

    async def fire(self, platform_game: PlatformGameInterface):
        webhook = DiscordWebhook(url=self._webhook_url)

        embed = DiscordEmbed(
            title=f"{platform_game.get_name()}",
            description=f"{platform_game.get_platform_name()}"
        )

        embed.set_thumbnail(
            url=platform_game.get_image_url())
        embed.add_embed_field(
            name="🆔 ID", value=platform_game.get_unique_id())
        embed.add_embed_field(
            name="📦 Version", value=platform_game.get_version())
        embed.add_embed_field(name="⏰ Update Time",
                              value=platform_game.get_update_time_fmt())

        embed.add_embed_field(
            name="📜 Patch Notes", value=f"[Click here]({platform_game.get_patch_notes_url()})", inline=False)

        embed.set_timestamp()

        webhook.add_embed(embed)
        webhook.execute()
