import asyncio
import logging
from typing import List

from loguru import logger
from asyncio import gather

from notifiers import NotifierInterface
from notifiers import TelegramNotifier

from utils import LogHandler
from utils import ConfigManager

from platforms import PlatformGameInterface
from platforms import HoYoPlayPlatformGame
from platforms import SteamPlatformGame, SteamPlatform

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    telegram_token: str
    telegram_chat_id: str
    steam_ids: str
    hoyoplay_ids: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class GameUpdateNotifier:
    def __init__(self, notifier: NotifierInterface, games: List[PlatformGameInterface]) -> None:
        self._notifier = notifier
        self._games = games
        self._config = ConfigManager.load()

    def check_game_updated(self, game: PlatformGameInterface) -> bool:
        platform_name, unique_id, version = map(
            str, [game.get_platform_name(), game.get_unique_id(),
                  game.get_version()]
        )

        if platform_name not in self._config:
            self._config[platform_name] = {}
            self._config[platform_name][unique_id] = version
            logger.warning(
                f"Platform name {platform_name} was not found in config. Creating new..."
            )
            return False

        if unique_id not in self._config[platform_name]:
            self._config[platform_name][unique_id] = version
            logger.warning(
                f"Unique ID {unique_id} was not found in config. Creating new..."
            )
            return False

        if self._config[platform_name][unique_id] != version:
            self._config[platform_name][unique_id] = version
            return True

        return False

    async def process_game(self, game: PlatformGameInterface):
        try:
            if not await game.collect_info():
                logger.error(
                    f"[{game.get_platform_name()}] {game.get_name()} failed to collect info"
                )
                return False

            if self.check_game_updated(game):
                logger.success(
                    f"[{game.get_platform_name()}] {game.get_name()} updated"
                )
                await self._notifier.fire(game)
                return True
            else:
                logger.info(
                    f"[{game.get_platform_name()}] {game.get_name()} not updated"
                )
                return False
        except Exception as e:
            logger.exception(
                f"Error processing game: [{game.get_platform_name()}] {game.get_name()} - {e}"
            )
            return False

    async def run(self):
        try:
            # Request info for all added Steam games
            SteamPlatform.prepare_info(
                [int(game.get_unique_id())
                 for game in self._games if isinstance(game, SteamPlatformGame)]
            )

            # Process all games
            results = await gather(*[self.process_game(game) for game in self._games])

            if any(results):
                ConfigManager.save(self._config)
                logger.success(f"Updated config saved: {self._config}")
            else:
                logger.info("No updates detected, config unchanged.")
        except Exception as e:
            logger.exception(f"Error in run method: {e}")


async def main():
    logging.basicConfig(handlers=[LogHandler()], level="INFO", force=True)

    settings = Settings()
    logger.success("Loaded configuration from .env")
    logger.success(settings.model_dump())

    steam_ids = settings.steam_ids.split(',') if settings.steam_ids else []
    hoyoplay_ids = settings.hoyoplay_ids.split(
        ',') if settings.hoyoplay_ids else []

    game_list = [
        platform(game_id)
        for platform, ids in (
            (SteamPlatformGame, steam_ids),
            (HoYoPlayPlatformGame, hoyoplay_ids),
        )
        for game_id in ids
    ]

    game_update_checker = GameUpdateNotifier(
        TelegramNotifier(settings.telegram_token,
                         settings.telegram_chat_id), game_list
    )

    while True:
        await game_update_checker.run()
        await asyncio.sleep(60)


if __name__ == "__main__":
    asyncio.run(main())
