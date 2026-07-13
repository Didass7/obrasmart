# 🏗️ Obras Smart — Plataforma de RAG Híbrido para Gestão de Obras

O **Obras Smart** é uma plataforma inteligente de apoio à decisão para a engenharia civil. O sistema recolhe dados métricos em tempo real de uma obra (atividades, pisos, progressos), consolida-os num pipeline analítico e utiliza um motor de **RAG Híbrido (Retrieval-Augmented Generation)** para cruzar esses dados com as regras textuais de um Caderno de Encargos, respondendo a perguntas complexas sem alucinações.

---

## 🏗️ Arquitetura do Sistema e Fluxo de Dados

O projeto foi desenhado seguindo uma arquitetura moderna de três camadas:

1. **Camada de Engenharia de Dados (Ingestão e Armazenamento):**
   * Um simulador gera eventos contínuos em JSON.
   * Um pipeline em **Pandas** processa, limpa e calcula prioridades de revisão com base no progresso.
   * Os dados são guardados em formato colunar **Parquet** de alta performance.
   * O **DuckDB** atua como o Data Warehouse analítico, executando queries SQL ultra-rápidas e deduplicando o histórico em tempo real.

2. **Camada de Inteligência Artificial (AI Engineering):**
   * O Caderno de Encargos (texto não estruturado) passa por um processo de *chunking* inteligente.
   * Os vetores são gerados localmente através de embeddings da **HuggingFace** (`all-MiniLM-L6-v2`) e indexados na base de dados vetorial **ChromaDB**.
   * O motor de RAG Híbrido funde o contexto do documento com o estado analítico do DuckDB e envia-o para o LLM **Llama 3.1** via **Groq API**.

3. **Camada de Aplicação (API e Frontend):**
   * O **FastAPI** serve os endpoints de alertas analíticos e a rota do chat de IA.
   * O **Streamlit** oferece uma interface visual intuitiva com um dashboard de alertas críticos e um chat interativo.

---

## Tecnologias Utilizadas

* **Linguagem:** Python 3.11+
* **Data & Analytics:** Pandas, PyArrow (Parquet), DuckDB (SQL)
* **AI & RAG:** LangChain, ChromaDB, HuggingFace Embeddings, Groq API (Llama 3.1)
* **Application Layer:** FastAPI, Uvicorn, Streamlit, Requests, Python-Dotenv

---

## Como Executar o Projeto

### 1. Pré-requisitos
Garante que tens o Python instalado e uma chave de API gratuita criada em [console.groq.com](https://console.groq.com/).

### 2. Configuração do Ambiente
Clona o repositório, cria o teu ambiente virtual e instala as dependências:
```bash
python -m venv .venv
source .venv/Scripts/activate  # No Windows: .\.venv\Scripts\activate
pip install -r requirements.txt
```

Cria um ficheiro `.env` na raiz do projeto e adiciona a tua chave do Groq:
```text
GROQ_API_KEY=gsk_tua_chave_aqui
```

### 3. Execução dos Componentes (Passo a Passo)

Para colocar o ecossistema a funcionar, executa os scripts na seguinte ordem:

* **Gerar dados da obra (Deixa correr 10 segundos e para com Ctrl+C):**
  ```bash
  python src/generator.py
  ```
* **Processar e consolidar os dados no Data Warehouse:**
  ```bash
  python src/processor.py
  ```
* **Iniciar o Backend (API FastAPI):**
  ```bash
  python -m uvicorn src.api:app --reload
  ```
* **Iniciar o Frontend (Interface Streamlit - Executar num novo terminal):**
  ```bash
  streamlit run src/app.py
  ```

Abra o navegador no endereço indicado pelo Streamlit (normalmente `http://localhost:8501`) para interagir com o painel!