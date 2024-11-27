import asyncio
from datetime import datetime, timedelta

from motor.motor_asyncio import AsyncIOMotorClient

from motor.motor_asyncio import AsyncIOMotorClient


MONGO_URI = "mongodb+srv://matiukhinoleksandr:matiukhinoleksandr@aeroport.9ir8trs.mongodb.net/?retryWrites=true&w=majority&appName=AEROPORT"
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



    #max_value_result = await collection.aggregate(pipeline).to_list(length=None)  # Используем await

    #if max_value_result:
       # expensivest = max_value_result[0]["max_value"]
    #else:
      #  expensivest = 0

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

    start_of_month = datetime(current_date.year, current_date.month, 1)

    end_of_month = datetime(current_date.year, current_date.month + 1, 1) - timedelta(days=1)

    high_level_total = await collection.count_documents({
        "analysis.suspicious_level": "high"

    })

    kyiv_high_level_total = await collection.count_documents({
        "analysis.suspicious_level": "high",
        "extended_info.region": "Київська область",

    })

    chenivtshy_high_level_total = await collection.count_documents({
        "analysis.suspicious_level": "high",
        "extended_info.region": "Чернівецеька область",

    })

    kharkiv_high_level_total = await collection.count_documents({
        "analysis.suspicious_level": "high",
        "extended_info.region": "Харківська область",

    })

    odessa_high_level_total = await collection.count_documents({
        "analysis.suspicious_level": "high",
        "extended_info.region": "Одеська область",
    })

    lviv_high_level_total = await collection.count_documents({
        "analysis.suspicious_level": "high",
        "extended_info.region": "Львівська область",

    })

    print(high_level_total)
    print(kyiv_high_level_total)
    print(chenivtshy_high_level_total)
    print(kharkiv_high_level_total)
    print(odessa_high_level_total)
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

    data_high = [
        kyiv_high_level_percentage,
        chenivtshy_high_level_percentage,
        kharkiv_high_level_total_percentage,
        odessa_high_level_percentage,
        lviv_high_level_percentage]





if __name__ == "__main__":
    asyncio.run(big_statistic())


