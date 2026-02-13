############################
# Simulação de Monte Carlo #
############################

import pandas as pd
import numpy as np

def monte_carlo_heatwaves(ano, n_sims=500, n_waves=5, dur_range=(3,7), temp_increase=(2,5), heat=True):
    temp_csv=f'temperatura_{ano}.csv'
    hum_csv=f'umidade_{ano}.csv'

    # lê temperatura
    df_temp = pd.read_csv(temp_csv, parse_dates=['Data'])
    # lê umidade relativa
    df_hum = pd.read_csv(hum_csv, parse_dates=['Data'])
    # merge
    df = pd.merge(df_temp, df_hum, on='Data', how='inner')

    # cria coluna com dia do ano (1-365)
    df["dayofyear"] = df["Data"].dt.dayofyear
    ndays = len(df)

    # --- define intervalos por estação ---
    # usando datas típicas para hemisfério sul
    summer = np.concatenate([np.arange(355, 366), np.arange(1, 80)])   # verão
    autumn = np.arange(80, 172)                                        # outono
    winter = np.arange(172, 266)                                       # inverno
    spring = np.arange(266, 355)                                       # primavera

    if heat:
        allowed_days = autumn#np.concatenate([autumn, winter])   # calor → outono + inverno
    else:
        allowed_days = np.concatenate([spring, autumn])  

    # resultados
    sim_results = []

    for sim in range(1):
        df_sim = df.copy()

        # sorteia inícios dentro da estação escolhida
        possible_starts = df.index[df["dayofyear"].isin(allowed_days)].values
        start_days = np.random.choice(possible_starts, n_waves, replace=False)
        print(start_days)

        for start in start_days:
            duration = np.random.randint(dur_range[0], dur_range[1]+1)
            intensity = np.random.uniform(temp_increase[0], temp_increase[1])
            end = min(start + duration, ndays)

            if heat:
                # onda de calor → ↑ temp, ↓ umidade
                df_sim.loc[start:end-1, 'temperature'] = np.clip(df_sim.loc[start:end-1, 'temperature'] + intensity, -1, 40)
                df_sim.loc[start:end-1, 'humidity'] = np.maximum(0, df_sim.loc[start:end-1, 'humidity'] - intensity*2)
            else:
                # onda de frio → ↓ temp, ↑ umidade
                df_sim.loc[start:end-1, 'temperature'] = np.clip(df_sim.loc[start:end-1, 'temperature'] - intensity, -1, 40)
                df_sim.loc[start:end-1, 'humidity'] = np.clip(df_sim.loc[start:end-1, 'humidity'] + intensity, 0, 99)

        sim_results.append(df_sim)

    # salva apenas a 1ª simulação
    if heat:
        sim_results[0][["Data", "humidity"]].to_csv(f'umidade_wave_{ano}_heat.csv', index=False)
        sim_results[0][["Data", "temperature"]].to_csv(f'temperatura_wave_{ano}_heat.csv', index=False)
    else:
        sim_results[0][["Data", "humidity"]].to_csv(f'umidade_wave_{ano}_cold.csv', index=False)
        sim_results[0][["Data", "temperature"]].to_csv(f'temperatura_wave_{ano}_cold.csv', index=False)

    return sim_results

# monte_carlo_heatwaves(
#     ano=2050,
#     n_sims=1,
#     n_waves=3,
#     dur_range=(5,7),
#     temp_increase=(12,18),
#     heat=False
# )


def simulation_pm(poluente, n_sims=500, n_waves=5, dur_range=(3,7), temp_increase=(2,5), ano=2025):

    pm_csv=f'transformer_curitiba_{poluente}.csv'
    # lê temperatura
    df_pm = pd.read_csv(pm_csv, parse_dates=['Data'])
    df_pm = df_pm.tail(365).reset_index(drop=True)

    # Copia a original, pega só a data e número de dias no período
    df = df_pm.copy()                        
    ndays = len(df)                  

    # usando datas típicas para hemisfério sul
    summer = np.concatenate([np.arange(355, 366), np.arange(1, 80)])   # verão
    autumn = np.arange(80, 172)                                        # outono
    winter = np.arange(172, 266)                                       # inverno
    spring = np.arange(266, 355)                                       # primavera

    allowed_days = np.concatenate([summer,spring])  
   

    # resultados da simulação
    sim_results = []                     

    # Loop para cada simulação Monte Carlo
    for sim in range(n_sims):
        df_sim = df.copy()   
        # aleatoriamente no período completo
        start_days = np.random.choice(allowed_days, n_waves, replace=False)
        print(start_days)
        # cada onda de calor
        for start in start_days:
            # aleatoriedade de duração
            duration = np.random.randint(dur_range[0], dur_range[1]+1)
            # aleatoriedade da intensidade (em °C)
            intensity = np.random.uniform(temp_increase[0], temp_increase[1])
            # SEgurança. Não deixa ultrapassar o valor máximo dos dias
            end = min(start+duration, ndays)
            
            df_sim.loc[start:end-1, poluente] = np.clip(df_sim.loc[start:end-1, poluente] + intensity, 0, 300)

            # diminui RH durante a onda de calor
            #df_sim.loc[start:end-1, 'humidity'] = np.maximum(0, df_sim.loc[start:end-1, 'humidity'] - intensity*2) 

        # Adiciona aos resultados
        sim_results.append(df_sim)

    sim_results[0][["Data", poluente]].to_csv(f'transformer_curitiba_{poluente}_{ano}_mod.csv', index=False)

simulation_pm(
    poluente='pm2.5_alt',
    n_sims=1,
    n_waves=2,
    dur_range=(7,14),
    temp_increase=(70, 100),
    ano=2050
)


##############################
# Simulação Monte Carlo Real #
##############################


def monte_carlo_heatwaves_real(temp_csv, hum_csv, n_sims=1000, min_days=3, perc_threshold=95, phi=0.8):


    # Lê CSVs
    df_temp = pd.read_csv(temp_csv, parse_dates=['Data'])
    df_hum = pd.read_csv(hum_csv, parse_dates=['Data'])

    # Merge pelo tempo
    df = pd.merge(df_temp, df_hum, on='Data', how='inner')
    ndays = len(df)

    # Calcula percentil de temperatura para critério de onda de calor
    temp_thresh = np.percentile(df['temperature'], perc_threshold)

    sim_results = []
    wave_stats = []

    mu = df['temperature'].mean()
    sigma = df['temperature'].std()

    for sim in range(n_sims):
        tas_sim = np.zeros(ndays)
        RH_sim = np.zeros(ndays)

        # Inicializa primeiro dia
        tas_sim[0] = np.random.normal(mu, sigma)
        RH_sim[0] = np.random.normal(df['humidity'].mean(), df['humidity'].std())

        # AR(1) diário
        for t in range(1, ndays):
            tas_sim[t] = mu + phi*(tas_sim[t-1] - mu) + np.random.normal(0, sigma*np.sqrt(1-phi**2))
            RH_sim[t] = np.clip(np.random.normal(df['humidity'].mean(), df['humidity'].std()), 0, 100)

        df_sim = df.copy()
        df_sim['temperature'] = tas_sim
        df_sim['humidity'] = RH_sim

        # Detecta ondas de calor
        heatwave_flag = tas_sim >= temp_thresh
        waves = []
        count = 0
        for flag in heatwave_flag:
            if flag:
                count += 1
            else:
                if count >= min_days:
                    waves.append(count)
                count = 0
        if count >= min_days:
            waves.append(count)

        sim_results.append(df_sim)
        wave_stats.append({
            'n_waves': len(waves),
            'durations': waves,
            'mean_duration': np.mean(waves) if waves else 0,
            'max_temperature': tas_sim.max()
        })

    # Salva a primeira simulação em CSV
    sim_results[0][['Data', 'temperature']].to_csv('temperatura_wave_sim1.csv', index=False)
    sim_results[0][['Data', 'humidity']].to_csv('umidade_wave_sim1.csv', index=False)

    return sim_results, wave_stats

# # Exemplo de execução
# sim_results, wave_stats = monte_carlo_heatwaves(
#     temp_csv='temperatura_2099.csv',
#     hum_csv='umidade_2099.csv',
#     n_sims=100,
#     min_days=3,
#     perc_threshold=95,
#     phi=0.8
# )

# print("Número de ondas de calor na primeira simulação:", wave_stats[0]['n_waves'])
# print("Duração média das ondas:", wave_stats[0]['mean_duration'])
# print("Temperatura máxima da simulação:", wave_stats[0]['max_temperature'])
