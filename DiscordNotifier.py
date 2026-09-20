from typing import Optional
from discord_webhook import DiscordWebhook, DiscordEmbed


class DiscordWebhookClient:
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    def _send(self, embed: DiscordEmbed) -> None:
        if not self.webhook_url:
            return

        webhook = DiscordWebhook(url=self.webhook_url)
        webhook.add_embed(embed)

        try:
            webhook.execute()
        except Exception:
            return

    def base_embed(self, title: str, icon_url: Optional[str] = None) -> DiscordEmbed:
        embed = DiscordEmbed(
            title=title,
            color=0x03B2F8,
        )

        if icon_url:
            embed.set_thumbnail(url=icon_url)

        embed.set_footer(text="Hoyolab Auto Check-in")
        embed.set_timestamp()
        return embed

    def send_notification(self, account, reward) -> None:
        embed = self.base_embed(
            title=f"{reward.game_name} Daily Check-In",
            icon_url=reward.icon,
        )

        embed.add_embed_field(name="UID", value=account.game_uid)
        embed.add_embed_field(name="Level", value=str(account.level))
        embed.add_embed_field(name="Name", value=account.nickname)
        embed.add_embed_field(name="Server", value=account.region_name)
        embed.add_embed_field(
            name="Reward",
            value=f"{reward.name} x {reward.cnt}",
        )

        self._send(embed)

    def send_error(self, message: str) -> None:
        embed = self.base_embed(title="Daily Check-In - Error")
        embed.add_embed_field(name="Error", value=message)
        self._send(embed)
