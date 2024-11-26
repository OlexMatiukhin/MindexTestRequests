from fastapi import FastAPI, HTTPException, Body, Depends, Query
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from pymongo.errors import PyMongoError
from typing_extensions import Union, Annotated, List
from db.session import connect_db, get_collection
from models.tenderModels import Tender

from fastapi import FastAPI, HTTPException, Body, Depends, Query

from db.session import get_collection, connect_db



app = FastAPI()







#Get Tender without filtation fields
@app.get("/tenders", tags=["tenders"], response_model=List[Tender])
async def get_all_users(start: int = Query(default=0, ge=0), end: int = Query(default=0, ge=0),   client: AsyncIOMotorClient = Depends(connect_db)) -> List[Tender]:
    collection = await get_collection(client, "test_for_practice", "tenders_test")
    if start > 0 and end > start:
        start -= 1
        limit = end - start
        cursor = collection.find({
            "$or": [
                {"extended_info.region": "Київська область"},
                {"extended_info.region": "Чернівецька область"}
            ]
        }).sort([("$natural", -1)]).skip(start).limit(limit)
        tenders = await cursor.to_list(length=limit)
    else:
        cursor = collection.find({
            "$or": [
                {"extended_info.region": "Київська область"},
                {"extended_info.region": "Одеська область"}
            ]
        }).sort([("$natural", -1)]).skip(start).limit(15)
        tenders = await cursor.to_list()
    if not tenders:
        raise HTTPException(status_code=404, detail="No tenders found")

    return [Tender(**{**tender, "_id": str(tender["_id"])}) for tender in tenders]



#Get tender only with quantyty strings
@app.get("/tenders", tags=["tenders"], response_model=List[Tender])
async def get_all_users(start: int = Query(default=0, ge=0), end: int = Query(default=0, ge=0),   client: AsyncIOMotorClient = Depends(connect_db)) -> List[Tender]:
    collection = await get_collection(client, "test_for_practice", "tenders_test")
    if start > 0 and end > start:
        start -= 1
        limit = end - start
        cursor = collection.find({
            "$or": [
                {"extended_info.region": "Київська область"},
                {"extended_info.region": "Чернівецька область"}
            ]
        }).sort([("$natural", -1)]).skip(start).limit(limit)
        tenders = await cursor.to_list(length=limit)
    else:
        cursor = collection.find({
            "$or": [
                {"extended_info.region": "Київська область"},
                {"extended_info.region": "Одеська область"}
            ]
        }).sort([("$natural", -1)]).skip(start).limit(15)
        tenders = await cursor.to_list()
    if not tenders:
        raise HTTPException(status_code=404, detail="No tenders found")

    return [Tender(**{**tender, "_id": str(tender["_id"])}) for tender in tenders]






#Serach tenders
@app.get("/tenders/s", response_model=List[Tender])
async def search_users(request:str, client: AsyncIOMotorClient = Depends(connect_db)) -> List[Tender]:
    collection = await get_collection(client, "test_for_practice", "tenders_test")
    cursor = collection.find({
        "$or": [
            {"items.description": {"$regex": request, "$options": "i"}},
            {"title": {"$regex": request, "$options": "i"}}
        ]
    })
    tenders = await cursor.to_list()
    if not tenders:
        raise HTTPException(status_code=404, detail="No tenders found")
    return [Tender(**{**tender, "_id": str(tender["_id"])}) for tender in tenders]



@app.get("/tenders/{tender_id}", response_model=Tender, tags=["lol"])
async def get_tender(tender_id: str, client: AsyncIOMotorClient = Depends(connect_db)):

    if not ObjectId.is_valid(tender_id):
        raise HTTPException(status_code=400, detail=f"Invalid tender ID format: {tender_id}")

    object_id = ObjectId(tender_id)

    collection = await get_collection(client, "test_for_practice", "tenders_test")

    tender = await collection.find_one({"_id": object_id})
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")

    return Tender(**{**tender, "_id": str(tender["_id"])})


#Tenders filtratiron
@app.get("/tenders", tags=["tenders"], response_model=List[Tender])
async def get_all_users(sort_by:str=None, date_from:list=None, region:str=None, customer:str=None, supplier:str=None, quantity_strings: list[int]=None,   client: AsyncIOMotorClient = Depends(connect_db)) -> List[Tender]:
    collection = await get_collection(client, "test_for_practice", "tenders_test")
    if sort_by:


    if not tenders:
        raise HTTPException(status_code=404, detail="No tenders found")

    return [Tender(**{**tender, "_id": str(tender["_id"])}) for tender in tenders]




















