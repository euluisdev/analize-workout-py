from fastapi import FastAPI
from pymongo import MongoClient
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64 
import os
from dotenv import load_dotenv
from bson import ObjectId

load_dotenv()

app = FastAPI() 

# Conect MongoDB
URI = os.getenv("MONGODB_URI")
client = MongoClient(URI)
db = client["BestFitData"]
workouts_collection = db["workouts"]

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

print("MongoDB URI:", URI)


@app.get("/workouts/{user_id}")
async def get_workouts(user_id: str):
    # Converte o user_id para ObjectId
    try:
        user_id_object = ObjectId(user_id)
    except Exception as e:
        return {"message": f"Erro ao converter user_id: {e}"}
    
    workouts = list(workouts_collection.find({"userId": user_id_object}))
    
    if not workouts:
        return {"message": "Nenhum treino encontrado para este usuário."}
    
    workouts_clean = [
        {"nome": workout["nome"], "muscleGroups": workout["muscleGroups"], "date": workout["date"], "description": workout["description"]}
        for workout in workouts
    ]
    
    return {"workouts": workouts_clean}


