from datetime import datetime
from loguru import logger
import asyncio

from aiocache import cached  # type: ignore

from platforms import PlatformGameInterface
from utils import http_get


class HoYoPlayPlatform:
    @staticmethod
    @cached(ttl=600)
    async def get_packages_data():
        packages_endpoints = [
            'http://sg-hyp-api.hoyoverse.com/hyp/hyp-connect/api/getGamePackages?launcher_id=VYTpXlbWo8',
            'http://hyp-api.mihoyo.com/hyp/hyp-connect/api/getGamePackages?launcher_id=jGHBHlcOq1',
        ]
        return await asyncio.gather(*[http_get(url) for url in packages_endpoints])

    @staticmethod
    @cached(ttl=600)
    async def get_games_data():
        games_endpoints = [
            'https://sg-hyp-api.hoyoverse.com/hyp/hyp-connect/api/getGames?launcher_id=VYTpXlbWo8',
            'http://hyp-api.mihoyo.com/hyp/hyp-connect/api/getGames?launcher_id=jGHBHlcOq1'
        ]
        return await asyncio.gather(*[http_get(url) for url in games_endpoints])


class HoYoPlayPlatformGame(PlatformGameInterface):
    def __init__(self, unique_id: str):
        self._unique_id = unique_id
        self._name = ''
        self._background_url = ''
        self._version = 0
        self._update_time = 0
        self._patch_notes_url = ''

    def get_platform_name(self) -> str:
        return 'HoYoPlay'

    @logger.catch
    async def collect_info(self) -> bool:
        try:
            game_data, package, posts = await asyncio.gather(
                HoYoPlayPlatformGame.get_game_data_by_id(self._unique_id),
                HoYoPlayPlatformGame.get_package_by_id(self._unique_id),
                HoYoPlayPlatformGame.get_posts_by_id(self._unique_id),
            )
        except Exception as e:
            logger.error(f"Error during async calls: {e}")
            return False

        # Check if any of the calls returned None
        if game_data is None or package is None or posts is None:
            return False

        self._name = game_data['display']['name']
        self._background_url = game_data['display']['background']['url']
        self._version = package['major']['version']
        self._patch_notes_url = posts['link']

        self._update_time = int(datetime.strptime(
            f'{datetime.now().year}/{posts["date"]}', '%Y/%m/%d').timestamp())

        return True

    def get_unique_id(self) -> str:
        return self._unique_id

    def get_version(self) -> str:
        return str(self._version)

    def get_update_timestamp(self) -> int:
        return self._update_time

    def get_name(self) -> str:
        return self._name

    def get_image_url(self) -> str:
        return self._background_url

    def get_patch_notes_url(self) -> str:
        return self._patch_notes_url

    @staticmethod
    async def get_package_by_id(target_id):
        """Fetch the package data by its ID."""

        packages = [pkg for data in await HoYoPlayPlatform.get_packages_data()
                    for pkg in data['data']['game_packages']]
        return next((pkg['main'] for pkg in packages if pkg['game']['id'] == target_id), None)

    @staticmethod
    async def get_game_data_by_id(target_id):
        """Fetch the game data by its ID."""

        games = [config for data in await HoYoPlayPlatform.get_games_data()
                 for config in data['data']['games']]
        return next((pkg for pkg in games if pkg['id'] == target_id), None)

    @staticmethod
    async def get_posts_by_id(target_id):
        """Fetch the latest announcement post by its ID."""

        posts_endpoints = [
            'https://sg-hyp-api.hoyoverse.com/hyp/hyp-connect/api/getGameContent?launcher_id=VYTpXlbWo8',
            'http://hyp-api.mihoyo.com/hyp/hyp-connect/api/getGameContent?launcher_id=jGHBHlcOq1'
        ]
        posts_data = await asyncio.gather(*[http_get(f'{url}&game_id={target_id}&language=eu')
                                            for url in posts_endpoints])

        # Filter out invalid data
        valid_posts_data = [
            data for data in posts_data
            if isinstance(data, dict) and data.get('data') is not None and data.get('retcode') == 0
        ]

        if not valid_posts_data:
            return None

        posts = [
            post_data for data in valid_posts_data for post_data in data['data'].get('content', {}).get('posts', [])
        ]

        # Find the latest announcement post
        return next((post for post in reversed(posts) if post.get('type') == 'POST_TYPE_ANNOUNCE'), None)
