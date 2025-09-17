import pandas as pd
import statistics
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# === 1) Ler o arquivo original ===
# Troque o caminho caso seu arquivo esteja em outra pasta
arquivo = r"C:\Users\soare\OneDrive\Documentos\Data Science\AnaliseGap\WIN$N_M1.csv"

# O arquivo vem separado por tabulação (\t)
tabela = pd.read_csv(arquivo, sep="\t")

# === 2) Limpar nome das colunas ===
# Remove os < e >
tabela.columns = [c.strip().replace("<","").replace(">","") for c in tabela.columns]

# Agora deve ter colunas tipo: DATE, TIME, OPEN, HIGH, LOW, CLOSE, VOL

# === 3) Criar coluna de data e hora ===
tabela["DATETIME"] = pd.to_datetime(
    tabela["DATE"].astype(str) + " " + tabela["TIME"].astype(str),
    format="%Y.%m.%d %H:%M:%S"
)

# === 4) Ordenar pelo tempo ===
tabela = tabela.sort_values(by="DATETIME").reset_index(drop=True)

# === 5) Selecionar e reorganizar colunas ===
# Mantendo só o que interessa para análise
colunas = ["DATETIME", "OPEN", "HIGH", "LOW", "CLOSE", "VOL"]
tabela = tabela[colunas]

# === 6) Salvar em formato limpo ===
saida = "WIN_M1_normalizado.csv"
tabela.to_csv(saida, index=False)

print("✅ Arquivo tratado e salvo em:", saida)

# Identificando os Gaps
tabela['Prev_Close'] = tabela['CLOSE'].shift(1)

tabela['Gap'] = tabela['OPEN'] - tabela['Prev_Close']
tabela['Gap%'] = (tabela["Gap"]/tabela["Prev_Close"]) *100

tabela['Gap_Direçao'] = tabela["Gap"].apply(lambda x: 'Alta' if x > 0 else ('Baixa' if x < 0 else 'sem gap'))

#Filtra apenas os que tem gap
gaps = tabela[tabela['Gap_Direçao'] != 'sem gap'].copy()

print(gaps[['DATETIME', 'Prev_Close', 'OPEN', 'Gap', 'Gap%', 'Gap_Direçao']])

#Apresenta as principais estatisticas da base de dados
tabela_detalhes = tabela.describe()
print(tabela_detalhes)

# --- identificar fechamento dos gaps ---
gaps["Fechou_Gap"] = False
gaps["Tempo_Fecho"] = np.nan

for i, row in gaps.iterrows():
    ref_price = row["Prev_Close"]
    start_time = row["DATETIME"]

    # pegar candles seguintes até o gap fechar
    futuros = tabela.loc[tabela["DATETIME"] > start_time]

    if row["Gap"] > 0:  # gap de alta
        fechado = futuros[futuros["LOW"] <= ref_price]
    else:  # gap de baixa
        fechado = futuros[futuros["HIGH"] >= ref_price]

    if not fechado.empty:
        gaps.at[i, "Fechou_Gap"] = True
        fechamento = fechado.iloc[0]["DATETIME"]
        gaps.at[i, "Tempo_Fecho"] = (fechamento - start_time).total_seconds() / 60.0

# --- amplitude absoluta ---
gaps["Amplitude"] = gaps["Gap"].abs()

# --- faixas de amplitude ---
bins = [-np.inf, 5, 10, 20, 50, 100, np.inf]
labels = ["<=5", "6-10", "11-20", "21-50", "51-100", "100+"]

gaps["Faixa"] = pd.cut(gaps["Amplitude"], bins=bins, labels=labels)

# --- resumo por faixa ---
resumo = gaps.groupby("Faixa").agg(
    total_gaps=("Gap", "count"),
    pct_total=("Gap", lambda x: 100*len(x)/len(gaps)),
    prob_fecho=("Fechou_Gap", "mean"),
    mediana_amplitude=("Amplitude", "median"),
    mediana_tempo_fecho=("Tempo_Fecho", "median")
).reset_index()

print(resumo)
