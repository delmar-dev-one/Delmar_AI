#bibliotecas que iremos utlizar no modelo
from sklearn.datasets import load_diabetes
from sklearn.linear_model import LinearRegression
from sklearn.kernel_ridge import KernelRidge
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.pipeline import Pipeline
from sklearn.kernel_ridge import KernelRidge
from sklearn.metrics import r2_score
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

__all__ = [
    'pd',
    'sns',
    'plt',
    'r2_score',
    'PolynomialFeatures',
    'load_diabetes',
    'train_test_split',
    'Pipeline',
    'StandardScaler',
    'LinearRegression',
    'KernelRidge'
]