import pymongo

MONGO_URI = "mongodb+srv://matiukhinoleksandr:matiukhinoleksandr@aeroport.9ir8trs.mongodb.net/?retryWrites=true&w=majority&appName=AEROPORT"
myclient = pymongo.MongoClient(MONGO_URI)
mydb = myclient["test_for_practice"]
mycol = mydb["tenders_test"]

document_count = mycol.count_documents({})
if document_count > 0:
    print(f"Коллекция содержит {document_count} документов.")
else:
    print("Коллекция пуста.")
