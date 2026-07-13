import streamlit as st
import requests

# Configuração da página do Streamlit
st.set_page_config(page_title="SmartSite Analytics", page_icon="🏗️", layout="wide")

st.title("🏗️ Obras Smart — Painel de Controlo da Obra")
st.markdown("Monitorização de progresso por IA e análise de Caderno de Encargos em tempo real.")

# URLs da tua API FastAPI
URL_ALERTAS = "http://127.0.0.1:8000/alertas"
URL_CHAT = "http://127.0.0.1:8000/chat"

# Criar duas colunas na interface: Esquerda para Alertas, Direita para o Chat de IA
col1, col2 = st.columns([1, 1])

with col1:
    st.header("Alertas Críticos da Obra")
    try:
        # Faz o pedido à rota /alertas do FastAPI
        resposta = requests.get(URL_ALERTAS).json()
        alertas = resposta.get("alertas", [])
        
        if alertas:
            # Exibe os alertas numa tabela bonita do Streamlit
            st.dataframe(alertas, use_container_width=True)
        else:
            st.success("✅ Nenhuma atividade em atraso crítico de momento!")
    except Exception:
        st.error("❌ Não foi possível conectar à API. Garante que o FastAPI está a correr!")

with col2:
    st.header("🤖 Assistente de IA do Engenheiro")
    
    # Caixa de texto onde o utilizador digita a pergunta
    pergunta = st.text_input("Faz uma pergunta sobre o estado ou regras da obra:")
    
if st.button("Enviar Pergunta") and pergunta:
        with st.spinner("🤖 A analisar dados e caderno de encargos..."):
            try:
                # 1. Faz o pedido à API
                resposta_chat = requests.get(URL_CHAT, params={"pergunta": pergunta}).json()
                
                # 2. Exibe a resposta correta usando a chave detetada no debug
                st.chat_message("assistant").write(resposta_chat.get("resposta_ia"))
                
            except Exception as e:
                st.error(f"❌ Erro ao comunicar com o motor de IA: {e}")