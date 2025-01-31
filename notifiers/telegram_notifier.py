from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from platforms import PlatformGameInterface
from notifiers import NotifierInterface


class TelegramNotifier(NotifierInterface):
    def __init__(self, api_key, chat_id):
        self._api_key = api_key
        self._chat_id = chat_id
        self._bot = Bot(token=self._api_key)

    async def fire(self, platform_game: PlatformGameInterface):
        # Prepare game details
        game_title = f"*{platform_game.get_name()}* ({platform_game.get_platform_name()})"
        game_details = [
            f"ID: *{platform_game.get_unique_id()}*",
            f"Version: *{platform_game.get_version()}*",
            f"Update Time: *{platform_game.get_update_time_fmt()}*"
        ]
        caption = f"{game_title}\n\n" + "\n".join(game_details)

        patch_notes_url = platform_game.get_patch_notes_url()
        image_url = platform_game.get_image_url()

        await self._bot.send_photo(
            chat_id=self._chat_id,
            photo=image_url,
            caption=caption,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(
                    'Open Patch Notes', url=patch_notes_url)]] if patch_notes_url else []
            )
        )
