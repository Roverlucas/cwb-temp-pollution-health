import pandas as pd
import numpy as np
import os
import re

# Configurações
FILE = "curitiba"  # Nome do seu arquivo CSV

# Critério mínimo: proporção de dados não nulos por coluna
MIN_PERC_VALID = 0.9

def processar_novos_dados(caminho_arquivo):
    try:
        dados = pd.read_csv(f'{caminho_arquivo}.csv', parse_dates=["time_stamp"])
    except Exception as e:
        print(f"Erro ao carregar o arquivo: {e}")
        return None
    
    # Extração da data definda no arquivo
    dados['Data'] = dados['time_stamp'].dt.date
    
    # Remover colunas não numéricas (exceto timestamp)
    colunas_numericas = dados.select_dtypes(include=[np.number]).columns.tolist()
    
    return dados, colunas_numericas

#não vamos usar, mas serve para caso tenha mais de um no dia
def calcular_medias_simples(dados, colunas):
    # Agrupar por data e calcular média
    medias = dados.groupby('Data')[colunas].mean().reset_index()
    
    # Aplicar critério de percentual de dados válidos por coluna
    resultados = medias.copy()
    for col in colunas:
        count_validos = dados.groupby('Data')[col].apply(lambda x: x.notna().sum())
        total = dados.groupby('Data')[col].count() + dados.groupby('Data')[col].apply(lambda x: x.isna().sum())
        percentual_valido = count_validos / total
        resultados[col] = np.where(percentual_valido >= MIN_PERC_VALID, resultados[col], np.nan)
    
    return resultados

def salvar_resultados(data, nome):

    for col in data.columns:
        if col == "Data":
            continue
        df_coluna = data[["Data", col]]
        caminho_csv = f"{nome}_{col}.csv"
        df_coluna.to_csv(caminho_csv, index=False, float_format="%.4f")
    

dados, colunas_numericas = processar_novos_dados(FILE)

if dados is not None:
    medias_resultado = calcular_medias_simples(dados, colunas_numericas)
  
    salvar_resultados(medias_resultado, FILE)
else:
    print("Falha no processamento.")
