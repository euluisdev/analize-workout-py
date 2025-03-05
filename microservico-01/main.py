from fastapi import FastAPI, Depends, HTTPException, Request
from pymongo import MongoClient
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64 
import os
import jwt
import plotly.graph_objects as go
from datetime import datetime


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

    weekly_counts = df["week"].value_counts().sort_index().astype(int)

    current_week = datetime.now().strftime('%Y-%U')
    
    # Criar gráfico com Plotly
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=weekly_counts.index.tolist(), 
        y=weekly_counts.values.astype(int), 
        marker_color="gold",
        opacity=0.7
    ))

    fig.update_layout(
        title=f"Frequência de Treinos por Semana - Semana Atual: {current_week}",
        xaxis_title="Semana",
        yaxis_title="Quantidade de Treinos",
        template="plotly_dark", 
        xaxis=dict(type="category"), 
         yaxis=dict(tickmode="linear", tick0=0, dtick=1)
    )

    # Retornar o JSON do gráfico para o frontend renderizar
    return fig.to_json()







