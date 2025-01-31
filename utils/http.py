from json import JSONDecodeError
from typing import Any
from loguru import logger

import aiohttp


async def http_get(url: str) -> dict[str, Any] | str | None:
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                response_text = await response.text()

                logger.trace(f"HTTP {response.status} GET {url}")
                logger.trace(response_text)

                if response.status == 200:
                    try:
                        return await response.json()
                    except (JSONDecodeError, UnicodeDecodeError) as e:
                        logger.error(f"Error decoding JSON: {e}")
                        return response_text
                else:
                    logger.error(f"HTTP error: {response.status}")
                    return None

        except aiohttp.ClientError as e:
            logger.error(f"Error during HTTP request: {e}")
            return None
