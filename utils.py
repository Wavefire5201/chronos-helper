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


async def sanitize_minecraft_user(username: str) -> str:
    re = requests.get(f"https://api.mojang.com/users/profiles/minecraft/{username}")
    return re.json()["name"]


async def whitelist_user(username: str) -> None:
    command = f"whitelist add {username}"
    logger.info(f"Ran {command}")
    res = await rcon(
        command,
        host=RCON_HOST,
        port=RCON_PORT,
        passwd=RCON_PASSWORD,
    )
    logger.info(res)


async def get_whitelist() -> list:
    command = f"whitelist list"
    res = await rcon(
        command,
        host=RCON_HOST,
        port=RCON_PORT,
        passwd=RCON_PASSWORD,
    )
    logger.info(res)
    return res.split(":")[1].strip().split(", ")
