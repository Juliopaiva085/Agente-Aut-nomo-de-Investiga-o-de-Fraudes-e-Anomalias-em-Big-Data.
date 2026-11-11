# Relatório de Auditoria de Big Data

Dataset: `transacoes_bigdata.parquet` (1.000.000 de registros)

## 1. Estatísticas Agregadas (DuckDB)
```
merchant_category  total_transacoes  ticket_medio  valor_maximo  desvio_padrao
           travel            200549         51.38       98500.0         384.04
           crypto            199529         52.23       98500.0         495.33
           retail            199416         50.21       98500.0         225.99
        groceries            200426         52.54       98500.0         494.26
      electronics            200080         50.64       98500.0         225.76
```

## 2. Diagnóstico do Agente Autônomo (LLM)
1. **Identificação do comportamento mais anômalo:**

   A categoria "retail" apresenta o comportamento mais anômalo, com um ticket médio de $50.21, sendo mais baixo que as demais categorias (travel, crypto, groceries, electronics) que possuem um ticket médio de aproximadamente $51.38.

2. **Risco associado:**

   Para o negócio, a anomalia na categoria "retail" pode implicar:

   - **Perda de transações:** Se o ticket médio for significativamente baixo para uma categoria, os comerciantes podem perder transações, pois um menor número de produtos por transação pode resultar em menos lucros.
   
   - **Menor receita por transação:** Se o ticket médio for muito baixo, as vendas por transação podem ser reduzidas, afetando o lucro por transação.
   
   - **Risco de fraude:** Uma categoria com um ticket médio muito baixo pode ser mais fácil de manipular e falsificar, aumentando o risco de fraude.

## 3. Evidências: Registros Isolados (> 3 Desvios Padrão)
```
 transaction_id  user_id merchant_category  amount  is_international
         275128    23640            crypto 98500.0                 0
         317591    28502            crypto 98500.0                 0
         672732    15616            crypto 98500.0                 0
         114105    11546            crypto 98500.0                 0
         938208    13227            crypto 98500.0                 0
```
