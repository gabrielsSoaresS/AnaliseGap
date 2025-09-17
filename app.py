import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

# === Carregar os dados ===
arquivo = r"C:\Users\soare\OneDrive\Documentos\Data Science\AnaliseGap\WIN$N_M1.csv"

# Lê o CSV
tabela = pd.read_csv(arquivo, sep="\t")
tabela.columns = [c.strip().replace("<","").replace(">","") for c in tabela.columns]

# Criar coluna datetime
tabela["DATETIME"] = pd.to_datetime(
    tabela["DATE"].astype(str) + " " + tabela["TIME"].astype(str),
    format="%Y.%m.%d %H:%M:%S"
)

tabela = tabela.sort_values(by="DATETIME").reset_index(drop=True)
colunas = ["DATETIME", "OPEN", "HIGH", "LOW", "CLOSE", "VOL"]
tabela = tabela[colunas]

# Identificar Gaps
tabela["Prev_Close"] = tabela["CLOSE"].shift(1)
tabela["Gap"] = tabela["OPEN"] - tabela["Prev_Close"]
tabela["Gap%"] = (tabela["Gap"] / tabela["Prev_Close"]) * 100
tabela["Gap_Direcao"] = tabela["Gap"].apply(lambda x: "Alta" if x > 0 else ("Baixa" if x < 0 else "Sem Gap"))

gaps = tabela[tabela["Gap_Direcao"] != "Sem Gap"].copy()

# === Streamlit ===
st.title("📊 Análise de Gaps - WIN$N_M1")

# Mostrar dados
if st.checkbox("Mostrar tabela completa"):
    st.dataframe(gaps)

# Estatísticas
st.subheader("📈 Estatísticas dos Gaps")
st.write(gaps[["Gap", "Gap%", "Gap_Direcao"]].describe())

# Histograma dos gaps
st.subheader("📊 Distribuição dos Gaps")
fig, ax = plt.subplots()
sns.histplot(gaps["Gap"], bins=50, ax=ax)
st.pyplot(fig)

# Boxplot
st.subheader("📦 Boxplot dos Gaps")
fig, ax = plt.subplots()
sns.boxplot(x=gaps["Gap"], ax=ax)
st.pyplot(fig)

# Frequência por direção
st.subheader("📊 Frequência dos Gaps por Direção")
freq = gaps["Gap_Direcao"].value_counts()
st.bar_chart(freq)
