from os import getenv

from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv


load_dotenv()


cluster = AsyncIOMotorClient(getenv('data_url'))
general_q = cluster.ineverbot_questions.questions # General questions.
nsfw_q = cluster.ineverbot_questions.nsfw_questions # NSFW questions.


async def random_question(nsfw: bool = False) -> dict:
    col = nsfw_q if nsfw else general_q # Select collection.
    return await col.aggregate([{'$sample': {'size': 1}}]).next()
