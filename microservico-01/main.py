from fastapi import FastAPI, Depends, HTTPException, Request
from pymongo import MongoClient
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64 
import os
import jwt
from dotenv import load_dotenv
from bson import ObjectId
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()
app = FastAPI() 

origins=[
    "http://localhost:3000",  
    "http://127.0.0.1:3000", 
    "https://bestfitclass.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, 
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Set-Cookie", "Authorization"],
    expose_headers=["Set-Cookie"]
)

URI = os.getenv("MONGODB_URI")
client = MongoClient(URI)
db = client["BestFitData"]
workouts_collection = db["workouts"]

jwtSecret = os.getenv("JWT_SECRET")
ALGORITHM = "HS256"

def verify_token(req: Request):
    token = req.cookies.get("authToken", None)
 
    if not token:
        raise HTTPException(status_code=401, detail="Token não fornecido")
    
    try:
        decoded = jwt.decode(token, jwtSecret, algorithms=[ALGORITHM])
        print("Token decodificado com sucesso:", decoded)
        return decoded["email"]
        
    except Exception as e:
        print("Erro específico na verificação:", str(e))
        raise HTTPException(status_code=401, detail=f"Token inválido: {str(e)}")

@app.get("/")
def read_root():
    return {"message": "Microserviço está rodando!"}

@app.get("/workouts")
async def get_workouts(email: str = Depends(verify_token), req: Request = None):

    user = db["users"].find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    user_id = user["_id"] 

    workouts = list(workouts_collection.find({"userId": ObjectId(user_id)}))

    if not workouts:
        return {"message": "Nenhum treino encontrado para este usuário."}

    # dataframe
    df = pd.DataFrame(workouts)
    df["date"] = pd.to_datetime(df["date"])
    df["week"] = df["date"].dt.strftime('%Y-%U')

    weekly_counts = df["week"].value_counts().sort_index()
    
    # Criar o gráfico
    plt.figure(figsize=(8, 5))
    weekly_counts.plot(kind="bar", color="yellow", alpha=0.7)
    plt.title(f"Frequência de Treinos por Semana - Usuário {user_id}")
    plt.xlabel("Semana")
    plt.ylabel("Quantidade de Treinos")
    plt.xticks(rotation=45)

    img = io.BytesIO()
    plt.savefig(img, format="png")
    plt.close()
    img_base64 = base64.b64encode(img.getvalue()).decode("utf-8")


    return {"image": f"data:image/png;base64,{img_base64}"}







