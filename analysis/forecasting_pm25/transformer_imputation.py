import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from pypots.imputation import Transformer

# Carrega os dados
def transformer(cidade, coluna):
    file_name = f"{cidade}_{coluna}.csv"
    df = pd.read_csv(file_name, parse_dates=['Data'])

    data_values = df.iloc[:, 1:].values  # Exclui a coluna de data

    # Normaliza os dados
    scaler = StandardScaler()
    data_scaled = scaler.fit_transform(data_values)

    # Prepara os dados para o modelo
    n_steps = data_scaled.shape[0]
    n_features = data_scaled.shape[1]
    data_scaled = data_scaled.reshape(1, n_steps, n_features)  # (batch_size, n_steps, n_features)
    dataset = {"X": data_scaled}

    # Inicializa e treina o modelo Transformer
    transformer = Transformer(n_steps=n_steps, n_features=n_features, n_layers=2, d_model=64, n_heads=8, d_k=16, d_v=16, d_ffn=128, dropout=0.1, epochs=200)
    transformer.fit(dataset)

    # Imputa os dados faltantes
    imputed_data = transformer.impute(dataset)
    imputed_data = imputed_data.reshape(-1, 1)
    imputed_data = scaler.inverse_transform(imputed_data)


    # Salva os dados imputados
    df.iloc[:, 1:] = imputed_data
    # Salva o resultado
    df.to_csv(f"transformer_{cidade}_{coluna}.csv", index=False)

colunas = ["humidity", "temperature", "pressure", "pm2.5_alt", "pm2.5_alt_a", "pm2.5_alt_b", "0.3_um_count", "1.0_um_count", "2.5_um_count", "10.0_um_count", "pm1.0_cf_1", "pm1.0_cf_1_a", "pm1.0_cf_1_b", "pm10.0_cf_1", "pm10.0_cf_1_a", "pm10.0_cf_1_b"]
for i in colunas:
    transformer('curitiba',i)