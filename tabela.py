import pandas as pd
import statistics
import matplotlib.pyplot as plt
import seaborn

# === 1) Ler o arquivo original ===
# Troque o caminho caso seu arquivo esteja em outra pasta
arquivo = "WIN$N_M1.csv"

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

#Gera o boxplot
seaborn.boxplot(tabela)
plt.show()
