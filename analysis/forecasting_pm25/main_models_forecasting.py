import csv
import os
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, mean_absolute_percentage_error
from tqdm import tqdm
from xgboost import XGBRegressor
from MLP_model import MLP_model
import matplotlib.dates as mdates

def split_temporal(X, y, train_size=0.7):
    n = len(X)
    train_end = int(train_size * n)
    
    X_train, y_train = X[:train_end], y[:train_end]
    X_val, y_val = X[train_end:], y[train_end:]
    
    return X_train, y_train, X_val, y_val

def lagApplication(df, pollutant, dias=1):
    df = df.copy()
    df[pollutant] = df[pollutant].shift(-dias)
    df = df.dropna(subset=[pollutant])
    return df

def load_and_prepare_data(Pollutant, Humid, Temp, Week_day, Holiday, internacoes_file, pollutant, lag=0):
    df_Pollutant = pd.read_csv(Pollutant)
    df_Pollutant = lagApplication(df_Pollutant, pollutant, lag)
    df_humid = pd.read_csv(Humid)
    df_temp = pd.read_csv(Temp)

    for df in [df_Pollutant, df_humid, df_temp]:
        df['Data'] = pd.to_datetime(df['Data'], format='%Y-%m-%d')

    df = df_Pollutant.merge(df_humid, on='Data').merge(df_temp, on='Data')

    df_week = pd.read_csv(Week_day)
    df_week['Data'] = pd.to_datetime(df_week['Data'], format='%Y-%m-%d')
    df_holiday = pd.read_csv(Holiday)
    df_holiday['Data'] = pd.to_datetime(df_holiday['Data'], format='%Y-%m-%d')

    df = df.merge(df_week, on='Data').merge(df_holiday, on='Data')

    df_internacoes = pd.read_csv(internacoes_file)
    df_internacoes['Data'] = pd.to_datetime(df_internacoes['Data'], format='%Y-%m-%d')

    df = df.merge(df_internacoes, on='Data')
    df.sort_values('Data', inplace=True)
    
    # **Guardar as datas para plotagem posterior**
    dates = df['Data'].copy()
    df.drop(columns=['Data'], inplace=True)

    X = df.drop(columns=['Hospitalizations'])
    y = df['Hospitalizations']
    return X, y, dates

def load_future_data(Pollutant, Temp_future, Humid_future, Week_day_future, Holiday_future, pollutant, lag):
    # Carrega dados
    df_Pollutant = pd.read_csv(Pollutant)
    df_humid = pd.read_csv(Humid_future)
    df_temp = pd.read_csv(Temp_future)
    df_week = pd.read_csv(Week_day_future)
    df_holiday = pd.read_csv(Holiday_future)

    # df_Pollutant = df_Pollutant.tail(365).reset_index(drop=True)
    # df_humid = df_humid.tail(365).reset_index(drop=True)
    df_temp = df_temp.iloc[:, :2]  # pega só as duas primeiras colunas
    df_temp.columns = ['Data', 'temperature']  # renomeia para padrão
    df_temp['Data'] = pd.to_datetime(df_temp['Data'], errors='coerce')

    # Atualiza coluna Data para alinhar com as datas futuras
    df_Pollutant['Data'] = pd.to_datetime(df_temp['Data'], errors='coerce')
    df_humid['Data'] = pd.to_datetime(df_temp['Data'], errors='coerce')

    # Aplica lag
    df_Pollutant = lagApplication(df_Pollutant, pollutant, lag)

    # **Garante datetime para todas colunas Data antes do merge**
    df_Pollutant['Data'] = pd.to_datetime(df_Pollutant['Data'], errors='coerce')
    df_humid['Data'] = pd.to_datetime(df_humid['Data'], errors='coerce')
    df_temp['Data'] = pd.to_datetime(df_temp['Data'], errors='coerce')
    df_week['Data'] = pd.to_datetime(df_week['Data'], errors='coerce')
    df_holiday['Data'] = pd.to_datetime(df_holiday['Data'], errors='coerce')

    # Combina todos os dados
    df_future = df_Pollutant.merge(df_humid, on='Data').merge(df_temp, on='Data')
    df_future = df_future.merge(df_week, on='Data').merge(df_holiday, on='Data')

    df_future.sort_values('Data', inplace=True)
    
    dates = df_future['Data'].copy()
    df_future.drop(columns=['Data'], inplace=True)
    
    return df_future, dates

def load_data_prev(Internacoes, ano):

    # Carrega dados
    df_internacoes = pd.read_csv(Internacoes)

    # Converte a coluna 'Data' para datetime
    df_internacoes['Data'] = pd.to_datetime(df_internacoes['Data'], format='%Y-%m-%d', errors='coerce')

    # Filtra pelo ano desejado
    df_internacoes = df_internacoes[df_internacoes['Data'].dt.year == ano]

    # Garante no máximo 365 entradas (caso o ano tenha menos, mantém o que tem)
    df_internacoes = df_internacoes.head(365).reset_index(drop=True)

    # Ordena por data e separa as datas
    df_internacoes.sort_values('Data', inplace=True)
    dates = df_internacoes['Data'].copy()
    df_internacoes.drop(columns=['Data'], inplace=True)

    return df_internacoes, dates

def main_all_methods(cidade, pollutant, lag, prev_ano, ano, cold=False, heat=False, pm=False):

    hidden_range = range(1, 2, 1)  
    neuron_MLP =  {0: 6, 1: 4, 2: 3, 3: 3, 4: 6, 5: 3, 6: 4, 7: 12}[lag]
    neuron_xgb = {0: 29, 1: 18, 2: 79, 3: 22, 4: 23, 5: 18, 6: 35, 7: 19}[lag]

    
    #dados históricos
    X, y, dates = load_and_prepare_data(
        f'transformer_{cidade}_{pollutant}.csv',
        f'umidade_2022_2024.csv',
        f'temperatura_2022_2024.csv',
        'dia_da_semana.csv',
        'feriados.csv',
        f'internacoes_{cidade}.csv',
        pollutant,
        lag
    )
    
    # Normalização
    scaler_X = StandardScaler()
    X_scaled = scaler_X.fit_transform(X)
    scaler_y = StandardScaler()
    y_scaled = scaler_y.fit_transform(y.values.reshape(-1, 1))
    
    X_train, y_train, X_val, y_val = split_temporal(X_scaled, y_scaled)
    y_val_inv = scaler_y.inverse_transform(y_val)
    
    # 3. Treina modelos e encontra melhores parâmetros
    best_models = {
        'MLP': {'model': None, 'n': None, 'mse_val': float('inf')},
        'XGBOOST': {'model': None, 'n': None, 'mse_val': float('inf')},
    }
    
    for n_neurons in tqdm(hidden_range, desc="Testando hiperparâmetros"):

        # Testa MLP
        mlp = MLP_model(hidden_layer_sizes=[neuron_MLP], max_iter=1000)
        mlp.fit(X_train, y_train.ravel())
        y_pred_val = mlp.predict(X_val)
        y_pred_val_inv = scaler_y.inverse_transform(y_pred_val.reshape(-1, 1))
        mse_val = mean_squared_error(y_val_inv, y_pred_val_inv)
        if mse_val < best_models['MLP']['mse_val']:
            best_models['MLP'] = {'model': mlp, 'n': n_neurons, 'mse_val': mse_val}
        
        # Testa XGBoost
        xgb = XGBRegressor(n_estimators=neuron_xgb, max_depth=5, learning_rate=0.1, objective='reg:squarederror', random_state=42)
        xgb.fit(X_train, y_train.ravel())
        y_pred_val = xgb.predict(X_val)
        y_pred_val_inv = scaler_y.inverse_transform(y_pred_val.reshape(-1, 1))
        mse_val = mean_squared_error(y_val_inv, y_pred_val_inv)
        if mse_val < best_models['XGBOOST']['mse_val']:
            best_models['XGBOOST'] = {'model': xgb, 'n': n_neurons, 'mse_val': mse_val}
    
    # 4. Avaliação final e previsão para o futuro
    X_train_full = np.concatenate((X_train, X_val), axis=0)
    y_train_full = np.concatenate((y_train, y_val), axis=0)
    
    results = {}
    predictions = {}
    predictions_original = {}
    
    for model_type in ['MLP', 'XGBOOST']:
        best_model = best_models[model_type]['model']
        n_param = best_models[model_type]['n']
        
        # Re-treina com todos os dados
        if model_type == 'MLP':
            best_model.fit(X_train_full, y_train_full.ravel())
            y_pred = best_model.predict(X_val)
        else:  # XGBOOST
            best_model.fit(X_train_full, y_train_full.ravel())
            y_pred = best_model.predict(X_val)

            # ===== SHAP ANALYSIS =====
            import shap
            explainer = shap.Explainer(best_model, X_train_full)
            shap_values = explainer(X_train_full)

            feature_name_map = {
                'temperatura': 'Temperature',
                'temperature': 'Temperature',
                'umidade': 'Relative humidity',
                'humidity': 'Relative humidity',
                'pm2.5_alt': r'PM$_{2.5}$',
                'pm10': r'PM$_{10}$',
                'semana': 'Weekday',
                'feriado': 'Holiday'
            }

            feature_names = [feature_name_map.get(col, col) for col in X.columns]

            plt.figure()
            shap.summary_plot(
                shap_values,
                X_train_full,
                feature_names=feature_names,
                show=False
            )
            plt.tight_layout()
            plt.savefig(
                f'shap_summary_{cidade}_lag{lag}.png',
                dpi=300,
                bbox_inches='tight'
            )
            plt.close()

            plt.figure()
            shap.summary_plot(
                shap_values,
                X_train_full,
                feature_names=feature_names,
                plot_type="bar",
                show=False
            )
            plt.tight_layout()
            plt.savefig(
                f'shap_bar_{cidade}_lag{lag}.png',
                dpi=300,
                bbox_inches='tight'
            )
            plt.close()

        
        y_pred_inv = scaler_y.inverse_transform(y_pred.reshape(-1, 1))
        
        results.update({
            model_type: mean_squared_error(y_val_inv, y_pred_inv),
            f'{model_type}_RMSE': np.sqrt(mean_squared_error(y_val_inv, y_pred_inv)),
            f'{model_type}_MAE': mean_absolute_error(y_val_inv, y_pred_inv),
            f'{model_type}_MAPE': mean_absolute_percentage_error(y_val_inv, y_pred_inv),
            f'{model_type}_N': n_param,
            f'y_pred_{model_type.lower()}': y_pred_inv.flatten()
        })
        
        # Previsão para o futuro
        if cold:
            X_future, dates_future = load_future_data(
                f'transformer_{cidade}_{pollutant}_{prev_ano}.csv',
                f'temperatura_wave_{ano}_cold.csv',
                f'umidade_wave_{ano}_cold.csv',
                #f'transformer_{cidade}_humidity.csv',
                f'dia_da_semana_{ano}.csv',
                f'feriados_{ano}.csv',
                pollutant,
                lag
            )
            X_future_original, dates_future_original = load_future_data(
                f'transformer_{cidade}_{pollutant}_{prev_ano}.csv',
                f'temperatura_{prev_ano}.csv',
                f'umidade_{prev_ano}.csv',
                #f'transformer_{cidade}_humidity.csv',
                f'dia_da_semana_{prev_ano}.csv',
                f'feriados_{prev_ano}.csv',
                pollutant,
                lag
            )
        elif heat:
            X_future, dates_future = load_future_data(
                f'transformer_{cidade}_{pollutant}_{prev_ano}.csv',
                f'temperatura_wave_{ano}_heat.csv',
                f'umidade_wave_{ano}_heat.csv',
                #f'transformer_{cidade}_humidity.csv',
                f'dia_da_semana_{ano}.csv',
                f'feriados_{ano}.csv',
                pollutant,
                lag
            )
            X_future_original, dates_future_original = load_future_data(
                f'transformer_{cidade}_{pollutant}_{prev_ano}.csv',
                f'temperatura_{prev_ano}.csv',
                f'umidade_{prev_ano}.csv',
                #f'transformer_{cidade}_humidity.csv',
                f'dia_da_semana_{prev_ano}.csv',
                f'feriados_{prev_ano}.csv',
                pollutant,
                lag
            )        
        elif pm:
            X_future, dates_future = load_future_data(
                f'transformer_{cidade}_{pollutant}_{ano}_mod.csv',
                f'temperatura_{ano}.csv',
                f'umidade_{ano}.csv',
                #f'transformer_{cidade}_humidity.csv',
                f'dia_da_semana_{ano}.csv',
                f'feriados_{ano}.csv',
                pollutant,
                lag
            )            
            X_future_original, dates_future_original = load_future_data(
                f'transformer_{cidade}_{pollutant}_{prev_ano}.csv',
                f'temperatura_{prev_ano}.csv',
                f'umidade_{prev_ano}.csv',
                #f'transformer_{cidade}_humidity.csv',
                f'dia_da_semana_{prev_ano}.csv',
                f'feriados_{prev_ano}.csv',
                pollutant,
                lag
            )
        else:
            X_future, dates_future = load_future_data(
                f'transformer_{cidade}_{pollutant}_{prev_ano}.csv',
                f'temperatura_{ano}.csv',
                f'umidade_{ano}.csv',
                #f'transformer_{cidade}_humidity.csv',
                f'dia_da_semana_{ano}.csv',
                f'feriados_{ano}.csv',
                pollutant,
                lag
            )            
            X_future_original, dates_future_original = load_future_data(
                f'transformer_{cidade}_{pollutant}_{prev_ano}.csv',
                f'temperatura_{prev_ano}.csv',
                f'umidade_{prev_ano}.csv',
                #f'transformer_{cidade}_humidity.csv',
                f'dia_da_semana_{prev_ano}.csv',
                f'feriados_{prev_ano}.csv',
                pollutant,
                lag
            )
        
        y_prev, dates_prev = load_data_prev(f'internacoes_{cidade}.csv', prev_ano)
        X_future_scaled = scaler_X.transform(X_future)
        X_future_scaled_original = scaler_X.transform(X_future_original)
        preds_scaled = best_model.predict(X_future_scaled)
        preds_scaled_original = best_model.predict(X_future_scaled_original)
        predictions[model_type] = scaler_y.inverse_transform(preds_scaled.reshape(-1, 1)).flatten()
        predictions_original[model_type] = scaler_y.inverse_transform(preds_scaled_original.reshape(-1, 1)).flatten()
    
    results['y_test'] = y_val_inv.flatten()
    
    # Gera gráficos e CSV com as datas de validação (prev) e previsão (ano futuro)
    if heat:
        generate_outputs(cidade, lag, predictions_original, predictions, dates_future_original, dates_future, prev_ano, ano, 'heat')
        generate_outputs_barras_semana(cidade, lag, predictions_original, predictions, dates_future_original, dates_future, prev_ano, ano, 'heat')
    elif cold:
        generate_outputs(cidade, lag, predictions_original, predictions, dates_future_original, dates_future, prev_ano, ano, 'cold')
        generate_outputs_barras_semana(cidade, lag, predictions_original, predictions, dates_future_original, dates_future, prev_ano, ano, 'cold') 
    else:
        generate_outputs(cidade, lag, predictions_original, predictions, dates_future_original, dates_future, prev_ano, ano, '_')
        generate_outputs_barras_semana(cidade, lag, predictions_original, predictions, dates_future_original, dates_future, prev_ano, ano, '_')      
    
    return results, predictions


def generate_outputs(cidade, lag, predictions_prev, predictions, dates_prev, dates_future, prev_ano, ano, wave):
    # Converte para datetime e depois para strings "MM-DD"
    dates_prev = pd.to_datetime(dates_prev)
    dates_future = pd.to_datetime(dates_future)

    #predictions_prev = predictions_prev[:-1]

    str_dates_prev = dates_prev.dt.strftime('%m-%d')
    str_dates_future = dates_future.dt.strftime('%m-%d')
    
    colors = {'MLP': '#1f77b4', 'XGBOOST': '#ff7f0e'}

    plt.figure(figsize=(18, 12))  # mais alto para 2 plots verticais
    
    modelos = ['MLP', 'XGBOOST']
    
    for i, model in enumerate(modelos, 1):
        plt.subplot(2, 1, i)
        
        # Ajusta as previsões (remove último valor)
        preds_model = predictions[model]
        preds_prev = predictions_prev[model]
        
        # Plot dos dados reais do ano anterior
        plt.plot(str_dates_prev, preds_prev, '-',
                 label=f'{prev_ano} (Predicted)', 
                 color='black', 
                 linewidth=2)
        
        # Plot das previsões do modelo para o ano futuro
        plt.plot(str_dates_future, preds_model,
                 '-', 
                 label=f'{ano} ({model} Predicted)',
                 color=colors[model],
                 linewidth=2)
        
        # Ajusta o eixo X para mostrar apenas os dias 01 de cada mês
        tick_positions = [j for j, date in enumerate(str_dates_prev) if date.endswith('-01')]
        tick_labels = [str_dates_prev[j] for j in tick_positions]
        
        plt.xticks(tick_positions, tick_labels, rotation=45, fontsize=10)
        plt.grid(True, linestyle='--', alpha=0.3)
        
        plt.title(f'Model {model} - {cidade.capitalize()} (Lag {lag})', fontsize=10, pad=10)
        plt.xlabel('Day (MM-DD)', fontsize=10)
        plt.ylabel('Number of Hospitalizations', fontsize=10)
        plt.legend()
    
    plt.tight_layout()
    plt.savefig(f'comparacao_{prev_ano}_{ano}_{cidade}_lag{lag}_{wave}.png', dpi=300, bbox_inches='tight')
   # plt.show()

def generate_outputs_barras(cidade, lag, predictions_prev, predictions, dates_prev, dates_future, prev_ano, ano, wave):
    
    # Garantir 1D
    dates_prev = pd.to_datetime(dates_prev)
    dates_future = pd.to_datetime(dates_future)
    for model in predictions:
        predictions[model] = np.array(predictions[model]).flatten()
        predictions_prev[model] = np.array(predictions_prev[model]).flatten()

    modelos = ['MLP', 'XGBOOST']
    plt.figure(figsize=(18, 12))

    for i, model in enumerate(modelos, 1):
        preds_model = predictions[model]
        preds_model_original = predictions_prev[model]
        min_len_future = min(len(dates_future), len(preds_model))
        dates_fut = dates_future[:min_len_future]
        dates_fut_original = dates_prev[:min_len_future]
        preds_model = preds_model[:min_len_future]
        preds_model_original = preds_model_original[:min_len_future]

        df_future = pd.DataFrame({
            'date': dates_fut,
            'internacoes': preds_model
        })
        df_future['month'] = df_future['date'].dt.month
        df_prev = pd.DataFrame({
            'date': dates_fut_original,
            'internacoes': preds_model_original
        })
        df_prev['month'] = df_prev['date'].dt.month

        monthly_prev = df_prev.groupby('month')['internacoes'].sum()
        monthly_future = df_future.groupby('month')['internacoes'].sum()

        diff = monthly_future - monthly_prev
        bar_colors = ['blue' if val >= 0 else 'red' for val in diff]

        plt.subplot(2, 1, i)
        plt.bar(diff.index, diff.values, color=bar_colors)
        plt.axhline(0, color='black', linewidth=1)
        plt.xticks(range(1, 13), 
                   ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
        plt.ylabel('Difference in Hospitalizations')
        plt.title(f'Monthly Difference {ano} - {prev_ano} ({model}) - {cidade.capitalize()} (Lag {lag})')

    plt.tight_layout()
    plt.savefig(f'comparacao_barras_{prev_ano}_{ano}_{cidade}_lag{lag}_{wave}.png', dpi=300, bbox_inches='tight')
    #plt.show()

def generate_outputs_barras_semana(cidade, lag, predictions_prev, predictions, dates_prev, dates_future, prev_ano, ano, wave):
    
    # transformar em array
    dates_prev = pd.to_datetime(dates_prev)
    dates_future = pd.to_datetime(dates_future)
    for model in predictions:
        predictions[model] = np.array(predictions[model]).flatten()
        predictions_prev[model] = np.array(predictions_prev[model]).flatten()

    modelos = ['MLP', 'XGBOOST']
    plt.figure(figsize=(18, 12))

    for i, model in enumerate(modelos, 1):
        preds_model = predictions[model]
        preds_model_original = predictions_prev[model]
        min_len_future = min(len(dates_future), len(preds_model))
        dates_fut = dates_future[:min_len_future]
        dates_fut_original = dates_prev[:min_len_future]
        preds_model = preds_model[:min_len_future]
        preds_model_original = preds_model_original[:min_len_future]

        df_future = pd.DataFrame({
            'date': dates_fut,
            'internacoes': preds_model
        })
        df_future['week'] = df_future['date'].dt.isocalendar().week

        df_prev = pd.DataFrame({
            'date': dates_fut_original,
            'internacoes': preds_model_original
        })
        df_prev['week'] = df_prev['date'].dt.isocalendar().week


        # Totais anuais
        total_prev = df_prev['internacoes'].sum()
        total_future = df_future['internacoes'].sum()

        # Agregar por semana
        weekly_prev = df_prev.groupby('week')['internacoes'].sum()
        weekly_future = df_future.groupby('week')['internacoes'].sum()

        # Preencher semanas faltantes com 0
        all_weeks = range(1, 54)
        weekly_prev = weekly_prev.reindex(all_weeks, fill_value=0)
        weekly_future = weekly_future.reindex(all_weeks, fill_value=0)

        # Diferença percentual
        with np.errstate(divide='ignore', invalid='ignore'):
            diff_pct = ((weekly_future - weekly_prev) / weekly_prev.replace(0, np.nan)) * 100
            diff_pct = diff_pct.fillna(0)  # se semana anterior tinha 0, fica 0

        # Cores
        bar_colors = ['blue' if val >= 0 else 'red' for val in diff_pct]

        # Plot
        plt.subplot(2, 1, i)
        bars = plt.bar(diff_pct.index, diff_pct.values, color=bar_colors)
        plt.axhline(0, color='black', linewidth=1)
        plt.xticks(range(1, 54, 2))  # marcar de 2 em 2 semanas
        plt.ylabel('Difference (%)')
        plt.title(f'{model} - Weekly Difference {ano} vs {prev_ano} - {cidade.capitalize()} (Lag {lag})')

        # Legenda
        plt.legend(
            [plt.Rectangle((0, 0), 1, 1, color='blue'),
             plt.Rectangle((0, 0), 1, 1, color='red')],
            ['Increase', 'Decrease'],
            loc='upper left'
        )

        
        plt.text(0.99, 0.95, 
                 f'{prev_ano}: {total_prev:.0f}\n{ano}: {total_future:.0f}',
                 transform=plt.gca().transAxes,
                 ha='right', va='top',
                 fontsize=12,
                 bbox=dict(facecolor='white', alpha=0.7, edgecolor='black'))

    plt.tight_layout()
    plt.savefig(f'comparacao_barras_semana_{prev_ano}_{ano}_{cidade}_lag{lag}_{wave}.png', dpi=300, bbox_inches='tight')
   # plt.show()

anos = [2022, 2023, 2024, 2030, 2050, 2099]
anos_prev = [2030, 2050, 2099]

if __name__ == '__main__':
    for lag in range(0, 1):
        main_all_methods('curitiba', 'pm2.5_alt', lag,2024 ,2050,cold=False,heat=False,pm=False)
        # for ano in anos:
        #     for ano_prev in anos_prev:
        #         if ano == anos_prev:
        #             main_all_methods('curitiba', 'pm2.5_alt', lag,ano,ano_prev,cold=False,heat=True,pm=False)
        #             main_all_methods('curitiba', 'pm2.5_alt', lag,ano,ano_prev,cold=True,heat=False,pm=False)
        #         elif ano < 2030:
        #             main_all_methods('curitiba', 'pm2.5_alt', lag,ano,ano_prev,cold=False,heat=True,pm=False)
        #             main_all_methods('curitiba', 'pm2.5_alt', lag,ano,ano_prev,cold=True,heat=False,pm=False)
        #             main_all_methods('curitiba', 'pm2.5_alt', lag,ano,ano_prev,cold=False,heat=False,pm=False)

