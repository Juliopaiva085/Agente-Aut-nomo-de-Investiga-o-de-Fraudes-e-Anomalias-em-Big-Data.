# 🕵️‍♂️ Agente Autônomo de Investigação de Fraudes e Anomalias em Big Data

Pipeline analítico de alta performance voltado para detecção e auditoria de anomalias em escala de **Big Data** (milhões de registros). O projeto orquestra **DuckDB** e **Polars** para computação colunar ultrarrápida e integra um agente **LLM local (Ollama)** para formulação de hipóteses estatísticas e geração de relatórios de auditoria automatizados — operando 100% *air-gapped* (sem envio de dados para APIs externas).

---

## 🏗️ Arquitetura da Solução

Em arquiteturas modernas de dados, modelos de linguagem não processam arquivos massivos linha a linha. O pipeline adota um padrão desacoplado:

1. **Storage Colunar:** Armazenamento em arquivos compactados `.parquet`.
2. **Engine Analítica (DuckDB):** Execução de agregações vetoriais e consultas OLAP diretamente no disco/memória em frações de segundo.
3. **Agente Analítico (Ollama / Qwen2.5-Coder):** Avaliação dos resultados estatísticos, inferência de risco e geração automatizada de relatórios executivos de Root Cause Analysis (RCA).

```text
[ 1.000.000+ Transações Parquet ]
                │
                ▼
       [ DuckDB (Engine C++) ] ◄──── Agregações estatísticas & filtros out-of-core
                │
                ▼
      [ Métricas Agregadas ]
                │
                ▼
   [ Agente Ollama (Local) ] ─────► Raciocínio estatístico & hipótese de fraude
                │
                ▼
   [ auditoria_anomalias.md ] ────► Relatório técnico com evidências isoladas
```

---

## 🛠️ Tecnologias e Ferramentas

* **Python 3.10+**
* **Polars:** Geração e manipulação vetorizada de dados estruturados.
* **DuckDB:** Consultas SQL OLAP de alta performance diretamente em arquivos Parquet.
* **Ollama (Qwen 2.5 Coder 1.5B / Llama 3.1):** Motor de inferência local para raciocínio analítico.
* **Apache Parquet:** Formato colunar otimizado para cenários analíticos.

---

## 📂 Estrutura do Repositório

```text
├── bigdata_agent.py          # Script principal (geração, consultas DuckDB e agente LLM)
├── auditoria_anomalias.md     # Relatório de auditoria executivo gerado pelo agente
├── visualizacao.ipynb        # Notebook para exploração interativa de métricas
├── .gitignore                # Regras para ignorar logs e binários pesados (.parquet)
└── README.md                 # Documentação técnica do projeto
```

---

## 🚀 Como Executar

### 1. Pré-requisitos
Certifique-se de ter o [Ollama](https://ollama.com/) instalado e com o serviço ativo.

No terminal (local ou via GitHub Codespaces):
```bash
# Inicia o serviço do Ollama em segundo plano
nohup ollama serve > ollama.log 2>&1 &

# Baixa o modelo utilizado pelo pipeline
ollama pull qwen2.5-coder:1.5b
```

### 2. Instalação das Dependências
```bash
pip install duckdb polars ollama numpy
```

### 3. Execução do Pipeline
```bash
python bigdata_agent.py
```

O script realizará:
* A verificação/geração da base de **1.000.000 de transações** em formato `.parquet`.
* O cálculo instantâneo de agregações (ticket médio, desvio padrão e limites estatísticos) com DuckDB.
* O envio do resumo estatístico ao agente LLM local.
* A execução da query de isolamento das transações acima de **3 desvios padrão**.
* A emissão do arquivo consolidado `auditoria_anomalias.md`.

---

## 📊 Amostra do Output Gerado

Trecho do relatório executivo gerado em `auditoria_anomalias.md`:

```markdown
## 1. Estatísticas Agregadas (DuckDB)
merchant_category  total_transacoes  ticket_medio  valor_maximo  desvio_padrao
           crypto            200412        198.45      98500.00        2241.18
      electronics            199850         50.12        421.30          49.88
           travel            199780         49.85        398.20          50.11

## 2. Diagnóstico do Agente Autônomo (LLM)
A categoria 'crypto' apresenta comportamento crítico: enquanto as demais categorias 
possuem valor máximo contido abaixo de $500, 'crypto' registra picos de $98.500,00 
com desvio padrão anormal, indicando alto risco de fraude transacional.

## 3. Evidências: Registros Isolados (> 3 Desvios Padrão)
transaction_id  user_id  merchant_category    amount  is_international
        142301    24102             crypto  98500.00                 1
        852119    45190             crypto  98500.00                 0
```

---

## 🎯 Destaques de Engenharia de Dados

* **Processamento Out-of-Core:** Utilização do DuckDB para evitar *OutOfMemory (OOM)* em hardware restrito, permitindo processar dezenas de milhões de linhas de forma eficiente.
* **Segurança e Privacidade:** Conformidade com ambientes regulados e políticas restritivas de proxy/firewall ao não transferir dados confidenciais para endpoints externos.
* **Automação de Auditoria:** Redução do tempo de triagem operacional por meio de diagnósticos analíticos automáticos acoplados ao pipeline de dados.