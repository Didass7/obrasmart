import os
import duckdb
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_groq import ChatGroq

load_dotenv()

DIRETORIO_ATUAL = os.path.dirname(os.path.abspath(__file__))
RAIZ_PROJETO = os.path.dirname(DIRETORIO_ATUAL)

PASTA_VETORIAL = os.path.join(RAIZ_PROJETO, "data", "chroma_db")
FICHEIRO_REGRAS = os.path.join(RAIZ_PROJETO, "caderno_de_encargos.txt")
CAMINHO_PARQUET = os.path.join(RAIZ_PROJETO, "data", "consolidado.parquet")

print("A carregar o modelo de Embeddings local (HuggingFace)...")
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

def inicializar_base_vetorial():
    """Lê o caderno de encargos e grava no ChromaDB (Mantém-se igual)."""
    if not os.path.exists(FICHEIRO_REGRAS):
        return
    with open(FICHEIRO_REGRAS, "r", encoding="utf-8") as f:
        texto_completo = f.read()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)
    pedacos_texto = text_splitter.split_text(texto_completo)
    db = Chroma.from_texts(texts=pedacos_texto, embedding=embeddings, persist_directory=PASTA_VETORIAL)
    return db

def obter_status_tempo_real():
    if not os.path.exists(CAMINHO_PARQUET):
        return "Nenhum dado de progresso em tempo real disponível ainda."
    
    con = duckdb.connect(os.path.join(RAIZ_PROJETO, "data", "obrasmart.db"))
    
    # Traz apenas o estado mais recente de cada atividade da obra
    query = """
        SELECT piso, zona, atividade, progresso_atual, prioridade_revisao 
        FROM 'data/consolidado.parquet'
        QUALIFY ROW_NUMBER() OVER (
            PARTITION BY id_obra, piso, zona, atividade 
            ORDER BY timestamp DESC
        ) = 1
    """
    linhas = con.execute(query).fetchall()
    con.close()
    
    texto_status = ""
    for l in linhas:
        texto_status += f"- {l[2]} no {l[0]} ({l[1]}): Progresso atual de {l[3]}%. Prioridade de Revisão: {l[4]}.\n"
    return texto_status

def perguntar_ao_caderno(pergunta: str):
    """Procura o contexto no ChromaDB + Dados do DuckDB e envia para o Groq."""
    db = Chroma(persist_directory=PASTA_VETORIAL, embedding_function=embeddings)
    documentos_proximos = db.similarity_search(pergunta, k=2)
    contexto_regras = "\n".join([doc.page_content for doc in documentos_proximos])
    
    # 1. Procurar os dados analíticos gerados pelo teu pipeline
    contexto_dados_live = obter_status_tempo_real()
    
    llm = ChatGroq(model_name="llama-3.1-8b-instant", temperature=0.2)
    
    # 2. PROMPT HÍBRIDO: Entregamos as regras E o estado atual dos dados à IA
    prompt = f"""
    És um Engenheiro Fiscalizador de uma obra de construção civil. 
    Responde à pergunta do utilizador cruzando as REGRAS DO CADERNO DE ENCARGOS com o ESTADO ATUAL EM TEMPO REAL.

    [DOCUMENTO] REGRAS DO CADERNO DE ENCARGOS:
    {contexto_regras}

    [BASE DE DADOS] ESTADO ATUAL DA OBRA EM TEMPO REAL:
    {contexto_dados_live}

    PERGUNTA DO UTILIZADOR:
    {pergunta}

    RESPOSTA COMPLETA (Cruza os dados com as regras se necessário. Em português de Portugal):
    """
    
    resposta = llm.invoke(prompt)
    return resposta.content

if __name__ == "__main__":
    inicializar_base_vetorial()
    # Teste rápido cruzando dados
    print(perguntar_ao_caderno("O isolamento do Piso 2 cumpre as regras e está a avançar bem?"))