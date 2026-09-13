# Modularização
import sys
import os

# Adiciona a raiz do projeto ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

import Delmar_AI.Demonstration.model_reg.dados_trat as dt
import Delmar_AI.Demonstration.model_reg.library as lib



# Preparação Final do X e y
df_final = dt.df.copy()

# Medição R2_score da nossa library
score = lib.r2_score

# Pipeline
pipeline = lib.Pipeline([
    ('scaler', lib.StandardScaler()), 
    ('kr', lib.KernelRidge())
])

pipeline_2 = lib.Pipeline([
    ('scaler', lib.StandardScaler()),
    ('linear', lib.LinearRegression())
])

pipeline_3 = lib.Pipeline([
    ('scaler', lib.StandardScaler()),
    ('poly', lib.PolynomialFeatures(degree=2)),
    ('model', lib.LinearRegression()) 
])


# X: BMI + Pressão Arterial + Todas as colunas de sangue (s1 a s6)
colunas_x = ['bmi', 'bp', 's1', 's2', 's3', 's4', 's5', 's6']
X = df_final[colunas_x]

# y: O alvo real (progressão da diabetes)
y = dt.diabetes.target.copy()

# Divisão de Treino e Teste
x_tr, x_ts, y_tr, y_ts = lib.train_test_split(X, y, test_size=0.2, random_state=42)

# Treinamento dos Pipelines (Já definidos anteriormente)
pipeline.fit(x_tr, y_tr)     # KernelRidge
pipeline_2.fit(x_tr, y_tr)   # Linear
pipeline_3.fit(x_tr, y_tr)   # Polynomial

# Predições (Usando o conjunto de teste)
pred_1 = pipeline.predict(x_ts)
pred_2 = pipeline_2.predict(x_ts)
pred_3 = pipeline_3.predict(x_ts)

# Gráfico de Dispersão: Real vs Predito (Para o modelo Linear)
lib.plt.figure(figsize=(10, 6))
lib.plt.scatter(y_ts, pred_2, color='blue', alpha=0.5, label='Predições (Linear)')
lib.plt.plot([y_ts.min(), y_ts.max()], [y_ts.min(), y_ts.max()], 'r--', lw=2, label='Perfeição')

lib.plt.xlabel('Valores Reais (Progressão Diabetes)')
lib.plt.ylabel('Valores Preditos pelo Modelo')
lib.plt.title('Comparação: Real vs Predição (Modelo Linear)')
lib.plt.legend()
lib.plt.show()

# Performance Comparativa
print(f"R² KernelRidge: {pipeline.score(x_ts, y_ts):.4f}")
print(f"R² Linear:      {pipeline_2.score(x_ts, y_ts):.4f}")
print(f"R² Polynomial:  {pipeline_3.score(x_ts, y_ts):.4f}")
