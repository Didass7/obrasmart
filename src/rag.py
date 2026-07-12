import os
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_groq import ChatGroq

# 1. Carregar a chave do Groq que guardaste no ficheiro .env
load_dotenv()

# Configuração de caminhos e modelos
PASTA_VETORIAL = "data/chroma_db"
FICHEIRO_REGRAS = "caderno_de_encargos.txt"

# Usamos um modelo gratuito da HuggingFace que corre 100% local no teu PC para traduzir texto em números (embeddings)
print("A carregar o modelo de Embeddings local (HuggingFace)...")
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

def inicializar_base_vetorial():
    """Lê o caderno de encargos, faz o chunking, gera embeddings e guarda no ChromaDB."""
    if not os.path.exists(FICHEIRO_REGRAS):
        print(f"Ficheiro {FICHEIRO_REGRAS} não encontrado!")
        return

    print("A ler o Caderno de Encargos...")
    with open(FICHEIRO_REGRAS, "r", encoding="utf-8") as f:
        texto_completo = f.read()

    # CHUNKING: O 'RecursiveCharacterTextSplitter' divide o texto de forma inteligente,
    # tentando não cortar frases a meio (olha para parágrafos, pontos e espaços).
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)
    pedacos_texto = text_splitter.split_text(texto_completo)
    print(f"Texto dividido em {len(pedacos_texto)} pedaços (chunks).")

    # GUARDAR NO CHROMADB: Pega nos pedaços, passa-os pelo modelo de embeddings e guarda no disco
    print("A gravar os vetores no ChromaDB...")
    db = Chroma.from_texts(
        texts=pedacos_texto, 
        embedding=embeddings, 
        persist_directory=PASTA_VETORIAL
    )
    print("Base de dados vetorial criada com sucesso!")
    return db

def perguntar_ao_caderno(pergunta: str):
    """Procura o contexto no ChromaDB e pede ao Groq para responder."""
    # 1. Ligar ao ChromaDB existente no disco
    db = Chroma(persist_directory=PASTA_VETORIAL, embedding_function=embeddings)
    
    # 2. RETRIEVAL: Procura no ChromaDB os 2 pedaços de texto mais parecidos com a pergunta
    print(f"🔍 A pesquisar contexto para: '{pergunta}'...")
    documentos_proximos = db.similarity_search(pergunta, k=2)

    # Junta os pedaços encontrados numa única string de contexto
    contexto = "\n".join([doc.page_content for doc in documentos_proximos])
    
    # === ADICIONA ESTAS LINHAS DE DEBUG AQUI: ===
    print("\n📦 [DEBUG] CONTEXTO ENVIADO PARA A IA:")
    print(contexto if contexto else "🚨 ALERTA: O contexto está VAZIO!")
    print("-" * 40 + "\n")
    # ============================================
    
    # 3. Inicializar o Groq (Llama 3) usando a chave do .env
    llm = ChatGroq(model_name="llama-3.1-8b-instant", temperature=0.2)
    
    # 4. PROMPT ENGINEERING: Construímos a instrução exata para a IA não inventar
    prompt = f"""
    És um Engenheiro Fiscalizador de uma obra de construção civil. 
    Responde à pergunta do utilizador utilizando APENAS o contexto fornecido abaixo.
    Se não souberes a resposta com base no contexto, diz explicitamente que a informação não consta no caderno de encargos.

    CONTEXTO DA OBRA:
    {contexto}

    PERGUNTA:
    {pergunta}

    RESPOSTA (em português de Portugal):
    """
    
    # 5. Envia para o Groq e recebe a resposta
    resposta = llm.invoke(prompt)
    return resposta.content

# Bloco de teste rápido
if __name__ == "__main__":
    # Primeiro criamos a base de dados vetorial
    inicializar_base_vetorial()
    
    # Teste de pergunta
    print("\nA testar o cérebro da IA...")
    resposta_teste = perguntar_ao_caderno("Qual é o isolamento planeado para o Piso 2?")
    print(f"\nResposta da IA:\n{resposta_teste}")