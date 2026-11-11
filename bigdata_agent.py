import os
import duckdb
import polars as pl
import numpy as np
import ollama

ARQUIVO_BIGDATA = "transacoes_bigdata.parquet"
MODELO_LLM = "qwen2.5-coder:1.5b" # Ou llama3.1:8b se tiver máquina mais potente

def gerar_massa_bigdata():
    """Gera 1 milhão de linhas em Parquet simulando logs de transações com fraudes/outliers."""
    if os.path.exists(ARQUIVO_BIGDATA):
        print(f"📦 Base '{ARQUIVO_BIGDATA}' já existe.")
        return

    print("⏳ Gerando 1.000.000 de registros particionados em Parquet...")
    n_rows = 1_000_000
    
    # Criando colunas de forma vetorizada com Polars
    np.random.seed(42)
    df = pl.DataFrame({
        "transaction_id": np.arange(1, n_rows + 1),
        "user_id": np.random.randint(1000, 50000, size=n_rows),
        "merchant_category": np.random.choice(["retail", "travel", "groceries", "electronics", "crypto"], size=n_rows),
        "amount": np.round(np.random.exponential(scale=50.0, size=n_rows), 2),
        "is_international": np.random.choice([0, 1], p=[0.95, 0.05], size=n_rows)
    })
    
    # Injeta fraudes e outliers bizarros (para o agente caçar)
    fraude_indices = np.random.choice(n_rows, size=15, replace=False)
    # Valores exorbitantes em cripto de madrugada
    df = df.with_columns(
        pl.when(pl.col("transaction_id").is_in(fraude_indices))
        .then(pl.lit(98500.00))
        .otherwise(pl.col("amount"))
        .alias("amount")
    )
    
    df.write_parquet(ARQUIVO_BIGDATA)
    print(f"✅ Arquivo Parquet gerado com sucesso! Tamanho: {os.path.getsize(ARQUIVO_BIGDATA) / (1024*1024):.2f} MB\n")

def executar_query_duckdb(sql_query: str) -> str:
    """Ferramenta para o agente: Executa SQL diretamente no Parquet usando DuckDB."""
    con = duckdb.connect()
    # Registra o arquivo Parquet como uma tabela relacional virtual
    con.execute(f"CREATE VIEW transacoes AS SELECT * FROM read_parquet('{ARQUIVO_BIGDATA}')")
    try:
        resultado = con.execute(sql_query).df()
        return resultado.to_string(index=False)
    except Exception as e:
        return f"Erro na sintaxe SQL: {str(e)}"

def agente_investigador():
    """Agente que inspeciona a base de dados, formula análises e descobre padrões de risco."""
    print("🚀 [SISTEMA] Iniciando Agente Investigador de Big Data com DuckDB...")
    
    # Passo 1: O Agente extrai as métricas de primeira ordem via DuckDB
    print("📊 [AGENTE] Computando estatísticas de agregação sobre 1.000.000 de linhas...")
    stats_query = """
        SELECT 
            merchant_category,
            COUNT(*) as total_transacoes,
            ROUND(AVG(amount), 2) as ticket_medio,
            ROUND(MAX(amount), 2) as valor_maximo,
            ROUND(STDDEV(amount), 2) as desvio_padrao
        FROM transacoes
        GROUP BY merchant_category
        ORDER BY valor_maximo DESC
    """
    resumo_estatistico = executar_query_duckdb(stats_query)
    print(resumo_estatistico)
    print("\n------------------------------------------------------------\n")
    
    # Passo 2: O Agente recebe o resultado do Big Data e formula a hipótese de anomalia
    prompt_investigacao = f"""
    Você é um Engenheiro de Dados Sênior e Especialista em Fraude.
    Analisamos uma base de 1 milhão de transações em Parquet. Aqui estão os dados agregados:

    {resumo_estatistico}

    Tarefa:
    1. Identifique qual categoria apresenta o comportamento mais anômalo e cite os valores discrepantes.
    2. Explique brevemente o risco associado a essa anomalia para o negócio.
    
    Responda em português, de forma concisa e técnica (máximo 4 linhas).
    """
    
    print("🧠 [AGENTE] Analisando outliers e formulando hipótese de fraude (Ollama)...")
    resposta = ollama.chat(model=MODELO_LLM, messages=[
        {'role': 'user', 'content': prompt_investigacao}
    ])
    
    analise = resposta['message']['content']
    print("\n================ DIAGNÓSTICO DO AGENTE ================\n")
    print(analise)
    print("\n=======================================================\n")
    
    # Passo 3: Execução real da query analítica no DuckDB para isolar as transações fraudulentas
    print("🔍 [SISTEMA] Executando query analítica no DuckDB para isolar as anomalias...")
    query_isolamento = """
        WITH metricas AS (
            SELECT 
                AVG(amount) as media,
                STDDEV(amount) as desvio
            FROM transacoes
            WHERE merchant_category = 'crypto'
        )
        SELECT 
            t.transaction_id,
            t.user_id,
            t.merchant_category,
            t.amount,
            t.is_international
        FROM transacoes t, metricas m
        WHERE t.merchant_category = 'crypto'
          AND t.amount > (m.media + 3 * m.desvio)
        ORDER BY t.amount DESC
        LIMIT 10;
    """
    fraudes_detectadas = executar_query_duckdb(query_isolamento)
    print("\n🚨 [ALERTA] Top 10 Transações Anômalas Isoladas:")
    print(fraudes_detectadas)
    print("\n------------------------------------------------------------\n")
    
    # Passo 4: Salva o parecer técnico consolidado em Markdown
    with open("auditoria_anomalias.md", "w", encoding="utf-8") as f:
        f.write("# Relatório de Auditoria de Big Data\n\n")
        f.write(f"Dataset: `{ARQUIVO_BIGDATA}` (1.000.000 de registros)\n\n")
        f.write("## 1. Estatísticas Agregadas (DuckDB)\n```\n" + resumo_estatistico + "\n```\n\n")
        f.write("## 2. Diagnóstico do Agente Autônomo (LLM)\n" + analise + "\n\n")
        f.write("## 3. Evidências: Registros Isolados (> 3 Desvios Padrão)\n```\n" + fraudes_detectadas + "\n```\n")
        
    print("📁 [SISTEMA] Relatório completo salvo em 'auditoria_anomalias.md'!")

if __name__ == "__main__":
    gerar_massa_bigdata()
    agente_investigador()