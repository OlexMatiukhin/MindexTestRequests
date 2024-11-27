import asyncio
from datetime import datetime, timedelta

import pytz
from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorClient

from motor.motor_asyncio import AsyncIOMotorClient
from typing_extensions import List

from models.tenderModels import Tender

MONGO_URI = "mongodb://AdminMASI:admin1488%40%40%40%40%40@129.151.207.119:27017/"
client = AsyncIOMotorClient(MONGO_URI)
db = client["test_for_practice"]
collection = db["tenders_test"]

async def main():
    total_count = await collection.count_documents({})  # Нужно использовать await для асинхронной операции
    high_level_total = await collection.count_documents({"analysis.suspicious_level": "high"})  # Используем await

    if total_count != 0:
        high_level_percentage = (high_level_total / total_count) * 100
    else:
        high_level_percentage = 0.0


    result = [
        {
            "total": total_count,
            "high_level_percentage": high_level_percentage,
           # "expensivest": expensivest
        }
    ]
    print(result)

async def big_statistic():


        current_date = datetime.now()


        start_of_month_str = f"{current_date.year}-{current_date.month:02d}-01"
        end_of_month_str = f"{current_date.year}-{current_date.month + 1 if current_date.month < 12 else 1:02d}-01"


        start_date = datetime.strptime(start_of_month_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_of_month_str, "%Y-%m-%d") - timedelta(days=1)


        start_of_month = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_month = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)

        print("Start of Month:", start_of_month)
        print("End of Month:", end_of_month)




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
            "extended_info.region": "Чернівецька область",
            "creation_date": {"$gte": start_of_month, "$lte": end_of_month}
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


        print("Total high level:", high_level_total)
        print("Kyiv high level:", kyiv_high_level_total)
        print("Chernivtsi high level:", chenivtshy_high_level_total)
        print("Kharkiv high level:", kharkiv_high_level_total)
        print("Odessa high level:", odessa_high_level_total)
        print("Lviv high level:", lviv_high_level_total)

        if high_level_total != 0:
            kyiv_high_level_percentage = kyiv_high_level_total / high_level_total * 100
            chenivtshy_high_level_percentage = chenivtshy_high_level_total / high_level_total * 100
            kharkiv_high_level_percentage = kharkiv_high_level_total / high_level_total * 100
            odessa_high_level_percentage = odessa_high_level_total / high_level_total * 100
            lviv_high_level_percentage = lviv_high_level_total / high_level_total * 100
        else:
            kyiv_high_level_percentage = 0.0
            chenivtshy_high_level_percentage = 0.0
            kharkiv_high_level_percentage = 0.0
            odessa_high_level_percentage = 0.0
            lviv_high_level_percentage = 0.0

        data_high = [
            kyiv_high_level_percentage,
            chenivtshy_high_level_percentage,
            kharkiv_high_level_percentage,
            odessa_high_level_percentage,
            lviv_high_level_percentage
        ]

        return data_high


async def test_get_tenders(
)-> List[Tender]:
    query = {}



    cursor = collection.find().skip(0).limit(100)
    tenders = await cursor.to_list(length=100)


    if not tenders:
        raise HTTPException(status_code=404, detail="No tenders found.")

    tenders_result= [Tender(**{**tender, "_id": str(tender["_id"])}) for tender in tenders]

    print(tenders_result)



if __name__ == "__main__":
    asyncio.run(big_statistic())


