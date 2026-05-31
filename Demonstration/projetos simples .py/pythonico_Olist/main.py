import csv        # Necessário para exibir primeiras linhas de verificação
import datetime   # Verificação de tipo datetime na formatação

# Importa todas as funções do módulo de sanitização
from sanitizacao import (
    ler_csv,
    vazio,
    USAR_MEDIA,
    lida_categorias,
    classificar_pedido,
    formatar_data_br,
    salvar_csv,
    exibir_relatorio,
)


# ──────────────────────────────────────────────────────────────────────
#   PIPELINE A — PEDIDOS

def pipeline_pedidos() -> None:
    """
    Lê, trata e salva o dataset de pedidos (olist_orders_dataset.csv).

    Colunas do dataset
    ------------------
    order_id                        : str   — ID único do pedido
    customer_id                     : str   — ID do cliente
    order_status                    : str   — Status (delivered, shipped, etc.)
    order_purchase_timestamp        : data  — Momento da compra
    order_approved_at               : data  — Aprovação do pagamento (pode ser nula)
    order_delivered_carrier_date    : data  — Entrega à transportadora (pode ser nula)
    order_delivered_customer_date   : data  — Entrega ao cliente (pode ser nula)
    order_estimated_delivery_date   : data  — Prazo estimado de entrega

    Tratamentos aplicados
    ---------------------
    • Nulos em datas          → None (média não faz sentido para datas)
    • order_status nulo       → 'desconhecido'
    • Datas válidas           → convertidas para datetime por vazio()
    • order_status            → padronizado com lida_categorias()
    • Classificação           → 'entregue' | 'cancelado' | 'pendente'
    • Datas no CSV final      → formatadas para DD/MM/AAAA
    """

    print("\n Iniciando pipeline: PEDIDOS")

    # LEITURA 
    # Cada linha vira um dict; chaves = cabeçalhos do CSV
    pedidos = ler_csv('olist_orders_dataset.csv')

    #  REGRAS DE TRATAMENTO DE NULOS 
    # Datas ausentes → None   (pedido ainda não passou por essa etapa)
    # Status ausente → texto padrão para não quebrar lida_categorias()
    regras_pedidos = {
        'order_approved_at'            : None,           # Pagamento não aprovado ainda
        'order_delivered_carrier_date' : None,           # Ainda não enviado
        'order_delivered_customer_date': None,           # Ainda não entregue
        'order_status'                 : 'desconhecido', # Status faltante no sistema
    }

    # vazio() normaliza strings vazias/'NULL'/'N/A' → None,
    # aplica os substitutos acima e converte colunas de data → datetime
    pedidos = vazio(pedidos, regras_pedidos)

    # CONTADORES PARA O RELATÓRIO 
    total_corrigidos = 0  # Pedidos pendentes (nulos foram tratados)
    total_cancelados = 0  # Pedidos cancelados sem data de entrega

    # Lista de TODAS as colunas de data do dataset de pedidos.
    # O loop abaixo formata cada uma para DD/MM/AAAA APÓS a classificação,
    # pois classificar_pedido() precisa do valor datetime (ou None) para
    # decidir se o pedido foi entregue.
    COLUNAS_DATA_PEDIDOS = [
        'order_purchase_timestamp',      # Sempre preenchido
        'order_approved_at',             # Pode ser None
        'order_delivered_carrier_date',  # Pode ser None (enviado mas sem registro)
        'order_delivered_customer_date', # Pode ser None (pendente ou cancelado)
        'order_estimated_delivery_date', # Sempre preenchido
    ]

    # PROCESSAMENTO LINHA A LINHA 
    for pedido in pedidos:

        # Padroniza o status com lower() + strip() + re.sub()
        #     Ex: ' Delivered ' → 'delivered', 'CANCELED!' → 'canceled'
        pedido['order_status'] = lida_categorias(
            pedido.get('order_status') or 'desconhecido'
        )

        #  Classifica ANTES de formatar as datas.
        #     classificar_pedido() testa se customer_date é None —
        #     se já fosse string 'DD/MM/AAAA', nunca seria None e
        #     todos os pedidos seriam marcados como 'entregue' (bug).
        classificacao = classificar_pedido(pedido)
        pedido['classificacao'] = classificacao  # Nova coluna no CSV de saída

        #  Contadores para o relatório final
        if classificacao == 'cancelado':
            total_cancelados += 1
        elif classificacao == 'pendente':
            total_corrigidos += 1

        #  Formata todas as colunas de data para DD/MM/AAAA.
        #     Percorre a lista para garantir que nenhuma coluna seja esquecida
        #     (bug anterior: carrier_date ficava como objeto datetime no CSV).
        for col in COLUNAS_DATA_PEDIDOS:
            val = pedido.get(col)
            if val is not None:
                # formatar_data_br() aceita datetime ou string ISO
                pedido[col] = formatar_data_br(val)
            # None permanece None → salvar_csv grava como '' no CSV

    # SALVAMENTO do CSV processado.
    salvar_csv('olist_orders_processado.csv', pedidos)

    #  RELATÓRIO 
    exibir_relatorio(
        total      = len(pedidos),
        corrigidos = total_corrigidos,
        cancelados = total_cancelados,
    )


# ──────────────────────────────────────────────────────────────────────
#   PIPELINE B — PRODUTOS

def pipeline_produtos() -> None:
    """
    Vamos ler, tratar e salvar o dataset de produtos (olist_products_dataset.csv).

    Colunas do dataset
    ------------------
    product_id                  : str   — ID único do produto
    product_category_name       : str   — Categoria em português (pode ser nula)
    product_name_lenght         : int   — Nº de caracteres no nome (pode ser nulo)
    product_description_lenght  : int   — Nº de caracteres na descrição (pode ser nulo)
    product_photos_qty          : int   — Nº de fotos (pode ser nulo)
    product_weight_g            : float — Peso em gramas (pode ser nulo)
    product_length_cm           : float — Comprimento em cm (pode ser nulo)
    product_height_cm           : float — Altura em cm (pode ser nulo)
    product_width_cm            : float — Largura em cm (pode ser nulo)

    Tratamentos aplicados
    ---------------------
    • product_category_name nulo  → 'sem categoria'  (regra do requisito)
    • Dimensões físicas nulas      → média da coluna  (USAR_MEDIA)
    • product_photos_qty nulo      → 0  (produto sem foto cadastrada)
    • product_name/desc_lenght     → média da coluna
    • Categoria                    → padronizada com lida_categorias()
    • Dimensões inválidas (≤ 0)    → substituídas pela média da coluna
    """

    print("\n  Iniciando pipeline: PRODUTOS")

    # LEITURA
    produtos = ler_csv('olist_products_dataset.csv')

    # PRÉ-CALCULA MÉDIAS DAS COLUNAS NUMÉRICAS 
    # Calculado antes do loop para não recalcular a cada linha.
    # As médias serão usadas tanto para nulos quanto para valores inválidos (≤ 0).
    COLUNAS_NUMERICAS = [
        'product_name_lenght',
        'product_description_lenght',
        'product_photos_qty',
        'product_weight_g',
        'product_length_cm',
        'product_height_cm',
        'product_width_cm',
    ]

    # Importa _calcular_media diretamente para uso no pipeline de produtos
    from sanitizacao import calcular_media as _calcular_media

    # Dicionário coluna → média pré-calculada (ignora nulos e não-numéricos)
    medias = {col: _calcular_media(produtos, col) for col in COLUNAS_NUMERICAS}

    # REGRAS DE TRATAMENTO DE NULOS 
    # Cada coluna recebe uma estratégia específica:
    #   'sem categoria' → texto padrão exigido pelo requisito
    #   USAR_MEDIA      → substitui nulos pela média pré-calculada
    #   0               → produto sem foto é um estado válido de negócio
    regras_produtos = {
        'product_category_name'      : 'sem categoria', # Requisito: preencher vazio
        'product_name_lenght'        : USAR_MEDIA,      # Nulo → média dos demais
        'product_description_lenght' : USAR_MEDIA,      # Nulo → média dos demais
        'product_photos_qty'         : 0,               # Sem foto = 0, não média
        'product_weight_g'           : USAR_MEDIA,      # Dimensão física → média
        'product_length_cm'          : USAR_MEDIA,      # Dimensão física → média
        'product_height_cm'          : USAR_MEDIA,      # Dimensão física → média
        'product_width_cm'           : USAR_MEDIA,      # Dimensão física → média
    }

    # Aplica normalização e substitutos em todos os registros
    produtos = vazio(produtos, regras_produtos)

    #  CONTADORES PARA O RELATÓRIO 
    total_categoria_corrigida = 0  # Produtos que tinham categoria nula
    total_dimensao_corrigida  = 0  # Produtos com dimensão nula ou inválida

    # Colunas de dimensão física — usadas na validação de valores ≤ 0
    COLUNAS_DIMENSAO = [
        'product_weight_g',
        'product_length_cm',
        'product_height_cm',
        'product_width_cm',
    ]

    #  PROCESSAMENTO LINHA A LINHA ──
    for produto in produtos:

        # 5a. Padroniza a categoria com lower() + strip() + re.sub()
        #     Ex: 'Bebês'      → 'bebs'   (remove acento)
        #         'Casa & Jardim' → 'casa  jardim'  (remove &)
        #     Se ainda for None após vazio() (improvável), usa 'sem categoria'
        categoria_raw = produto.get('product_category_name') or 'sem categoria'
        produto['product_category_name'] = lida_categorias(categoria_raw)

        # Conta correções de categoria (valor era nulo antes do vazio())
        # A flag é detectável porque vazio() já substituiu None por 'sem categoria'
        if produto['product_category_name'] == 'sem categoria':
            total_categoria_corrigida += 1

        # Converte colunas numéricas de string → float para validação.
        #     vazio() mantém os valores como string (lidos do CSV);
        #     precisamos de float para comparar com 0.
        for col in COLUNAS_NUMERICAS:
            val = produto.get(col)
            if val is not None:
                try:
                    produto[col] = float(val)  # Converte '120.5' → 120.5
                except (ValueError, TypeError):
                    # Valor não é numérico (ex: texto corrompido) → usa média
                    produto[col] = medias.get(col)

        # Valida dimensões físicas: valor ≤ 0 é fisicamente impossível.
        #     Um produto não pode ter peso zero ou altura negativa —
        #     esses valores indicam erro de cadastro, não ausência de dado.
        #     Substituímos pela média da coluna (mesma estratégia dos nulos).
        for col in COLUNAS_DIMENSAO:
            val = produto.get(col)
            # Verifica se é número e se é inválido (zero ou negativo)
            if isinstance(val, float) and val <= 0:
                produto[col] = medias.get(col)  # Substitui pela média
                total_dimensao_corrigida += 1   # Conta para o relatório

        # Garante que product_photos_qty seja inteiro (não float)
        #     O CSV grava '3.0' quando lido como float; convertemos para int
        qty = produto.get('product_photos_qty')
        if qty is not None:
            try:
                produto['product_photos_qty'] = int(float(qty))
            except (ValueError, TypeError):
                produto['product_photos_qty'] = 0  # Fallback seguro

    # SALVAMENTO 
    salvar_csv('olist_products_processado.csv', produtos)

    # RELATÓRIO 
    # Reutiliza exibir_relatorio() adaptando os contadores:
    #   total      = total de produtos lidos
    #   corrigidos = categorias nulas corrigidas
    #   cancelados = dimensões inválidas corrigidas (≤ 0)
    exibir_relatorio(
        total      = len(produtos),
        corrigidos = total_categoria_corrigida,
        cancelados = total_dimensao_corrigida,
    )


# ──────────────────────────────────────────────────────────────────────
#   ORQUESTRADOR PRINCIPAL
    """
    Aqui é executado os dois pipelines em sequência:
      [A] Pedidos  → olist_orders_processado.csv
      [B] Produtos → olist_products_processado.csv
    """
def main() -> None:

    # Pipeline A: dataset de pedidos
    pipeline_pedidos()

    # Pipeline B: dataset de produtos
    pipeline_produtos()

    print("\nOK  Sanitização concluída. Arquivos gerados:")
    print("    • olist_orders_processado.csv")
    print("    • olist_products_processado.csv\n")


# ──────────────────────────────────────────────────────────────────────
#   BLOCO DE VERIFICAÇÃO

if __name__ == "__main__":
    main()

    # Exibe as 5 primeiras linhas de cada CSV gerado para conferência visual
    for nome_arquivo in ('olist_orders_processado.csv', 'olist_products_processado.csv'):
        print(f"\n── Primeiras 5 linhas: {nome_arquivo} ──\n")
        # tente fazer a leitura do arquivo gerado; se não existir, exiba mensagem de erro.
        try:
            with open(nome_arquivo, 'r', encoding='utf-8') as f:
                # csv.DictReader paara lê o CSV e converter cada linha em um dicionário usando os cabeçalhos como chaves
                leitor = csv.DictReader(f)
                for i, linha in enumerate(leitor):
                    if i >= 5:
                        break   # Para após 5 linhas
                    print(linha)

        except FileNotFoundError:
            # Caso o arquivo não tenha sido gerado — provavelmente o CSV de entrada não existe
            print(f"  Arquivo {nome_arquivo} não encontrado.")
