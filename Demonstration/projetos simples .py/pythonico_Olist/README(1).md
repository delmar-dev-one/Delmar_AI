 # 🧹 Pipeline de Sanitização — Olist Dataset

Projeto de limpeza e padronização de dois datasets do e-commerce Olist,
desenvolvido com **Python puro** (sem Pandas), usando `csv.DictReader`,
`datetime`, `re` e estruturas nativas da linguagem.

---

## 📁 Estrutura do Repositório

```
mine_projeto_bloco_1/
├── sanitizacao.py                  # Módulo com todas as funções reutilizáveis
├── main.py                         # Orquestrador dos dois pipelines
├── olist_orders_dataset.csv        # Dataset de entrada — Pedidos
├── olist_products_dataset.csv      # Dataset de entrada — Produtos
├── olist_orders_processado.csv     # Saída gerada automaticamente
├── olist_products_processado.csv   # Saída gerada automaticamente
└── README.md                       # Este arquivo
```

---

## ⚙️ Como Executar

### 1. Pré-requisitos

- Python **3.10 ou superior** (usa `str | None` em type hints)
- **Nenhuma biblioteca externa** — apenas a biblioteca padrão do Python

### 2. Baixar os datasets

Faça o download dos dois arquivos CSV do
[Kaggle — Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
e coloque-os na mesma pasta que `main.py`:

```
olist_orders_dataset.csv
olist_products_dataset.csv
```

### 3. Rodar o pipeline

```bash
python main.py
```

O terminal exibirá dois relatórios — um por dataset — seguidos das
primeiras 5 linhas de cada CSV gerado:

```
🔄  Iniciando pipeline: PEDIDOS
✔  Arquivo salvo em: olist_orders_processado.csv

════════════════════════════════════════════
             RELATÓRIO FINAL
════════════════════════════════════════════
  Linhas processadas        :    99441
  Registros nulos corrigidos:      xxx   ← pedidos pendentes
  Pedidos cancelados s/data :      xxx   ← cancelados sem entrega
════════════════════════════════════════════

🔄  Iniciando pipeline: PRODUTOS
✔  Arquivo salvo em: olist_products_processado.csv

════════════════════════════════════════════
             RELATÓRIO FINAL
════════════════════════════════════════════
  Linhas processadas        :    32951
  Registros nulos corrigidos:      xxx   ← categorias corrigidas
  Pedidos cancelados s/data :      xxx   ← dimensões inválidas (≤ 0)
════════════════════════════════════════════

✅  Sanitização concluída.
```

---

## 🔍 O que cada arquivo faz

### `sanitizacao.py` — funções reutilizáveis

| Função | O que faz |
|--------|-----------|
| `ler_csv(caminho)` | Lê CSV com `csv.DictReader` → `list[dict]` sem Pandas |
| `vazio(tratar, substitutos)` | Trata nulos por coluna: valor fixo, média ou `None` |
| `_normalizar(valor)` | Converte `''`, `'NULL'`, `'N/A'`, `'None'` → `None` |
| `_parece_data(coluna)` | Detecta colunas de data pelo nome (`'date'`, `'time'`) |
| `_converter_data(valor)` | Tenta 5 formatos de data com `strptime`; mantém string se falhar |
| `_calcular_media(registros, col)` | Média aritmética ignorando nulos e não-numéricos |
| `calcular_media` | Alias público de `_calcular_media` para importação externa |
| `lida_categorias(n)` | `lower()` + `strip()` + `re.sub()` para padronizar categorias |
| `classificar_pedido(pedido)` | Classifica em `'entregue'` / `'cancelado'` / `'pendente'` |
| `formatar_data_br(data)` | `datetime` ou string ISO → `'DD/MM/AAAA'` |
| `salvar_csv(caminho, dados)` | Salva `list[dict]` em CSV com Python puro (RFC 4180) |
| `exibir_relatorio(...)` | Imprime sumário estatístico no terminal |

### `main.py` — dois pipelines independentes

#### Pipeline A — Pedidos

```
ler_csv('olist_orders_dataset.csv')
  → vazio(regras_pedidos)          # nulos → None ou 'desconhecido'
  → lida_categorias(order_status)  # lower + strip + regex
  → classificar_pedido()           # 'entregue'|'cancelado'|'pendente'
  → formatar_data_br() ×5 colunas  # todas as datas → DD/MM/AAAA
  → salvar_csv('olist_orders_processado.csv')
  → exibir_relatorio()
```

#### Pipeline B — Produtos

```
ler_csv('olist_products_dataset.csv')
  → calcular_media() ×7 colunas    # pré-calcula médias antes do loop
  → vazio(regras_produtos)         # nulos → 'sem categoria' | média | 0
  → lida_categorias(category)      # lower + strip + regex
  → float() em colunas numéricas   # converte strings do CSV para número
  → validar dimensões ≤ 0          # substitui valores impossíveis pela média
  → int(photos_qty)                # garante inteiro, não float
  → salvar_csv('olist_products_processado.csv')
  → exibir_relatorio()
```

---

## 🗂️ Estratégia de tratamento por coluna

### Dataset de Pedidos — `olist_orders_dataset.csv`

| Coluna | Tipo | Nulo vira | Motivo |
|--------|------|-----------|--------|
| `order_status` | texto | `'desconhecido'` | Evita quebrar `lida_categorias()` |
| `order_approved_at` | data | `None` | Média de timestamps não tem significado |
| `order_delivered_carrier_date` | data | `None` | Pedido ainda não enviado é estado válido |
| `order_delivered_customer_date` | data | `None` | Pedido não entregue → `classificar_pedido()` decide |
| `order_purchase_timestamp` | data | — | Sempre preenchido no Olist |
| `order_estimated_delivery_date` | data | — | Sempre preenchido no Olist |

Nova coluna gerada: **`classificacao`** → `'entregue'` / `'cancelado'` / `'pendente'`

### Dataset de Produtos — `olist_products_dataset.csv`

| Coluna | Tipo | Nulo vira | Motivo |
|--------|------|-----------|--------|
| `product_category_name` | texto | `'sem categoria'` | Requisito explícito do projeto |
| `product_name_lenght` | int | média da coluna | Dado estatístico; média é representativa |
| `product_description_lenght` | int | média da coluna | Idem |
| `product_photos_qty` | int | `0` | Produto sem foto é estado válido de negócio |
| `product_weight_g` | float | média da coluna | Dimensão física sem dado → média dos demais |
| `product_length_cm` | float | média da coluna | Idem |
| `product_height_cm` | float | média da coluna | Idem |
| `product_width_cm` | float | média da coluna | Idem |

Validação extra: **dimensões com valor ≤ 0** são fisicamente impossíveis
(peso zero, altura negativa indicam erro de cadastro) e também são
substituídas pela média da coluna.

---

## 🛠️ Decisões técnicas

### Por que `csv.DictReader` e não Pandas?

O projeto demonstra domínio dos recursos nativos do Python. `csv.DictReader`
mapeia cada linha em um dicionário sem dependência externa — mais leve,
mais portável e auditável linha a linha.

### Por que `USAR_MEDIA` é um objeto sentinela e não `None`?

`None` é um valor legítimo de substituição (para datas ausentes). Usar
`object()` como sentinela garante que nunca haverá colisão acidental:
`USAR_MEDIA is None` é sempre `False`.

### Por que as médias são pré-calculadas antes do loop?

Calcular a média dentro do `for produto in produtos` repetiria a operação
32 mil vezes. O pré-cálculo percorre os dados uma única vez por coluna,
antes do loop principal — reduzindo o custo de O(n²) para O(n).

### Por que média não faz sentido para datas?

A média de timestamps gera um instante artificial que não corresponde a
nenhum evento real. Para datas ausentes, mantém-se `None` e a função
`classificar_pedido()` interpreta o significado desse campo vazio segundo
a regra de negócio Olist.

### Regra de negócio — classificação de pedidos

```
order_delivered_customer_date == None?
  ├── order_status == 'canceled'  →  'cancelado'
  └── qualquer outro status       →  'pendente'
order_delivered_customer_date preenchida →  'entregue'
```

Pedidos sem data de entrega **não são necessariamente cancelados** —
podem estar em trânsito ou com status desatualizado no sistema.

### Por que classificar antes de formatar as datas?

`classificar_pedido()` testa `if not pedido.get('order_delivered_customer_date')`.
Se a data já estivesse formatada como `'13/04/2017'` (string não vazia),
o teste retornaria `False` e todos os pedidos seriam marcados como
`'entregue'` — um bug silencioso. A formatação ocorre **depois** da
classificação.

### Por que `product_photos_qty` vai para `0` e não para a média?

Um produto com `0` fotos é um estado válido de cadastro incompleto.
A média resultaria em um valor fracionário como `2.3 fotos`, que não
faz sentido semântico. O zero preserva a informação de ausência.

---

## 📊 Qualidade de Dados e Machine Learning — Reflexão Teórica

### Por que qualidade de dados importa em ML?

Modelos de Machine Learning aprendem padrões a partir dos dados de
treinamento. Dados com erros, nulos mal tratados ou categorias
inconsistentes fazem o modelo aprender padrões errados — fenômeno
conhecido como **"garbage in, garbage out"**.

No contexto deste dataset Olist, os principais riscos sem sanitização
seriam:

**1. Valores nulos sem tratamento**

Algoritmos como os do `scikit-learn` lançam `ValueError` em colunas com
`NaN`. Substituir nulos pela média é válido para variáveis numéricas com
distribuição simétrica (como peso e comprimento), mas pode introduzir
viés em distribuições assimétricas — nesses casos a mediana seria mais
adequada.

**2. Categorias inconsistentes**

`"Eletrônicos"`, `" eletronicos "` e `"ELETRONICOS!"` são três strings
distintas para o mesmo conceito. Sem `lower()` + `strip()` + `re.sub()`,
um modelo de árvore de decisão criaria três ramos separados para a mesma
categoria, inflando a complexidade e reduzindo a generalização.

**3. Datas como strings**

Modelos não interpretam `'2017-10-02 10:56:33'` como uma data — entendem
como texto opaco. Converter para `datetime` e extrair `hora`, `dia_semana`,
`tempo_de_entrega` como features numéricas permite ao modelo capturar
sazonalidade e padrões temporais.

**4. Dimensões físicas inválidas**

Um produto com `weight_g = 0` ou `height_cm = -1` passaria despercebido
sem validação. Em modelos de regressão para previsão de frete, esses
valores distorceriam os coeficientes — pois o modelo tentaria aprender
que "peso zero custa X reais de frete".

**5. Classificação incorreta do status do pedido**

`order_status` seria uma feature importante em modelos preditivos de
satisfação ou churn. Se pedidos pendentes forem confundidos com
cancelados, o modelo aprende uma associação falsa entre ausência de data
de entrega e cancelamento.

### Boas práticas aplicadas neste projeto

| Problema | Técnica | Justificativa |
|----------|---------|---------------|
| Strings vazias, NULL, N/A | `_normalizar()` → `None` | Padroniza representações diversas de ausência |
| Nulos em texto | `'sem categoria'` / `'desconhecido'` | Mantém o registro sem criar distorção numérica |
| Nulos em numéricos | `USAR_MEDIA` | Estratégia neutra que preserva a distribuição geral |
| Nulos em datas | `None` | Média de timestamps não tem significado de negócio |
| Categorias inconsistentes | `lower()` + `strip()` + `re.sub()` | Garante unicidade de cada categoria |
| Datas como string | `strptime()` com 5 formatos | Habilita extração de features temporais |
| Dimensões ≤ 0 | Substituição pela média | Valores impossíveis fisicamente são erros de cadastro |
| `photos_qty` nulo | `0` | Ausência de foto é informação, não erro numérico |

### Próximos passos para uso em ML

Após a sanitização deste pipeline, as etapas seguintes antes de treinar
um modelo seriam:

1. **Feature engineering** — extrair `hora`, `dia_semana`,
   `tempo_de_entrega_dias` das colunas datetime
2. **Encoding** — converter `order_status`, `classificacao` e
   `product_category_name` com `LabelEncoder` ou `OneHotEncoder`
3. **Normalização** — escalar variáveis contínuas (peso, frete, dimensões)
   com `MinMaxScaler` ou `StandardScaler`
4. **Divisão treino/teste** — separar os dados **antes** de qualquer
   transformação para evitar data leakage
5. **Análise de outliers** — detectar produtos com dimensões muito acima
   da média (ex: `weight_g > 3σ`) que podem distorcer modelos de regressão

---

## 📄 Licença

Projeto educacional — uso livre para fins de estudo.

Dataset original: [Olist Brazilian E-Commerce](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
(licença CC BY-NC-SA 4.0).
