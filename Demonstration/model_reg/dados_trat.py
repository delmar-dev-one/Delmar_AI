import Delmar_AI.projeto.model_reg.library as lib

# ──────────────────────────────────────────────────────────────────────────────
# 1. CARREGAMENTO DOS DADOS
# ──────────────────────────────────────────────────────────────────────────────
diabetes = lib.load_diabetes(as_frame=True)
df = lib.pd.DataFrame(data=diabetes.data, columns=diabetes.feature_names)

# ──────────────────────────────────────────────────────────────────────────────
# 2. INSPEÇÃO INICIAL
# ──────────────────────────────────────────────────────────────────────────────
print("=== Primeiras linhas ===")
print(df.head())

print("\n=== Valores faltantes por coluna ===")
print(df.isnull().sum())

print(f"\nDimensões do dataset: {df.shape}")

# ──────────────────────────────────────────────────────────────────────────────
# 3. DECODIFICAÇÃO DA COLUNA 'sex'
#    No dataset original (antes da normalização), sex é 1 ou 2.
#    Após normalização sklearn: valores negativos → grupo 1, positivos → grupo 2.
#    Convenção amplamente usada: negativo = Mulher, positivo = Homem.
# ──────────────────────────────────────────────────────────────────────────────
df['sex'] = df['sex'].apply(lambda x: 'Mulher' if x < 0 else 'Homem')

contagem_genero = df['sex'].value_counts()
print("\n=== Contagem por gênero ===")
print(contagem_genero)

# ──────────────────────────────────────────────────────────────────────────────
# 4. TRATAMENTO DE OUTLIERS – MÉTODO IQR
# ──────────────────────────────────────────────────────────────────────────────
COLUNAS_SANGUE = ['s1', 's2', 's3', 's4', 's5', 's6']


def tratar_outliers_iqr(df: lib.pd.DataFrame, colunas: list[str]) -> lib.pd.DataFrame:
    """
    Clipa outliers pelo critério IQR (±1.5×IQR) para as colunas indicadas.

    Parâmetros
    ----------
    df      : DataFrame original (não é modificado no lugar).
    colunas : Lista de nomes de colunas numéricas a tratar.

    Retorna
    -------
    DataFrame com outliers clipados.
    """
    df_copy = df.copy()
    for col in colunas:
        Q1 = df_copy[col].quantile(0.25)
        Q3 = df_copy[col].quantile(0.75)
        IQR = Q3 - Q1
        lim_inf = Q1 - 1.5 * IQR
        lim_sup = Q3 + 1.5 * IQR
        df_copy[col] = df_copy[col].clip(lower=lim_inf, upper=lim_sup)
    return df_copy


df = tratar_outliers_iqr(df, COLUNAS_SANGUE)

# ──────────────────────────────────────────────────────────────────────────────
# 5. TRANSFORMAÇÃO PARA FORMATO LONGO (TIDY)
# ──────────────────────────────────────────────────────────────────────────────
def transformar_para_long(df: lib.pd.DataFrame) -> lib.pd.DataFrame:
    """
    Aqui vamos converter as colunas de medições sanguíneas (s1–s6) para formato longo,
    mantendo age, sex e bmi como identificadores.
    """
    return df.melt(
        id_vars=['age', 'sex', 'bmi'],
        value_vars=COLUNAS_SANGUE,
        var_name='medicao_tipo',
        value_name='valor_medicao',
    )


df_long = transformar_para_long(df)
print(f"\nDataFrame longo: {df_long.shape[0]} linhas × {df_long.shape[1]} colunas")

# ──────────────────────────────────────────────────────────────────────────────
# 6. VISUALIZAÇÕES
# ──────────────────────────────────────────────────────────────────────────────
CORES_GENERO = {'Homem': 'steelblue', 'Mulher': 'salmon'}

# --- 6a. Dispersão: IMC × Idade segmentado por gênero -----------------------
fig, ax = lib.plt.subplots(figsize=(8, 6))

for genero, grupo in df.groupby('sex'):
    ax.scatter(
        grupo['bmi'], grupo['age'],
        color=CORES_GENERO[genero],
        alpha=0.6,
        edgecolors='white',
        linewidths=0.3,
        label=genero,
    )

ax.set_xlabel('IMC (bmi)')
ax.set_ylabel('Idade (age)')
ax.set_title('Distribuição de IMC por Idade e Gênero')
ax.legend(title='Gênero')
lib.plt.tight_layout()
# lib.plt.savefig('dispersao_imc_idade.png', dpi=150) # Salvando img
lib.plt.show()

# --- 6b. Boxplot: distribuição das medições sanguíneas por gênero -----------
fig, ax = lib.plt.subplots(figsize=(10, 6))

grupos = [
    df_long.loc[df_long['medicao_tipo'] == med, 'valor_medicao'].values
    for med in COLUNAS_SANGUE
]

ax.boxplot(grupos, labels=COLUNAS_SANGUE, patch_artist=True,
           boxprops=dict(facecolor='steelblue', alpha=0.6))
ax.set_xlabel('Tipo de Medição')
ax.set_ylabel('Valor (normalizado)')
ax.set_title('Distribuição das Medições Sanguíneas (após tratamento de outliers)')
lib.plt.tight_layout()
# lib.plt.savefig('boxplot_medicoes.png', dpi=150) # Salvando img
lib.plt.show()

# --- 6c. Barras: média de cada medição sanguínea ----------------------------
fig, ax = lib.plt.subplots(figsize=(8, 5))

medias = df_long.groupby('medicao_tipo')['valor_medicao'].mean().reindex(COLUNAS_SANGUE)
medias.plot(kind='bar', ax=ax, color='steelblue', edgecolor='white', alpha=0.85)

ax.set_xlabel('Tipo de Medição')
ax.set_ylabel('Valor Médio (normalizado)')
ax.set_title('Média das Medições Sanguíneas')
ax.tick_params(axis='x', rotation=0)
lib.plt.tight_layout()
# lib.plt.savefig('media_medicoes.png', dpi=150) # Salvando img
lib.plt.show()

print("\nAnálise concluída. Gráficos salvos em PNG.")


print(df_long)
