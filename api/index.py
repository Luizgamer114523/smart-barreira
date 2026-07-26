import os
import psycopg2
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="API da SmartBarrera")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)
class Item(BaseModel):
    """um exame de qualidade da água enviado pela smartbarrera."""
    ph: float
    turbidez: int
    tds: int
    temperatura: float

def conectar_banco():
    """Abre uma conexao com o banco Neon usando a variavel DATABASE_URL."""
    return psycopg2.connect("postgresql://neondb_owner:npg_43BetITFXaGS@ep-quiet-sea-axyyb7bt.c-4.us-east-2.aws.neon.tech/neondb?sslmode=require")

@app.get("/api")
def read_root():
    return {"ok": True}

@app.post("/leituras")
def salvar_exame(exame: Exame):
    """Recebe um exame da AquaBarreira e guarda no banco de dados."""
    conexao = conectar_banco()
    cursor = conexao.cursor()
    cursor.execute(
        """
        INSERT INTO leituras (ph, turbidez, tds, temperatura)
        VALUES (%s, %s, %s, %s)
        """,
        (exame.ph, exame.turbidez, exame.tds, exame.temperatura),
    )
    conexao.commit()
    cursor.close()
    conexao.close()
    return {"mensagem": "Exame guardado com sucesso!"}

@app.get("/leituras")
def listar_exames():
    """Devolve todos os exames guardados, do mais novo para o mais antigo."""
    conexao = conectar_banco()
    cursor = conexao.cursor()
    cursor.execute(
        """
        SELECT ph, turbidez, tds, temperatura, criado_em
        FROM leituras
        ORDER BY criado_em DESC
        """
    )
    linhas = cursor.fetchall()
    cursor.close()
    conexao.close()
    return [
        {
            "ph": linha[0], "turbidez": linha[1], "tds": linha[2],
            "temperatura": linha[3], "criado_em": linha[4].isoformat(),
        }
        for linha in linhas
    ]
    
    # postgresql://neondb_owner:npg_43BetITFXaGS@ep-quiet-sea-axyyb7bt.c-4.us-east-2.aws.neon.tech/neondb?sslmode=require
