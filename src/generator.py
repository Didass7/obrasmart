import json
import random
import time
from datetime import datetime
import os

PISOS = ["Piso 1", "Piso 2", "Piso 3"]
ZONAS = ["Zona Norte", "Zona Sul", "Zona Centro"]
ATIVIDADES = ["Isolamento Térmico", "Pintura", "Instalação Elétrica", "Betonagem"]

def gerar_dados_evento():
    dados = {
        "timestamp": datetime.now().isoformat(),
        "id_obra": "OBRA-LISBOA-01",
        "piso": random.choice(PISOS),          # Escolhe um item da lista PISOS
        "zona": random.choice(ZONAS),          # Escolhe um item da lista ZONAS
        "atividade": random.choice(ATIVIDADES),  # Escolhe um item da lista ATIVIDADES
        "progresso_atual": random.randint(0, 100), # Gera um número inteiro entre 0 e 100
        "responsavel": random.choice(["Eng. Silva", "Arq. Costa", "Téc. Martins"])
    }
    return dados

def simular_fluxo_obra():
    """Gera e grava dados continuamente na pasta 'data'."""
    print("Simulador iniciado. A gerar dados a cada 2 segundos... (Prime CTRL+C para parar)")

    if not os.path.exists("data"):
        os.makedirs("data")

    while True:
        dados = gerar_dados_evento()
        
        # 2. Cria um nome de ficheiro único usando um timestamp numérico (ex: evento_1719912345.json)
        timestamp_unix = int(time.time())
        nome_ficheiro = f"data/evento_{timestamp_unix}_{random.randint(100,999)}.json"
        
        # 3. Abre o ficheiro único e grava lá dentro o dicionário 'dados' completo
        with open(nome_ficheiro, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=4, ensure_ascii=False)
            print(f"Ficheiro guardado: {nome_ficheiro} -> {dados['atividade']} no {dados['piso']}")
        
        # 4. Espera 2 segundos fora do 'with' antes de voltar a repetir o ciclo
        time.sleep(2)

if __name__ == "__main__":
    simular_fluxo_obra()