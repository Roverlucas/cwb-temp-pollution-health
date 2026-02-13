import pandas as pd
from prophet import Prophet
import matplotlib.pyplot as plt

def prever_temperatura_ano(arquivo_csv='dados_simepar.csv', ano_alvo=2030):
    try:
        # 1. Carregar dados
        df = pd.read_csv(arquivo_csv)

        # Verificar colunas necessárias
        if not all(col in df.columns for col in ['datahora', 'media']):
            raise ValueError("O arquivo deve conter as colunas 'datahora' e 'media'.")

        # 2. Preparar dados para Prophet
        df = df[['datahora', 'media']].rename(columns={'datahora': 'ds', 'media': 'y'})
        df['ds'] = pd.to_datetime(df['ds'], errors='coerce')
        df = df.dropna().sort_values('ds')

        if len(df) < 2:
            raise ValueError("Dados insuficientes para modelagem.")

        # 3. Treinar modelo Prophet
        model = Prophet(yearly_seasonality=True, daily_seasonality=False)
        model.fit(df)

        # 4. Gerar datas futuras até o final do ano alvo
        ultima_data = df['ds'].max()
        data_final = pd.to_datetime(f'{ano_alvo}-12-31')
        if ultima_data >= data_final:
            print(f"Já existem dados até {data_final.date()}. Gerando previsão apenas para o ano {ano_alvo}.")
            future = df.copy()
        else:
            dias_adicionais = (data_final - ultima_data).days
            future = model.make_future_dataframe(periods=dias_adicionais, freq='D')

        # 5. Prever
        forecast = model.predict(future)

        # 6. Filtrar apenas o ano desejado
        forecast_ano = forecast[forecast['ds'].dt.year == ano_alvo]
        if forecast_ano.empty:
            print(f"Nenhuma previsão gerada para o ano {ano_alvo}.")
            return
        


        # 7. Salvar resultado
        nome_arquivo_saida = f'previsao_temperatura_{ano_alvo}.csv'
        forecast_ano_renomeado = forecast_ano[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].rename(columns={'ds': 'Data'})
        forecast_ano_renomeado.to_csv(
            nome_arquivo_saida,
            index=False,
            date_format='%Y-%m-%d'
        )
        print(f"Previsão para {ano_alvo} salva em: {nome_arquivo_saida}")

        # 8. Plotar resultado completo
        fig = model.plot(forecast)
        plt.title(f"Previsão de Temperatura até {forecast['ds'].max().year}")
        plt.show()

    except Exception as e:
        print(f"Erro: {str(e)}")

# Exemplo de uso:
if __name__ == '__main__':
    prever_temperatura_ano(ano_alvo=2030)
    prever_temperatura_ano(ano_alvo=2050)
