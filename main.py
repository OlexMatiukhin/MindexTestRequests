from datetime import datetime, timedelta

from fastapi import FastAPI, HTTPException, Body, Depends, Query
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from pymongo.errors import PyMongoError
from typing_extensions import Union, Annotated, List, Optional, Tuple, Dict
from db.session import connect_db, get_collection
from models.tenderModels import Tender

from fastapi import FastAPI, HTTPException, Body, Depends, Query

from db.session import get_collection, connect_db



app = FastAPI()













#Get and filtrate elements

@app.get("/tenders/allfiltr",  tags=["tenders"])
async def get_all_tenders(
        suspicious_level: Optional[str] = Query(None),
        sort_by: Optional[str] = Query(None),
        date_from: Optional[List[str]] = Query(None),
        region: Optional[str] = Query(None),
        organization: Optional[str] = Query(None),
        budget: Optional[List[float]] = Query(None),
        customer: Optional[str] = Query(None),
        quantity_strings: Optional[List[int]] = Query(None),
        client: AsyncIOMotorClient = Depends(connect_db)
) -> List[Tender]:
    query = {}
    collection = await get_collection(client, "test_for_practice", "tenders_test")
    if collection is None:
        raise HTTPException(status_code=500, detail="Database collection not found.")


    if suspicious_level:
        query["analysis.suspicious_level"] = suspicious_level

    if date_from and len(date_from) == 2:
        try:
            start_date = datetime.strptime(date_from[0], "%Y-%m-%d")
            end_date = datetime.strptime(date_from[1], "%Y-%m-%d")
            start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
            if start_date>end_date:
                query["creation_date"] = {
                    "$gte": start_date.isoformat(),
                    "$lte": end_date.isoformat()
                }
            else:
                raise HTTPException(status_code=400, detail="Start  date must be.")

        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

    if region:
        if isinstance(region, str):
            region = [region]
        query["extended_info.region"] = {"$in": region}

    if customer:
        query["extended_info.contact_info.name"] = customer

    if budget and len(budget) == 2:
        query["budget_info.amount"] = {"$gte": budget[0], "$lte": budget[1]}

    if organization:
        query["extended_info.organization"] = {"$regex": organization, "$options": "i"}
    sort_key = []
    if sort_by:
        sort_mapping = {
            "новіші": ["creation_date", 1],
            "старші": ["creation_date", -1],
            "дешевші": ["budget_info.amount", 1],
            "дорожчі": ["budget_info.amount", -1],
        }
        try:
            sort_key = sort_mapping[sort_by]
        except KeyError:
            raise HTTPException(status_code=400, detail="Invalid sort_by parameter.")
    else:
        sort_key = ["$natural", 1]

    start = 0
    limit = 15
    if quantity_strings and len(quantity_strings) == 2:
        start, end = quantity_strings
        if 0 < start < end:
            start -= 1
            limit = end - start

        else:
            raise HTTPException(status_code=400, detail="Invalid range in quantity_strings.")

    cursor = collection.find(query).sort(sort_key[0], sort_key[1]).skip(start).limit(limit)
    tenders = await cursor.to_list(length=limit)


    if not tenders:
        raise HTTPException(status_code=404, detail="No tenders found.")

    return [Tender(**{**tender, "_id": str(tender["_id"])}) for tender in tenders]




#Serach tenders
@app.get("/tenders/search")
async def search_tenders(request:str, client: AsyncIOMotorClient = Depends(connect_db)) -> List[Tender]:
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




@app.get("/tendersstatA", tags=["statistic"])
async def tenders_short_statistic(client: AsyncIOMotorClient = Depends(connect_db)) -> List[dict]:
    try:
        collection = await get_collection(client, "test_for_practice", "tenders_test")

        total_count = await collection.count_documents({})

        high_level_total = await collection.count_documents({"analysis.suspicious_level": "high"})


        if total_count != 0:
            high_level_percentage = (high_level_total / total_count) * 100
        else:
            high_level_percentage = 0.0


        pipeline = [
            {
                "$group": {
                    "_id": None,
                    "max_value": {"$max": "$budget_info.amount"}

                }
            },
            {
                "$project": {
                    "_id": 0,
                    "max_value": 1
                }
            }
        ]


        max_value_result = await collection.aggregate(pipeline).to_list(length=None)
        if max_value_result:
            expensivest = max_value_result[0]["max_value"]
        else:
            expensivest = 0

        result = [
            {
                "total": total_count,
                "high_level_percentage": high_level_percentage,
                "expensivest": expensivest
            }
        ]
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving data: {str(e)}")





#diagram statistic not done yet
@app.get("/tenderstatA", tags=["statistic"])
async def get_region_suspicous_statistic(client: AsyncIOMotorClient = Depends(connect_db)) -> List[dict]:
    labels=["Kyiv", "Chernivtsi", "Kharkiv", "Odessa", "Lviv"]

    colors= ["green", "orange", "red"]
    try:
        current_date = datetime.now()

        start_of_month_str = f"{current_date.year}-{current_date.month:02d}-01"
        end_of_month_str = f"{current_date.year}-{current_date.month + 1 if current_date.month < 12 else 1:02d}-01"

        start_date = datetime.strptime(start_of_month_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_of_month_str, "%Y-%m-%d") - timedelta(days=1)

        start_of_month = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_month = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)

        collection = await get_collection(client, "test_for_practice", "tenders_test")

        high_level_total = await collection.count_documents({
            "analysis.suspicious_level": "high",
            "creation_date": {"$gte": start_of_month.isoformat(), "$lte": end_of_month.isoformat()}
        })

        kyiv_high_level_total = await collection.count_documents({
            "analysis.suspicious_level": "high",
            "extended_info.region": "Київська область",
            "creation_date": {"$gte": start_of_month.isoformat(), "$lte": end_of_month.isoformat()}
        })

        chenivtshy_high_level_total = await collection.count_documents({
            "analysis.suspicious_level": "high",
            "extended_info.region": "Чернівецеька область",
            "creation_date": {"$gte": start_of_month.isoformat(), "$lte": end_of_month.isoformat()}
        })

        kharkiv_high_level_total = await collection.count_documents({
            "analysis.suspicious_level": "high",
            "extended_info.region": "Харківська область",
            "creation_date": {"$gte": start_of_month.isoformat(), "$lte": end_of_month.isoformat()}
        })

        odessa_high_level_total = await collection.count_documents({
            "analysis.suspicious_level": "high",
            "extended_info.region": "Одеська область",
            "creation_date": {"$gte": start_of_month.isoformat(), "$lte": end_of_month.isoformat()}
        })

        lviv_high_level_total = await collection.count_documents({
            "analysis.suspicious_level": "high",
            "extended_info.region": "Львівська область",
            "creation_date": {"$gte": start_of_month.isoformat(), "$lte": end_of_month.isoformat()}
        })

        if high_level_total != 0:
            kyiv_high_level_percentage = kyiv_high_level_total / high_level_total * 100
            chenivtshy_high_level_percentage = chenivtshy_high_level_total / high_level_total * 100
            kharkiv_high_level_total_percentage = kharkiv_high_level_total / high_level_total * 100
            odessa_high_level_percentage = odessa_high_level_total / high_level_total * 100
            lviv_high_level_percentage = lviv_high_level_total / high_level_total * 100

        else:
            kyiv_high_level_percentage = 0.0
            chenivtshy_high_level_percentage = 0.0
            kharkiv_high_level_total_percentage = 0.0
            odessa_high_level_percentage = 0.0
            lviv_high_level_percentage = 0.0

        data_high=[
            kyiv_high_level_percentage,
            chenivtshy_high_level_percentage,
            kharkiv_high_level_total_percentage,
            odessa_high_level_percentage,
            lviv_high_level_percentage]

        #medium_level

        medium_level_total = await collection.count_documents({
            "analysis.suspicious_level": "medium",
            "creation_date": {"$gte": start_of_month.isoformat(), "$lte": end_of_month.isoformat()}
        })

        kyiv_medium_level_total = await collection.count_documents({
            "analysis.suspicious_level": "medium",
            "extended_info.region": "Київська область",
            "creation_date": {"$gte": start_of_month.isoformat(), "$lte": end_of_month.isoformat()}
        })

        chenivtshy_medium_level_total = await collection.count_documents({
            "analysis.suspicious_level": "medium",
            "extended_info.region": "Чернівцеька область",
            "creation_date": {"$gte": start_of_month.isoformat(), "$lte": end_of_month.isoformat()}
        })

        kharkiv_medium_level_total = await collection.count_documents({
            "analysis.suspicious_level": "medium",
            "extended_info.region": "Харківська область",
            "creation_date": {"$gte": start_of_month.isoformat(), "$lte": end_of_month.isoformat()}
        })

        odessa_medium_level_total = await collection.count_documents({
            "analysis.suspicious_level": "medium",
            "extended_info.region": "Одеська область",
            "creation_date": {"$gte": start_of_month.isoformat(), "$lte": end_of_month.isoformat()}
        })

        lviv_medium_level_total = await collection.count_documents({
            "analysis.suspicious_level": "medium",
            "extended_info.region": "Львівська область",
            "creation_date": {"$gte": start_of_month.isoformat(), "$lte": end_of_month.isoformat()}
        })

        if medium_level_total != 0:
            kyiv_medium_level_percentage = kyiv_medium_level_total / medium_level_total * 100
            chenivtshy_medium_level_percentage = chenivtshy_medium_level_total / medium_level_total * 100
            kharkiv_medium_level_total_percentage = kharkiv_medium_level_total / medium_level_total * 100
            odessa_medium_level_percentage = odessa_medium_level_total / medium_level_total * 100
            lviv_medium_level_percentage = lviv_medium_level_total / medium_level_total * 100
        else:
            kyiv_medium_level_percentage = 0.0
            chenivtshy_medium_level_percentage = 0.0
            kharkiv_medium_level_total_percentage = 0.0
            odessa_medium_level_percentage = 0.0
            lviv_medium_level_percentage = 0.0

        data_medium = [
            kyiv_medium_level_percentage,
            chenivtshy_medium_level_percentage,
            kharkiv_medium_level_total_percentage,
            odessa_medium_level_percentage,
            lviv_medium_level_percentage
        ]


        low_level_total = await collection.count_documents({
            "analysis.suspicious_level": "low",
            "creation_date": {"$gte": start_of_month.isoformat(), "$lte": end_of_month.isoformat()}
        })

        kyiv_low_level_total = await collection.count_documents({
            "analysis.suspicious_level": "low",
            "extended_info.region": "Київська область",
            "creation_date": {"$gte": start_of_month.isoformat(), "$lte": end_of_month.isoformat()}
        })

        chenivtshy_low_level_total = await collection.count_documents({
            "analysis.suspicious_level": "low",
            "extended_info.region": "Чернівцеька область",
            "creation_date": {"$gte": start_of_month.isoformat(), "$lte": end_of_month.isoformat()}
        })

        kharkiv_low_level_total = await collection.count_documents({
            "analysis.suspicious_level": "low",
            "extended_info.region": "Харківська область",
            "creation_date": {"$gte": start_of_month.isoformat(), "$lte": end_of_month.isoformat()}
        })

        odessa_low_level_total = await collection.count_documents({
            "analysis.suspicious_level": "low",
            "extended_info.region": "Одеська область",
            "creation_date": {"$gte": start_of_month.isoformat(), "$lte": end_of_month.isoformat()}
        })

        lviv_low_level_total = await collection.count_documents({
            "analysis.suspicious_level": "low",
            "extended_info.region": "Львівська область",
            "creation_date": {"$gte": start_of_month.isoformat(), "$lte": end_of_month.isoformat()}
        })

        if low_level_total != 0:
            kyiv_low_level_percentage = kyiv_low_level_total / low_level_total * 100
            chenivtshy_low_level_percentage = chenivtshy_low_level_total / low_level_total * 100
            kharkiv_low_level_total_percentage = kharkiv_low_level_total / low_level_total * 100
            odessa_low_level_percentage = odessa_low_level_total / low_level_total * 100
            lviv_low_level_percentage = lviv_low_level_total / low_level_total * 100
        else:
            kyiv_low_level_percentage = 0.0
            chenivtshy_low_level_percentage = 0.0
            kharkiv_low_level_total_percentage = 0.0
            odessa_low_level_percentage = 0.0
            lviv_low_level_percentage = 0.0

        data_low = [
            kyiv_low_level_percentage,
            chenivtshy_low_level_percentage,
            kharkiv_low_level_total_percentage,
            odessa_low_level_percentage,
            lviv_low_level_percentage
        ]


        return [
            {
                "labels": labels,
                "datasets": [
                    {
                        "label": "Low Risk",
                        "data": data_high,
                        "backgroundColor": colors[0],
                    },
                    {
                        "label": "Medium Risk",
                        "data": data_medium,
                        "backgroundColor": colors[1],
                    },
                    {
                        "label": "High Risk",
                        "data": data_low,
                        "backgroundColor": colors[2],
                    },
                ],
            }
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving data: {str(e)}")




@app.get("/tendersstatC", tags=["statistic"])
async def get_general_suspicous_statistic(client: AsyncIOMotorClient = Depends(connect_db)) -> dict:
    try:


        current_date = datetime.now()


        start_of_month_str = f"{current_date.year}-{current_date.month:02d}-01"
        end_of_month_str = f"{current_date.year}-{current_date.month + 1 if current_date.month < 12 else 1:02d}-01"


        start_date = datetime.strptime(start_of_month_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_of_month_str, "%Y-%m-%d") - timedelta(days=1)


        start_of_month = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_month = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)


        collection = await get_collection(client, "test_for_practice", "tenders_test")

        total_count = await collection.count_documents({"creation_date": {"$gte": start_of_month.isoformat(), "$lte": end_of_month.isoformat()}})
        high_level_total = await collection.count_documents({
            "analysis.suspicious_level": "high",
            "creation_date": {"$gte": start_of_month.isoformat(), "$lte": end_of_month.isoformat()}
        })
        medium_level_total = await collection.count_documents({
            "analysis.suspicious_level": "medium",
            "creation_date": {"$gte": start_of_month.isoformat(), "$lte": end_of_month.isoformat()}
        })
        low_level_total = await collection.count_documents({
            "analysis.suspicious_level": "low",
            "creation_date": {"$gte": start_of_month.isoformat(), "$lte": end_of_month.isoformat()}
        })


        if total_count > 0:
            high_level_percentage = (high_level_total / total_count) * 100
            medium_level_percentage = (medium_level_total / total_count) * 100
            low_level_percentage = (low_level_total / total_count) * 100
        else:
            high_level_percentage = 0.0
            medium_level_percentage = 0.0
            low_level_percentage = 0.0

        return {
            "total": total_count,
            "high_level_percentage": round(high_level_percentage, 2),
            "medium_level_percentage": round(medium_level_percentage, 2),
            "low_level_percentage": round(low_level_percentage, 2)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving data: {str(e)}")


@app.get("/tenders/{tender_id}", tags=["lol"])
async def get_tender(tender_id: str, client: AsyncIOMotorClient = Depends(connect_db)):

    if not ObjectId.is_valid(tender_id):
        raise HTTPException(status_code=400, detail=f"Invalid tender ID format: {tender_id}")

    object_id = ObjectId(tender_id)

    collection = await get_collection(client, "test_for_practice", "tenders_test")

    tender = await collection.find_one({"_id": object_id})
    if not tender:
        raise HTTPException(status_code=404, detail="Tender not found")

    return Tender(**{**tender, "_id": str(tender["_id"])})
































































