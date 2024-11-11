import logging
import asyncio
from config import *
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.id import ID
from appwrite.query import Query

logger = logging.getLogger(__name__)

client = Client()
client.set_endpoint(APPWRITE_ENDPOINT)
client.set_project(APPWRITE_PROJECT_ID)
client.set_key(APPWRITE_API_KEY)
database = Databases(client)


def create_application(app: dict) -> None:
    try:
        res = database.create_document(
            database_id=APPWRITE_DB_ID,
            collection_id=APPWRITE_COLLECTION_ID,
            document_id=ID.unique(),
            data=app,
        )
        logger.info("Document created successfully: %s", res)
    except Exception as e:
        logger.error("Error creating document: %s", e)


def get_users() -> dict:
    try:
        res = database.list_documents(
            database_id=APPWRITE_DB_ID,
            collection_id=APPWRITE_COLLECTION_ID,
        )
        usernames = {
            document["discord-id"]: document["username"]
            for document in res["documents"]
        }
        logger.info("Retrieved usernames: %s", usernames)
        return usernames
    except Exception as e:
        logger.error("Error retrieving users: %s", e)
        return []


def get_application_by_mc(username: str):
    try:
        res = database.list_documents(
            database_id=APPWRITE_DB_ID,
            collection_id=APPWRITE_COLLECTION_ID,
            queries=[Query.search("username", username)],
        )
        logger.info("Searched for document: %s", res)
        return res
    except Exception as e:
        logger.error("Error searching document: %s", e)
