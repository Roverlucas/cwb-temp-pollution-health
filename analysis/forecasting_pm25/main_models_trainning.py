import csv
import os
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import shap
from sklearn.discriminant_analysis import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, mean_absolute_percentage_error
from sklearn.model_selection import train_test_split
from tqdm import tqdm
from xgboost import XGBRegressor

#from GRU_model import train_gru_pytorch
from MLP_model import MLP_model
from Transformer_model import train_transformer_pytorch
#from UnorganizedMachines import EchoStateNetwork, ExtremeLearningMachine
#from lstm_model import train_lstm_pytorch
from UnorganizedMachines import ExtremeLearningMachine
from xgboost_model import run_xgboost_model

def split_temporal(X, y, train_size=0.7, val_size=0.15):
    n = len(X)
    train_end = int(train_size * n)
    val_end = train_end + int(val_size * n)

    X_train, y_train = X[:train_end], y[:train_end]
    X_val, y_val = X[train_end:val_end], y[train_end:val_end]
    X_test, y_test = X[val_end:], y[val_end:]

    return X_train, y_train, X_val, y_val, X_test, y_test

def lagApplication(df, pollutant, dias=1):

    df = df.copy()  # Evita modificar o original
    
    # Aplica o shift apenas na coluna Frequencia
    df[pollutant] = df[pollutant].shift(-dias)
    
    # Remove as linhas com NaN geradas pelo shift
    df = df.dropna(subset=[pollutant])
    
    return df

def load_and_prepare_data(Pollutant, Humid, Temp, Week_day, Holiday, internacoes_file, pollutant, lag=0):
    # (Mantido igual ao seu código original)
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
    df.drop(columns=['Data'], inplace=True)

    X = df.drop(columns=['Hospitalizations'])
    y = df['Hospitalizations']
    return X, y

def evaluate_model(best_models, model_type, X_train, X_val, X_test, y_train, y_val, y_test_inv, y_test, scaler_y):
    
    # Combina treino e validação
    X_train_val = np.concatenate((X_train, X_val), axis=0)
    y_train_val = np.concatenate((y_train, y_val), axis=0)
    
    # Retreina
    # if model_type == 'LSTM':
    #     y_pred = train_lstm_pytorch(X_train_val, y_train_val.ravel(), X_test, y_test,
    #                               hidden_size=best_models['LSTM']['n'], 
    #                               num_layers=1, epochs=100, lr=0.001, batch_size=20)
    # elif model_type == 'GRU':
    #     y_pred = train_gru_pytorch(X_train_val, y_train_val.ravel(), X_test, y_test,
    #                   hidden_size=best_models['GRU']['n'], num_layers=1, epochs=100,
    #                   lr=0.001, batch_size=20)

    if model_type == 'MLP':
        final_model = MLP_model(hidden_layer_sizes=[best_models['MLP']['n']], max_iter=1000)
        y_train_val_fit = y_train_val.ravel()  
        final_model.fit(X_train_val, y_train_val_fit,)
    elif model_type == 'ELM':
        final_model = ExtremeLearningMachine(n_hidden=best_models['ELM']['n'])
        y_train_val_fit = y_train_val.ravel()  
        final_model.fit(X_train_val, y_train_val_fit, 'regularization')
    elif model_type == 'XGBOOST':
        final_model = XGBRegressor(n_estimators=best_models['XGBOOST']['n'], 
                                    max_depth=5, learning_rate=0.1,
                                    random_state=42)
        y_train_val_fit = y_train_val.ravel()
        final_model.fit(X_train_val, y_train_val_fit)

    y_pred = final_model.predict(X_test)
    
    # Transformação e métricas
    y_pred_inv = scaler_y.inverse_transform(y_pred.reshape(-1, 1))
    return {
        'mse': mean_squared_error(y_test_inv, y_pred_inv),
        'rmse': np.sqrt(mean_squared_error(y_test_inv, y_pred_inv)),
        'mae': mean_absolute_error(y_test_inv, y_pred_inv),
        'mape': mean_absolute_percentage_error(y_test_inv, y_pred_inv),
        'y_pred': y_pred_inv.flatten()
    }

def run_model_best(cidade, pollutant, lag, hidden_range) :
    # Carrega e prepara os dados
    Pollutant = f'transformer_{cidade}_{pollutant}.csv'
    #Humid = f'transformer_{cidade}_humidity.csv'
    #Temp = f'transformer_{cidade}_temperature.csv'
    Humid = f'umidade_2022_2024.csv'
    Temp = f'temperatura_2022_2024.csv'
    Week_day = 'dia_da_semana.csv'
    Holiday = 'feriados.csv'
    internacoes_file = f'internacoes_{cidade}.csv'

    X, y = load_and_prepare_data(Pollutant, Humid, Temp, Week_day, Holiday, internacoes_file, pollutant, lag)

    # Normalização
    scaler_X = StandardScaler()
    X_scaled = scaler_X.fit_transform(X)
    scaler_y = StandardScaler()
    y_scaled = scaler_y.fit_transform(y.values.reshape(-1, 1))

    # Divisão temporal
    X_train, y_train, X_val, y_val, X_test, y_test = split_temporal(X_scaled, y_scaled)
    
    # Preparação dos dados para métricas
    y_val_inv = scaler_y.inverse_transform(y_val)
    y_test_inv = scaler_y.inverse_transform(y_test)

    # Dicionário para armazenar os melhores modelos e parâmetros
    # best_models = {
    #     'ELM': {'model': None, 'n': None, 'mse_val': float('inf')},
    #     'ELM_pinv': {'model': None, 'n': None, 'mse_val': float('inf')},
    #     'ESN': {'model': None, 'n': None, 'mse_val': float('inf')},
    #     'MLP': {'model': None, 'n': None, 'mse_val': float('inf')},
    #     'XGBOOST': {'model': None, 'n': None, 'mse_val': float('inf')},
    #     'LSTM': {'model': None, 'n': None, 'mse_val': float('inf')},
    #     'GRU': {'model': None, 'n': None, 'mse_val': float('inf')},
    #     'TRANSFORMER': {'model': None, 'n': None, 'mse_val': float('inf')}

    # }
    best_models = {
        'ELM': {'model': None, 'n': None, 'mape_val': float('inf')},
        'MLP': {'model': None, 'n': None, 'mape_val': float('inf')},
        'XGBOOST': {'model': None, 'n': None, 'mape_val': float('inf')},

    }

    # --- Seleção de Hiperparâmetros (usando validação) ---
    for n in tqdm(hidden_range, desc="Ajustando hiperparâmetros"):
        # --- ELM ---
        elm = ExtremeLearningMachine(n_hidden=n)
        elm.fit(X_train, y_train, 'regularization')
        y_pred_val = elm.predict(X_val)
        y_pred_val_inv = scaler_y.inverse_transform(y_pred_val)
        mape_val = mean_absolute_percentage_error(y_val_inv, y_pred_val_inv)
        
        if mape_val < best_models['ELM']['mape_val']:
            best_models['ELM'] = {'model': elm, 'n': n, 'mape_val': mape_val}

        # # --- ELM pinv---
        # elm = ExtremeLearningMachine(n_hidden=n)
        # elm.fit(X_train, y_train, 'pinv')
        # y_pred_val = elm.predict(X_val)
        # y_pred_val_inv = scaler_y.inverse_transform(y_pred_val)
        # mse_val = mean_squared_error(y_val_inv, y_pred_val_inv)
        
        # if mse_val < best_models['ELM_pinv']['mse_val']:
        #     best_models['ELM_pinv'] = {'model': elm, 'n': n, 'mse_val': mse_val}

        # # --- ESN ---
        # esn = EchoStateNetwork(n_reservoir=n, spectral_radius=0.95)
        # esn.fit(X_train, y_train, volterra=True, pca=True, pca_components=2)
        # y_pred_val = esn.predict(X_val)
        # y_pred_val_inv = scaler_y.inverse_transform(y_pred_val)
        # mse_val = mean_squared_error(y_val_inv, y_pred_val_inv)
        
        # if mse_val < best_models['ESN']['mse_val']:
        #     best_models['ESN'] = {'model': esn, 'n': n, 'mse_val': mse_val}

        # --- MLP ---
        mlp = MLP_model(hidden_layer_sizes=[n], max_iter=1000)
        mlp.fit(X_train, y_train.ravel())
        y_pred_val = mlp.predict(X_val)
        y_pred_val_inv = scaler_y.inverse_transform(y_pred_val.reshape(-1, 1))
        mape_val = mean_absolute_percentage_error(y_val_inv, y_pred_val_inv)
        
        if mape_val < best_models['MLP']['mape_val']:
            best_models['MLP'] = {'model': mlp, 'n': n, 'mape_val': mape_val}

        # --- XGBoost ---
        model = XGBRegressor(n_estimators=n, max_depth=5, learning_rate=0.1, random_state=42)
        model.fit(X_train, y_train.ravel())
        y_pred_val = model.predict(X_val)
        y_pred_val_inv = scaler_y.inverse_transform(y_pred_val.reshape(-1, 1))
        mape_val = mean_absolute_percentage_error(y_val_inv, y_pred_val_inv)
        
        if mape_val < best_models['XGBOOST']['mape_val']:
            best_models['XGBOOST'] = {'model': model, 'n': n, 'mape_val': mape_val}

        # # --- LSTM ---
        # y_pred_val = train_lstm_pytorch(X_train, y_train.ravel(), X_val, y_val, 
        #                                hidden_size=n, num_layers=1, epochs=100, 
        #                                lr=0.001, batch_size=20)
        # y_pred_val_inv = scaler_y.inverse_transform(y_pred_val.reshape(-1, 1))
        # mse_val = mean_squared_error(y_val_inv, y_pred_val_inv)

        # if mse_val < best_models['LSTM']['mse_val']:
        #     best_models['LSTM'] = {'model': None, 'n': n, 'mse_val': mse_val} 

        # # GRU
        # y_pred_val = train_gru_pytorch(X_train, y_train.ravel(), X_val, y_val,
        #               hidden_size=n, num_layers=1, epochs=100,
        #               lr=0.001, batch_size=20)
        # y_pred_val_inv = scaler_y.inverse_transform(y_pred_val.reshape(-1, 1))
        # mse_val = mean_squared_error(y_val_inv, y_pred_val_inv)

        # if mse_val < best_models['GRU']['mse_val']:
        #     best_models['GRU'] = {'model': None, 'n': n, 'mse_val': mse_val} 

    
    results = {}
    
    
    # Avalia todos os modelos no teste
    #for model_type in ['ELM', 'ELM_pinv', 'ESN', 'MLP', 'XGBOOST', 'LSTM', 'GRU', 'TRANSFORMER']:
    for model_type in [ 'ELM', 'MLP', 'XGBOOST']:
        model_info = best_models[model_type]
        model_results = evaluate_model(best_models, model_type, X_train, X_val, X_test, y_train, y_val, y_test_inv, y_test, scaler_y)
        
        results[f'{model_type}'] = model_results['mse']
        results[f'{model_type}_RMSE'] = model_results['rmse']
        results[f'{model_type}_MAE'] = model_results['mae']
        results[f'{model_type}_MAPE'] = model_results['mape']
        results[f'{model_type}_N'] = model_info['n']
        results[f'y_pred_{model_type.lower()}'] = model_results['y_pred']

    results['y_test'] = y_test_inv.flatten()
    
    return results


def main_all_methods(cidade, pollutant, lag):
    output = []
    results = run_model_best(cidade, pollutant, lag, hidden_range=range(200, 201, 1))
    if results:
        header = f"--- Results for {cidade.upper()} - Lag: {lag} ---"
        output.append(header)
        for model in ["ELM", 'MLP', 'XGBOOST']:
            n = results.get(f'{model}_N', None)
            mse = results.get(model, None)
            rmse = results.get(f'{model}_RMSE', None)
            mae = results.get(f'{model}_MAE', None)
            mape = results.get(f'{model}_MAPE', None)
            line = (f"{model}: neurons={n}, MSE={mse}, RMSE={rmse}, MAE={mae}, MAPE={mape}")
            output.append(line)
        output.append("-" * 70)

    with open(f'resultados_{cidade}.csv', 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        for line in output:
            writer.writerow([line])

    if 'y_test' in results:
        y_test = results['y_test']
        models = ['ELM', 'MLP', 'XGBOOST']
        fig, axs = plt.subplots(3, 1, figsize=(12, 15), sharex=True)
        axs = axs.flatten()
        for idx, model in enumerate(models):
            pred_key = f'y_pred_{model.lower()}'
            pred = results.get(pred_key, None)
            if pred is not None:
                axs[idx].plot(y_test, label='Observed', linewidth=2)
                axs[idx].plot(pred, label=model, linewidth=2)
                axs[idx].legend(loc='upper right', framealpha=1)
                axs[idx].grid(True, alpha=0.3)
                axs[idx].set_ylabel('Hospitalizations', fontsize=10)
            else:
                axs[idx].text(0.5, 0.5, f'No prediction for {model}', ha='center', va='center')
                axs[idx].set_axis_off()
        axs[-1].set_xlabel('Samples', fontsize=12)
        plt.tight_layout()
        plt.subplots_adjust(top=0.94)
        plt.savefig(f'Predictions_{cidade}_LAG_{lag}.png', dpi=300, bbox_inches='tight')

    plt.figure(figsize=(18, 12))
    plt.suptitle(f'Model Performance by Imputation Method - {cidade.capitalize()}', y=1.02, fontsize=14)

    metrics = ['MSE', 'RMSE', 'MAE', 'MAPE']
    models = ['ELM', 'MLP', 'XGBOOST']
    colors = ['#1f77b4', "#83fff5", '#ff7f0e']

    data = {metric: [] for metric in metrics}
    for metric in metrics:
        for model in models:
            key = f'{model}_{metric}' if metric != 'MSE' else model
            value = results.get(key, np.nan)
            data[metric].append(value)

    fig, axs = plt.subplots(2, 2, figsize=(12, 10))
    axs = axs.flatten()
    for i, metric in enumerate(metrics):
        ax = axs[i]
        values = data[metric]
        x = np.arange(len(models))
        ax.bar(x, values, color=colors, tick_label=models)
        ax.set_title(metric, fontsize=12)
        ax.set_ylabel("Value")
        ax.set_ylim(bottom=0)
        ax.grid(True, axis='y', alpha=0.3)

    plt.suptitle(f'Model Performance - {cidade.capitalize()} (LAG {lag})', fontsize=14)
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig(f'Metrics_{cidade}_LAG_{lag}.png', dpi=300, bbox_inches='tight')
    #plt.show()

    


def plot_shap_xgboost(model, X, feature_names, cidade, lag, suffix=''):
    """
    Gera gráficos SHAP para o modelo XGBoost
    """
    explainer = shap.Explainer(model)
    shap_values = explainer(X)

    # Summary plot (beeswarm)
    plt.figure()
    shap.summary_plot(
        shap_values,
        X,
        feature_names=feature_names,
        show=False
    )
    plt.title(f'SHAP Summary - XGBoost - {cidade.capitalize()} (Lag {lag})')
    plt.savefig(
        f'shap_summary_xgb_{cidade}_lag{lag}{suffix}.png',
        dpi=300,
        bbox_inches='tight'
    )
    plt.close()

    # Bar plot (importância média)
    plt.figure()
    shap.summary_plot(
        shap_values,
        X,
        feature_names=feature_names,
        plot_type='bar',
        show=False
    )
    plt.title(f'SHAP Importance - XGBoost - {cidade.capitalize()} (Lag {lag})')
    plt.savefig(
        f'shap_bar_xgb_{cidade}_lag{lag}{suffix}.png',
        dpi=300,
        bbox_inches='tight'
    )
    plt.close()



if __name__ == '__main__':
    for i in range(0,1):
        main_all_methods('curitiba', 'pm2.5_alt', i)

