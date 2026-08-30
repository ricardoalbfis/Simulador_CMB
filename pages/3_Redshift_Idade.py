import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import quad

# Configuração da página
st.set_page_config(page_title="Idade do Universo vs Redshift", layout="wide")
st.title("Evolução Temporal: Idade do Universo x Redshift ⏳")

st.markdown("""
Esta ferramenta plota a **Idade do Universo no eixo X** (em bilhões de anos - Gyr) e o **Redshift ($z$) no eixo Y**. 
O gráfico compara o **Modelo Atual** (ajustado pelos seletores) com o **Modelo de Referência Padrão** em outra cor para facilitar a análise de variação.
""")

# Painel de controle no menu lateral (Atualização em tempo real)
st.sidebar.header("Parâmetros Cosmológicos (Modelo Atual)")
H0 = st.sidebar.slider("H0 (Constante de Hubble [km/s/Mpc]):", 50.0, 85.0, 67.4, 0.5)
Omega_m = st.sidebar.slider("Ωm (Densidade Total de Matéria):", 0.15, 0.45, 0.315, 0.005)

# Constantes físicas
sec_por_ano = 365.25 * 24 * 3600
anos_por_gyr = 1e9

def inv_E_z(z, Om):
    Ode = 1.0 - Om
    return 1.0 / ((1.0 + z) * np.sqrt(Om * (1.0 + z)**3 + Ode))

@st.cache_data
def calcular_idade_redshift(H0_val, Om_val):
    H0_s_local = H0_val * 1000.0 / (3.085677581e22)
    z_array = np.linspace(0, 20, 500)
    idades = []
    
    for z in z_array:
        integral, _ = quad(inv_E_z, z, np.inf, args=(Om_val,))
        tempo_segundos = integral / H0_s_local
        tempo_gyr = tempo_segundos / (sec_por_ano * anos_por_gyr)
        idades.append(tempo_gyr)
        
    return z_array, np.array(idades)

# Executa o cálculo para o modelo atual e para o modelo de referência fixo
z_vals, idade_vals_atual = calcular_idade_redshift(H0, Omega_m)
_, idade_vals_ref = calcular_idade_redshift(67.4, 0.315) # Valores originais de referência

# Plota o gráfico (Idade no X, Redshift no Y)
fig, ax = plt.subplots(figsize=(10, 5))
plt.style.use('dark_background')

# Linha de referência original (tracejada em âmbar)
ax.plot(idade_vals_ref, z_vals, color='#fbbf24', linestyle='--', linewidth=2.0, alpha=0.8, label='Modelo de Referência ($H_0=67.4, \\Omega_m=0.315$)')

# Linha do modelo atual ajustado (sólida em azul claro)
ax.plot(idade_vals_atual, z_vals, color='#38bdf8', linewidth=2.5, label=f'Modelo Atual ($H_0={H0}, \\Omega_m={Omega_m}$)')

ax.set_xlabel('Idade do Universo (Gyr)', fontsize=12)
ax.set_ylabel('Redshift ($z$)', fontsize=12)
ax.set_title('Comparação: Evolução do Redshift vs Idade do Universo', fontsize=14)

ax.grid(color='#334155', linestyle='-', linewidth=0.5, alpha=0.5)
ax.legend(loc='upper right', facecolor='#1e293b', edgecolor='none')

st.pyplot(fig)

# Cards informativos lado a lado
col1, col2 = st.columns(2)
with col1:
    st.info(f" **Idade Atual (Modelo Ajustado, $z=0$):** {idade_vals_atual[0]:.2f} bilhões de anos.")
with col2:
    st.success(f" **Idade Atual (Referência Fixa, $z=0$):** {idade_vals_ref[0]:.2f} bilhões de anos.")