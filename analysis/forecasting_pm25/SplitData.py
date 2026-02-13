import pandas as pd

# Carrega o CSV
df = pd.read_csv("internacoes_curitiba.csv")

# Renomeia a coluna de data (caso necessário)
df = df.rename(columns={"DATE": "Data"})

# Seleciona apenas as colunas desejadas
df_filtrado = df[["Data", "Hospitalizations"]].copy()

# Salva o novo CSV
df_filtrado.to_csv("internacoes_curitiba.csv", index=False)