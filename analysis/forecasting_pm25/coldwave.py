import pandas as pd

# Carregar o CSV
df = pd.read_csv("base_dados_completa_coldwave.csv", parse_dates=["time_stamp"])

df = df.sort_values("time_stamp").reset_index(drop=True)

# Identificar ondas de frio contínuas
df["coldwave_group"] = (df["is_coldwave"].diff().ne(0)).cumsum()
# filtrar apenas os grupos que são de frio
coldwave_groups = df[df["is_coldwave"] == 1].groupby("coldwave_group")

# Lista para guardar estatísticas
waves_stats = []

for g, group in coldwave_groups:
    duration = len(group)  # dias de onda de frio
    
    # estatísticas internas da onda
    stats = group[["t_max", "t_med", "t_min"]].agg(["mean", "std"])
    
    # dia anterior ao início
    first_day_idx = group.index.min()
    if first_day_idx > 0:
        prev_day = df.loc[first_day_idx - 1, ["t_max", "t_med", "t_min"]]
        drops = 100 * (group.iloc[0][["t_max", "t_med", "t_min"]] - prev_day) / prev_day
    else:
        drops = pd.Series({"t_max": None, "t_med": None, "t_min": None})
    
    waves_stats.append({
        "group": g,
        "duration_days": duration,
        "t_max_mean": stats.loc["mean", "t_max"],
        "t_max_std": stats.loc["std", "t_max"],
        "t_med_mean": stats.loc["mean", "t_med"],
        "t_med_std": stats.loc["std", "t_med"],
        "t_min_mean": stats.loc["mean", "t_min"],
        "t_min_std": stats.loc["std", "t_min"],
        "drop_t_max_%": drops["t_max"],
        "drop_t_med_%": drops["t_med"],
        "drop_t_min_%": drops["t_min"]
    })

# Criar DataFrame final
coldwave_summary = pd.DataFrame(waves_stats)

print(coldwave_summary)
coldwave_summary.to_csv("coldwave_summary.csv", index=False)