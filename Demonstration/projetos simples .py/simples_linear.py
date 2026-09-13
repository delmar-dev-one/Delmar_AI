import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import IsolationForest



# criar um modelo de previsão de novos dados de entrada
class Previsor:
    def __init__(self, x, y):
        self.data = np.array(x).reshape(-1, 1)
        self.target = np.array(y)
        self.model = LinearRegression()
        self.model.fit(self.data, self.target)

    def predict(self, new_data):
        new_data_reshaped = np.array(new_data).reshape(-1, 1)
        return self.model.predict(new_data_reshaped)
    
    def train_test_split(self, test_size=0.2, random_state=42):
        return train_test_split(self.data, self.target, test_size=test_size, random_state=random_state)
    def plot(self):
        plt.scatter(self.data, self.target, color='blue', label='Dados Reais')
        plt.plot(self.data, self.model.predict(self.data), color='red', label='Linha de Regressão')
        plt.xlabel('Entrada')
        plt.ylabel('Saída')
        plt.title('Regressão Linear Simples')
        plt.legend()
        plt.show()

# exibindo resultados do modelo
if __name__ == "__main__":
    x = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    y = [3, 4, 2, 5, 6, 7, 8, 9, 10, 12]

    previsor = Previsor(x, y)
    
    # Dividir os dados em conjunto de treino e teste
    X_train, X_test, y_train, y_test = previsor.train_test_split()
    
    # Fazer previsões com novos dados
    new_data = [11, 12, 13]
    predictions = previsor.predict(new_data)
    print("Previsões para novos dados \n{}: {}".format(new_data, predictions))
    

    # Plotar os dados e a linha de regressão
    previsor.plot()
    
    print("--------------------------------------------------")


    print("Dados de Treino X:", X_train.flatten())
    print("Dados de Treino y:", y_train)
    print("Dados de Teste X:", X_test.flatten())
    print("Dados de Teste y:", y_test)

    print("--------------------------------------------------")

    # Buscando se há outlaiers nos dados
    iso_forest = IsolationForest(contamination=0.1)
    outliers = iso_forest.fit_predict(previsor.data)
    print("Outliers detectados (1 = normal, -1 = outlier):\n", outliers)