import duckdb
import os

def analisar_dados_warehouse():
    caminho_parquet = "data/consolidado.parquet"
    
    if not os.path.exists(caminho_parquet):
        print("O ficheiro Parquet ainda não foi gerado. Corre o processor.py primeiro.")
        return

    # 1. Criar uma ligação ao DuckDB (ele cria um ficheiro de base de dados local automático)
    con = duckdb.connect("data/obrasmart.db")

    print("Ligação ao DuckDB estabelecida com sucesso!")

    # Vamos fazer uma consulta para ver quantas atividades temos por cada nível de prioridade.
    
    query = """
        SELECT 
            prioridade_revisao, 
            COUNT(*) as total_atividades,
            AVG(progresso_atual) as progresso_medio
        FROM 'data/consolidado.parquet'
        GROUP BY prioridade_revisao
    """
    
    # 2. Executar a query e transformar o resultado de volta para o formato do Pandas para ver no terminal
    resultado = con.execute(query).df()
    
    print("\nResumo Analítico do Warehouse (via SQL):")
    print(resultado)
    
    # Fechar a ligação à base de dados
    con.close()

if __name__ == "__main__":
    analisar_dados_warehouse()