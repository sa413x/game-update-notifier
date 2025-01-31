import json
from pathlib import Path
from loguru import logger


class ConfigManager:
    CONFIG_PATH = Path(__file__).parent.parent / "__config__" / "config.json"

    @staticmethod
    def load() -> dict:
        try:
            config_content = ConfigManager.CONFIG_PATH.read_text(
                encoding='UTF-8')
            config = json.loads(config_content)
            logger.success(f'Loaded config: {config}')
            return config
        except FileNotFoundError:
            logger.warning(
                f"Config file {ConfigManager.CONFIG_PATH} not found. Using default config.")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON: {e}")
            return {}

    @staticmethod
    def save(config: dict) -> None:
        ConfigManager.CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        ConfigManager.CONFIG_PATH.write_text(
            json.dumps(config, indent=4), encoding='UTF-8')
        logger.success(f'Config saved to {ConfigManager.CONFIG_PATH}')
