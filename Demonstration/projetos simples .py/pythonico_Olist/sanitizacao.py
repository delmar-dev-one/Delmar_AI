import csv        # Leitura nativa de arquivos CSV
import re         # Expressões regulares para limpeza de strings
import datetime   # Conversão e manipulação de datas
import os         # Operações com caminhos de arquivos

# ──────────────────────────────────────────────────────────────────────
#   CONFIGURAÇÃO DE CAMINHOS

# Diretório base onde estão os arquivos CSV do projeto
BASE_DIR = "/home/delmar/Downloads/mine_projeto_bloco_1-main"

# Caminhos completos de cada dataset — usa concatenação simples de string
caminho_arquivo1 = BASE_DIR + '/olist_products_dataset.csv'
caminho_arquivo2 = BASE_DIR + '/olist_orders_dataset.csv'

# ──────────────────────────────────────────────────────────────────────
#   SENTINELA: marcador especial para indicar "substituir pela média"
#   É um objeto único em memória — nunca será igual a None ou a qualquer
#   outro valor acidental do CSV.
USAR_MEDIA = object()

# ──────────────────────────────────────────────────────────────────────
#   LEITURA DO CSV

def ler_csv(caminho: str) -> list:

    # Abre o arquivo em modo leitura com codificação UTF-8 e no caminho especificado
    with open(caminho, newline='', encoding='utf-8') as f:
        # DictReader mapeia automaticamente cabeçalho → valor
        return list(csv.DictReader(f)) # Converte o iterador para lista para facilitar manipulação posterior


# ──────────────────────────────────────────────────────────────────────
#   HELPS INTERNOS  (prefixo _ = uso interno do módulo)

def _normalizar(valor) -> str | None:
    # Trata os dados : None nativo, string vazia, 'NULL', 'null',
    # 'N/A', 'NA' e 'None' (texto literal vindo do CSV).

    # Já é None nativo — retorna direto
    if valor is None:
        return None

    # Se for string, verifica se representa um vazio conhecido
    if isinstance(valor, str) and valor.strip() in ('', 'NULL', 'null', 'N/A', 'NA', 'None'):
        return None

    # Valor válido: remove espaços das bordas se for string
    return valor.strip() if isinstance(valor, str) else valor

# Aqui vamos detecta colunas que provavelmente contêm datas ou horas.
def _parece_data(nome_coluna: str) -> bool: #  bool  →  True se a coluna parecer conter data/hora

    nome = nome_coluna.lower()  # Normaliza para minúsculas antes de comparar os dados
    return 'date' in nome or 'time' in nome # Se o nome da coluna contém 'date' ou 'time', é provável que seja uma data/hora


# Formatos de data aceitos, do mais completo ao mais simples.
# A função _converter_data testa cada um na ordem até encontrar o correto.
FORMATOS_DATA = [
    '%Y-%m-%d %H:%M:%S',   # 2017-10-02 10:56:33  ← padrão dos dados +Olist
    '%Y-%m-%d %H:%M',      # 2017-10-02 10:56
    '%Y-%m-%d',            # 2017-10-02
    '%d/%m/%Y %H:%M:%S',   # 02/10/2017 10:56:33
    '%d/%m/%Y',            # 02/10/2017
]


def _converter_data(valor: str) -> datetime.datetime | str:
    """
    Tenta converter uma string em objeto datetime.

    Percorre FORMATOS_DATA em ordem; retorna o datetime
    convertido no primeiro formato que funcionar.
    Se nenhum funcionar, devolve a string original intacta.

    Parâmetros
    ----------
    valor : str
        String que representa uma data/hora

    Retorna
    -------
    datetime.datetime  se a conversão for bem-sucedida
    str                se nenhum formato bater (mantém original)
    """
    for fmt in FORMATOS_DATA:
        try:
            # strptime tenta interpretar a string segundo o formato
            return datetime.datetime.strptime(valor, fmt)
        except ValueError:
            # Formato não bateu — tenta o próximo
            continue
    # Nenhum formato funcionou: retorna string original sem modificação
    return valor


def _calcular_media(registros: list, coluna: str) -> float | None:
    """
    Calcula a média aritmética dos valores numéricos de uma coluna.

    Ignora valores nulos ou não-numéricos silenciosamente.

    Parâmetros
    ----------
    registros : list[dict]
        Lista de linhas do CSV
    coluna : str
        Nome da coluna a calcular a média

    Retorna
    -------
    float  com duas casas decimais, ou None se não houver valores válidos
    """
    valores = []  # Acumula floats válidos

    for registro in registros:
        # Normaliza o valor antes de tentar converter
        v = _normalizar(registro.get(coluna))
        if v is None:
            continue  # Pula nulos

        try:
            valores.append(float(v))  # Converte para número de ponto flutuante
        except (ValueError, TypeError):
            pass  # Ignora textos que não são numéricos

    if not valores:
        return None  # Sem valores válidos — não é possível calcular

    # Divide a soma pelo total de itens e arredonda para 2 casas decimais
    return round(sum(valores) / len(valores), 2)


# Alias público — permite importar em main.py sem quebrar o prefixo _ interno
calcular_media = _calcular_media

# ──────────────────────────────────────────────────────────────────────
#   TRATAMENTO DE NULOS  (função principal de sanitização)
# ──────────────────────────────────────────────────────────────────────

def vazio(tratar: list, substitutos: dict = None) -> list:
    """
    Trata valores vazios/nulos de uma lista de dicionários de forma flexível.

    Para cada coluna é possível definir uma estratégia diferente:
      • Valor fixo       → ex.: 'Sem Categoria', 0, 'desconhecido'
      • Média da coluna  → USAR_MEDIA  (só faz sentido para numéricos)
      • None             → deixa None (padrão para datas ausentes)

    Além disso, colunas cujo nome contém 'date' ou 'time' são
    automaticamente convertidas para datetime com _converter_data().

    Parâmetros
    ----------
    tratar      : list[dict]   Lista de linhas do CSV
    substitutos : dict         Mapa coluna → valor padrão (opcional)
                               Exemplo:
                                 {
                                   'product_category_name': 'Sem Categoria',
                                   'product_weight_g'     : USAR_MEDIA,
                                   'order_delivered_customer_date': None,
                                 }

    Retorna
    -------
    list[dict]  com os valores tratados (modifica in-place e retorna)
    """
    if substitutos is None:
        substitutos = {}  # Nenhuma regra especial — tudo vira None se vazio

    # Pré-calcula a média apenas das colunas marcadas com USAR_MEDIA
    # Faz isso antes do loop principal para evitar recalcular a cada linha
    medias_pre = {}
    for coluna, padrao in substitutos.items():
        if padrao is USAR_MEDIA:
            # _calcular_media percorre todos os registros e ignora nulos
            medias_pre[coluna] = _calcular_media(tratar, coluna)

    # Percorre cada linha (registro = dicionário de uma linha)
    for registro in tratar:
        # Percorre cada campo (chave → valor) do registro
        for chave, valor in registro.items():

            # ── Passo 1: Normaliza o valor bruto ────────────────────────
            # Converte strings vazias, 'NULL', 'N/A' etc. → None
            valor_limpo = _normalizar(valor)

            # ── Passo 2: Valor está vazio → aplica o substituto ─────────
            if valor_limpo is None:
                padrao = substitutos.get(chave)  # None se coluna não mapeada

                if padrao is USAR_MEDIA:
                    # Substitui pelo valor médio pré-calculado
                    registro[chave] = medias_pre.get(chave)
                else:
                    # Substitui pelo valor fixo definido (ou None por padrão)
                    registro[chave] = padrao

                continue  # Vai para o próximo campo — não tenta converter data

            # ── Passo 3: Valor presente → tenta converter datas ─────────
            if _parece_data(chave):
                # Coluna parece ser de data/hora: tenta converter para datetime
                registro[chave] = _converter_data(valor_limpo)
            else:
                # Campo de texto ou número: mantém o valor limpo
                registro[chave] = valor_limpo

    return tratar  # Retorna a lista modificada


# ──────────────────────────────────────────────────────────────────────
#   MÉDIA  (função legada mantida para compatibilidade)
# ──────────────────────────────────────────────────────────────────────

def media(registros: list, coluna: str) -> float | str:
    """
    Calcula a média de uma coluna numérica ignorando valores nulos.

    Parâmetros
    ----------
    registros : list[dict]   Lista de linhas do CSV
    coluna    : str          Nome da coluna

    Retorna
    -------
    float  com 2 casas decimais, ou 'N/A' se não houver valores válidos
    """
    # Coleta apenas os valores que existem (não são vazios/None)
    vals = [float(r[coluna]) for r in registros if r.get(coluna)]

    try:
        # Divide a soma pelo número de elementos; arredonda para 2 decimais
        return round(sum(vals) / len(vals), 2)
    except ZeroDivisionError:
        # Lista vazia: não há valores numéricos na coluna
        return "N/A"


# ──────────────────────────────────────────────────────────────────────
#   PADRONIZAÇÃO DE CATEGORIAS
# ──────────────────────────────────────────────────────────────────────

def lida_categorias(n: str) -> str:
    """
    Padroniza o nome de uma categoria de produto.

    Aplica três transformações em sequência:
      1. lower()  → converte todas as letras para minúsculas
      2. strip()  → remove espaços no início e no final
      3. re.sub() → remove caracteres especiais, mantendo apenas
                    letras minúsculas, dígitos, sublinhados e espaços

    Parâmetros
    ----------
    n : str
        Nome original da categoria (ex.: 'Eletrônicos!', ' Bebês ')

    Retorna
    -------
    str  padronizada (ex.: 'eletrnicos', 'bebs')
    """
    # Passo 1 e 2: minúsculas e sem espaços nas bordas
    n = n.lower().strip()

    # Passo 3: mantém apenas [a-z], [0-9], underline e espaço
    # O ^ dentro de [] significa "tudo EXCETO os caracteres listados"
    return re.sub(r'[^a-z0-9_\s]', '', n)


# ──────────────────────────────────────────────────────────────────────
#   CLASSIFICAÇÃO DE PEDIDOS
# ──────────────────────────────────────────────────────────────────────

def classificar_pedido(pedido: dict) -> str:
    """
    Classifica um pedido em 'entregue', 'cancelado' ou 'pendente'.

    Regra de negócio Olist:
      • Se NÃO há data de entrega ao cliente:
          – status == 'canceled' → 'cancelado'
          – qualquer outro status → 'pendente'
      • Se HÁ data de entrega → 'entregue'

    Parâmetros
    ----------
    pedido : dict
        Uma linha do dataset de pedidos já tratada

    Retorna
    -------
    str  →  'entregue' | 'cancelado' | 'pendente'
    """
    # Verifica se a data de entrega está ausente (None ou não existe)
    if not pedido.get('order_delivered_customer_date'):
        # Sem data de entrega: decide pelo status registrado no sistema
        return (
            'cancelado'   # Status indica cancelamento explícito
            if pedido.get('order_status') == 'canceled'
            else 'pendente'  # Em processamento ou aguardando envio
        )

    # Data de entrega preenchida → pedido chegou ao cliente
    return 'entregue'


# ──────────────────────────────────────────────────────────────────────
#   FORMATAÇÃO DE DATAS
# ──────────────────────────────────────────────────────────────────────

def formatar_data_br(data) -> str:
    """
    Converte data para o formato brasileiro DD/MM/AAAA.

    Aceita tanto objetos datetime quanto strings no padrão Olist
    ('AAAA-MM-DD HH:MM:SS'). Se a conversão falhar, mantém o original.

    Parâmetros
    ----------
    data : datetime.datetime | str
        Data a ser formatada

    Retorna
    -------
    str  no formato 'DD/MM/AAAA'
    """
    # Se já é um objeto datetime, formata diretamente
    if isinstance(data, datetime.datetime):
        return data.strftime('%d/%m/%Y')

    # Se é string, tenta converter antes de formatar
    try:
        dt = datetime.datetime.strptime(data, '%Y-%m-%d %H:%M:%S')
        return dt.strftime('%d/%m/%Y')
    except (ValueError, TypeError):
        # Não foi possível converter: retorna o valor original
        return data


# ──────────────────────────────────────────────────────────────────────
#   SALVAMENTO
# ──────────────────────────────────────────────────────────────────────

def salvar_csv(caminho: str, dados: list) -> None:
    """
    Salva uma lista de dicionários em um arquivo CSV.

    Usa apenas recursos nativos do Python (sem bibliotecas externas):
      • open()       para criar/sobrescrever o arquivo
      • join()       para montar cada linha com vírgulas
      • replace()    para escapar aspas duplas internas (padrão RFC 4180)

    Parâmetros
    ----------
    caminho : str         Caminho de destino do arquivo .csv
    dados   : list[dict]  Registros a salvar

    Retorna
    -------
    None  (gera o arquivo em disco e exibe mensagem de confirmação)
    """
    # Não há dados para salvar — encerra sem criar arquivo vazio
    if not dados:
        print("Nenhum dado para salvar.")
        return

    # Obtém os nomes das colunas a partir do primeiro registro
    cabecalhos = list(dados[0].keys())

    # Abre o arquivo em modo escrita (sobrescreve se já existir)
    with open(caminho, 'w', encoding='utf-8') as f:

        # ── Linha de cabeçalho ────────────────────────────────────────
        f.write(','.join(cabecalhos) + '\n')

        # ── Uma linha por registro ────────────────────────────────────
        for registro in dados:
            campos = []

            for chave in cabecalhos:
                valor = registro.get(chave, '')

                # Converte None para string vazia
                if valor is None:
                    valor = ''
                elif isinstance(valor, datetime.datetime):
                    # Segurança: datetime que escapou da formatação em main.py
                    # é gravado em formato ISO legível, não como repr do objeto
                    valor = valor.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    valor = str(valor)

                # RFC 4180: valores com vírgula, aspas ou quebra de linha
                # devem ser envolvidos em aspas duplas; aspas internas
                # são escapadas dobrando-as ("")
                if ',' in valor or '"' in valor or '\n' in valor:
                    valor = '"' + valor.replace('"', '""') + '"'

                campos.append(valor)

            # Escreve a linha com os campos separados por vírgula
            f.write(','.join(campos) + '\n')

    print(f"✔  Arquivo salvo em: {caminho}")


# ──────────────────────────────────────────────────────────────────────
#   RELATÓRIO FINAL
# ──────────────────────────────────────────────────────────────────────

def exibir_relatorio(total: int, corrigidos: int, cancelados: int) -> None:
    """
    Exibe um sumário estatístico do pipeline de sanitização.

    Parâmetros
    ----------
    total      : int   Total de linhas processadas
    corrigidos : int   Registros com nulos corrigidos (pendentes)
    cancelados : int   Pedidos classificados como cancelados
    """
    linha = "═" * 44
    print(f"\n{linha}")
    print(f"  {'RELATÓRIO FINAL':^40}")
    print(linha)
    print(f"  Linhas processadas        : {total:>8}")
    print(f"  Registros nulos corrigidos: {corrigidos:>6}")
    print(f"  Pedidos cancelados s/data : {cancelados:>6}")
    print(f"{linha}\n")