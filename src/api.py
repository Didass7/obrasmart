from fastapi import FastAPI
import duckdb
from src.rag import perguntar_ao_caderno

# Inicializa a aplicação FastAPI
app = FastAPI(title="SmartSite-Analytics API")

@app.get("/")
def home():
    """Rota raiz para verificar se a API está online."""
    return {"status": "online", "projeto": "SmartSite-Analytics"}

# --- O TEU DESAFIO ---
# Precisamos de criar a rota '/alertas'. 
# Ela deve abrir a ligação ao DuckDB ('data/obrasmart.db'), 
# fazer um SELECT para trazer todas as colunas onde a 'prioridade_revisao' seja igual a 'ALTA',
# converter para dicionário e devolver.

@app.get("/alertas")
def obtener_alertas():
    con = duckdb.connect("data/obrasmart.db")
    
    # Query corrigida e limpa (sem linhas duplicadas ou comentários perdidos)
    query = """
        SELECT timestamp, piso, zona, atividade, progresso_atual, prioridade_revisao, responsavel
        FROM 'data/consolidado.parquet'
        QUALIFY ROW_NUMBER() OVER (
            PARTITION BY id_obra, piso, zona, atividade 
            ORDER BY timestamp DESC
        ) = 1
    """
    
    df = con.execute(query).df()
    resultado = df[df['prioridade_revisao'] == 'ALTA'].to_dict(orient="records")
    con.close()
    return {"alertas": resultado}

@app.get("/chat")
def chat_obra(pergunta: str):
    """Rota que recebe uma pergunta por texto e responde usando o RAG do Groq"""
    resposta_ia = perguntar_ao_caderno(pergunta)

    return {
        "pergunta": pergunta,
        "resposta_ia": resposta_ia
    }