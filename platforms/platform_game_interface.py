from datetime import datetime
from abc import ABC, abstractmethod


class PlatformGameInterface(ABC):
    @abstractmethod
    def get_platform_name(self) -> str:
        """Return the platform name."""

    @abstractmethod
    async def collect_info(self) -> bool:
        """Collect information about the game."""

    @abstractmethod
    def get_unique_id(self) -> str:
        """Return the unique ID of the game on the platform."""

    @abstractmethod
    def get_version(self) -> str:
        """Return the game build ID."""

    @abstractmethod
    def get_update_timestamp(self) -> int:
        """Return the game update timestamp."""

    @abstractmethod
    def get_name(self) -> str:
        """Return the name of the game."""

    @abstractmethod
    def get_image_url(self) -> str:
        """Return the URL of the game's image."""

    @abstractmethod
    def get_patch_notes_url(self) -> str:
        """Return the URL of the game's patch notes."""

    def get_update_time_fmt(self, fmt='%Y-%m-%d'):
        """Return the formatted update time of the game."""

        return datetime.fromtimestamp(self.get_update_timestamp()).strftime(fmt)

    def to_string(self) -> str:
        """Create a string representation of the game's information."""

        return (
            f"Unique ID: {self.get_unique_id()}\n"
            f"Build ID: {self.get_version()}\n"
            f"Update Time: {self.get_update_timestamp()}\n"
            f"Name: {self.get_name()}\n"
            f"Image URL: {self.get_image_url()}\n"
            f"Patch Notes URL: {self.get_patch_notes_url()}"
        )
