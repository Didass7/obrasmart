import os
import json
import pandas as pd

def processar_dados_obra():
    pasta_data = "data"
    eventos = []

    # 1. Ler todos os ficheiros JSON da pasta
    for ficheiro in os.listdir(pasta_data):
        if ficheiro.endswith(".json"):
            caminho_completo = os.path.join(pasta_data, ficheiro)
            with open(caminho_completo, "r", encoding="utf-8") as f:
                dados = json.load(f)
                eventos.append(dados)

    if not eventos:
        print("Nenhum dado encontrado para processar.")
        return

    # 2. Converter a lista de eventos num DataFrame do Pandas
    df = pd.DataFrame(eventos)
    
    print("Dados brutos carregados no Pandas:")
    print(df.head()) # Mostra as primeiras linhas no terminal

    # 3. Criar a métrica 'prioridade_revisao' para CADA linha
    # O .apply() vai correr a linha inteira e aplicar o IF/ELSE a cada registo
    df['prioridade_revisao'] = df['progresso_atual'].apply(
        lambda x: 'ALTA' if x < 40 else 'NORMAL'
    )
    
    print("\nDados processados com a nova coluna de prioridade:")
    print(df[['atividade', 'progresso_atual', 'prioridade_revisao']].head())

    # 4. Guardar o resultado final num ficheiro Parquet compactado
    # O index=False evita que o Pandas grave uma coluna extra com os números das linhas
    df.to_parquet("data/consolidado.parquet", index=False)
    print("\nDados consolidados gravados em 'data/consolidado.parquet'")

if __name__ == "__main__":
    processar_dados_obra()