from fastapi import FastAPI
from pymongo import MongoClient
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64 

app = FastAPI() 

# Conect MongoDB
URI = 'MONGODB_URI'
client = MongoClient(URI)
db = client["BestFitData"]
workouts_collection = db["workouts"]



