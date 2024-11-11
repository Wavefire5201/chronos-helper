import logging
import requests
from rcon import rcon
from config import *

logger = logging.getLogger(__name__)


async def check_minecraft_user(username: str) -> bool:
    re = requests.get(f"https://api.mojang.com/users/profiles/minecraft/{username}")
    logger.info(f"Sent API request to check if {username} is a valid user.")
    logger.info(re.json())
    return "id" in re.json()


async def whitelist_user(username: str) -> None:
    res = await rcon(
        f"whitelist add {username}",
        host=RCON_HOST,
        port=RCON_PORT,
        passwd=RCON_PASSWORD,
    )
    logger.info(f"Added {username} to whitelist.")
    logger.info(res)
