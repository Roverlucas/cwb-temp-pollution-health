import pandas as pd
import numpy as np

def completar_datas_com_nan(nome_arquivo, cidade):
    """
    Completa todas as datas entre a primeira e última data do dataset,
    mantendo os valores originais e colocando NaN explicitamente nos faltantes.
    """
    # 1. Carrega os dados originais
    df = pd.read_csv(f'{cidade}_{nome_arquivo}.csv', parse_dates=['Data'])

    # 2. Cria um range completo de datas
    todas_datas = pd.date_range(
        start='2022-01-01',
        end=df['Data'].max(),
        freq='D'
    )

    # 3. Cria DataFrame com todas as datas
    df_completo = pd.DataFrame({'Data': todas_datas})

    # 4. Faz o merge mantendo NaN nos faltantes
    df_completo = df_completo.merge(df, on='Data', how='left')

    # 5. Garante que os valores numéricos sejam float (para aceitar NaN)
    df_completo[nome_arquivo] = df_completo[nome_arquivo].astype(float)

    # 6. Salva o resultado com NaN explícitos
    nome_saida = f'{cidade}_{nome_arquivo}.csv'
    df_completo.to_csv(nome_saida, index=False, na_rep='NaN')  # Aqui está o segredo!
    
    print(f"Arquivo gerado: '{nome_saida}'")
    print(f"Total de dias: {len(df_completo)}")
    print(f"Dias com NaN: {df_completo[nome_arquivo].isna().sum()}")
    
    return df_completo

import pandas as pd

# Carrega o CSV
df = pd.read_csv('curitiba_temperature.csv')

# Converte 'Data' para datetime (opcional, se quiser trabalhar com datas)
df['Data'] = pd.to_datetime(df['Data'])

# Converte a coluna de temperatura de Fahrenheit para Celsius
df['temperature'] = (df['temperature'] - 32) * 5 / 9

# (Opcional) Salva o resultado
df.to_csv('curitiba_temperature.csv', index=False)

print(df.head())

# Exemplo de uso:
if __name__ == '__main__':

    nomes= ["humidity", "temperature", "pressure", "pm2.5_alt", "pm2.5_alt_a", "pm2.5_alt_b", "0.3_um_count", "1.0_um_count", "2.5_um_count", "10.0_um_count", "pm1.0_cf_1", "pm1.0_cf_1_a", "pm1.0_cf_1_b", "pm10.0_cf_1", "pm10.0_cf_1_a", "pm10.0_cf_1_b"]

    for i in nomes:

        dados = completar_datas_com_nan(
            nome_arquivo=i,
            cidade='curitiba'
        )
    