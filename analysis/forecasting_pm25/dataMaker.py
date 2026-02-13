import pandas as pd
import holidays


def make_data(start, end):
    # Gera datas de 01/01/2022 até 01/01/2025
    datas = pd.date_range(start, end, freq='D')

    # Calcula o dia da semana com 1 = domingo, ..., 7 = sábado
    dias_semana = ((datas.dayofweek + 1) % 7) + 1

    # Cria o DataFrame
    df = pd.DataFrame({
        'Data': datas.strftime('%Y-%m-%d'),  # formato DD/MM/AAAA
        'semana': dias_semana
    })

    # Salva como CSV
    df.to_csv(f'dia_da_semana.csv', index=False)

    return df

def make_holiday(start,end):

    df = make_data(start,end)
    
    # Inicializa coluna feriado com 0
    df['feriado'] = 0

    df["Data"] = pd.to_datetime(df["Data"], errors='coerce')
    df['data_str'] = df['Data'].dt.strftime('%Y-%m-%d')

    anos = df["Data"].dt.year.unique()
    # Feriados nacionais do Brasil
    feriados_br = holidays.Brazil(years=anos)

    # Mapear data_date para índice do DataFrame
    df['data_date'] = df['Data'].dt.date
    data_to_index = {d: i for i, d in enumerate(df['data_date'])}

    # Aplica marcação para cada feriado
    for feriado in feriados_br:
        if feriado in data_to_index:
            pos = data_to_index[feriado]
            semana = df.iloc[pos][f'semana']
            marcar_feriado_extendido(semana, pos, df)

    # Exporta resultado
    df_final = df[['data_str', 'feriado']]
    df_final.columns = ['Data', 'feriado']
    df_final.to_csv(f"feriados.csv", index=False)


# Define função para marcar feriados e dias vizinhos
def marcar_feriado_extendido(semana, pos,df):
    dias = []
    if semana == 1:  # Domingo
        dias = [pos]
    elif semana == 2:  # Segunda
        dias = [pos - 2, pos - 1, pos]
    elif semana == 3:  # Terça
        dias = [pos - 3, pos - 2, pos - 1, pos]
    elif semana == 4:  # Quarta
        dias = [pos, pos + 1, pos + 2, pos + 3, pos + 4]
    elif semana == 5:  # Quinta
        dias = [pos, pos + 1, pos + 2, pos + 3]
    elif semana == 6:  # Sexta
        dias = [pos, pos + 1, pos + 2]
    elif semana == 7:  # Sábado
        dias = [pos, pos + 1]
    
    for i in dias:
        if 0 <= i < len(df):
            df.at[i, 'feriado'] = 1
    
make_holiday('2022-1-1','2024-12-31')