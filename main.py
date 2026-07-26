import os
import psycopg
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="API da SmartBarrera")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class Exame(BaseModel):
    """Um exame de qualidade da água enviado pela SmartBarrera."""
    ph: float
    turbidez: int
    tds: int
    temperatura: float


def conectar_banco():
    """Abre conexão com o Neon usando DATABASE_URL (pooler)."""
    return psycopg.connect(os.environ["DATABASE_URL"])


@app.get("/api")
def read_root():
    return {"ok": True}


@app.post("/leituras")
def salvar_exame(exame: Exame):
    with conectar_banco() as conexao:
        with conexao.cursor() as cursor:
            cursor.execute(
                "INSERT INTO leituras (ph, turbidez, tds, temperatura) "
                "VALUES (%s, %s, %s, %s)",
                (exame.ph, exame.turbidez, exame.tds, exame.temperatura),
            )
        conexao.commit()
    return {"mensagem": "Exame guardado com sucesso!"}


@app.get("/leituras")
def listar_exames():
    with conectar_banco() as conexao:
        with conexao.cursor() as cursor:
            cursor.execute(
                "SELECT ph, turbidez, tds, temperatura, criado_em "
                "FROM leituras ORDER BY criado_em DESC"
            )
            linhas = cursor.fetchall()
    return [
        {
            "ph": l[0], "turbidez": l[1], "tds": l[2],
            "temperatura": l[3], "criado_em": l[4].isoformat(),
        }
        for l in linhas
    ]
