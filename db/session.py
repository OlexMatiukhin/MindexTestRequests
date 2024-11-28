from fastapi import FastAPI, HTTPException, Depends
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URI = "mongodb://AdminMASI:admin1488%40%40%40%40%40@129.151.207.119:27017/"

app = FastAPI()


async def connect_db():
    try:
        client = AsyncIOMotorClient(MONGO_URI)
        await client.server_info()
        return client
    except ConnectionError as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")


async def get_collection(client: AsyncIOMotorClient, db_name: str, collection_name: str):
    try:
        db = client[db_name]
        collection = db[collection_name]
        return collection
    except ConnectionError as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")
