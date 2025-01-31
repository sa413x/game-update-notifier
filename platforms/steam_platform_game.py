from typing import Any
from loguru import logger
from cachetools import TTLCache, cached  # type: ignore
from steam.client import SteamClient  # type: ignore
from platforms import PlatformGameInterface


class SteamPlatform:
    _client: SteamClient | None = None
    _products_info: dict[str, dict[Any, Any]]

    @staticmethod
    @cached(cache=TTLCache(maxsize=1, ttl=3600))
    def get_client() -> SteamClient:
        """Return the authenticated cached SteamClient instance"""

        client = SteamClient()
        client.anonymous_login()
        return client

    @staticmethod
    def prepare_info(apps_ids: list[int]):
        """Query Steam API to cache all the products info"""

        client = SteamPlatform.get_client()
        SteamPlatform._products_info = client.get_product_info(apps=apps_ids)

    @staticmethod
    def get_products_info() -> dict[str, dict[Any, Any]]:
        """Return the cached products info"""

        return SteamPlatform._products_info


class SteamPlatformGame(PlatformGameInterface):
    def __init__(self, unique_id: str):
        self._unique_id = unique_id
        self._name = ''
        self._version = 0
        self._update_time = 0

    def get_platform_name(self) -> str:
        return 'Steam'

    @logger.catch
    async def collect_info(self) -> bool:
        app_id = int(self._unique_id)
        products_info = SteamPlatform.get_products_info()

        app_data = products_info['apps'][app_id]
        branch_data = app_data['depots']['branches']['public']

        self._version = int(branch_data['buildid'])
        self._update_time = int(branch_data['timeupdated'])
        self._name = app_data['common']['name']
        return self._version > 0

    def get_unique_id(self) -> str:
        return self._unique_id

    def get_version(self) -> str:
        return str(self._version)

    def get_update_timestamp(self) -> int:
        return self._update_time

    def get_name(self) -> str:
        return self._name

    def get_image_url(self) -> str:
        return f'https://cdn.cloudflare.steamstatic.com/steam/apps/{self._unique_id}/header.jpg'

    def get_patch_notes_url(self) -> str:
        if self._version > 0:
            return f'https://steamdb.info/patchnotes/{self._version}'
        return ''
