import numpy as np
import pandas as pd


def converter_tass(arquivo, saida, inicio, fim=None):
    # Lê o arquivo com parse de datas
    df = pd.read_csv(arquivo, parse_dates=["time"])
    coluna = df.columns[1]
    
    df["tass_celsius"] = df[coluna] - 273.15

    # Filtragem por período
    if fim:
        df = df[(df["time"] >= inicio) & (df["time"] <= fim)]
    else:
        df = df[df["time"] >= inicio]

    # Remove o horário, mantendo só a data
    df['Data'] = df['time'].dt.date

    # Renomeia a coluna
    df = df[['Data', 'tass_celsius']]
    df = df.rename(columns={'tass_celsius': 'temperature'})

    # Salva apenas o necessário
    df[["Data", "temperature"]].to_csv(saida, index=False)

def converter_huss(arquivo_huss, arquivo_tas, saida, inicio, fim=None):
    # Lê os arquivos
    df_huss = pd.read_csv(arquivo_huss, parse_dates=["time"])
    df_tas = pd.read_csv(arquivo_tas, parse_dates=["time"])

    # Renomeia colunas para garantir compatibilidade
    df_huss.columns = ['time', 'huss']
    df_tas.columns = ['time', 'tas']

    # Merge por tempo
    df = pd.merge(df_huss, df_tas, on="time", how="inner")

    # Filtragem por período
    if fim:
        df = df[(df["time"] >= inicio) & (df["time"] <= fim)]
    else:
        df = df[df["time"] >= inicio]

    # Converte huss de g/kg para kg/kg, se necessário
    if df["huss"].mean() > 0.1:
        df["huss"] = df["huss"] / 1000

    # Converte tas de Kelvin para Celsius, se necessário
    if df["tas"].mean() > 100:
        df["tas"] = df["tas"] - 273.15

    # Constante de pressão média em Curitiba (hPa)
    p = 900.0

    # Fórmulas
    q = df["huss"]
    T = df["tas"]

    e = (q * p) / (0.622 + 0.378 * q)
    es = 6.112 * np.exp((17.67 * T) / (T + 243.5))
    RH = 100 * e / es

    # Limita RH em 100%
    RH = RH.clip(upper=100)

    # Prepara o DataFrame final
    df["Data"] = df["time"].dt.date
    df["humidity"] = RH

    df[["Data", "humidity"]].to_csv(saida, index=False)
    
converter_tass("dados_cmip6/tasmed.csv",'temperatura_2099.csv', '2099-01-01','2100-01-01' )
converter_huss("dados_cmip6/huss.csv","dados_cmip6/tasmed.csv", 'umidade_2099.csv', '2099-01-01','2100-01-01' )
