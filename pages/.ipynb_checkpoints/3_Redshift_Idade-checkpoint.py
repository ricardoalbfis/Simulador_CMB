import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import quad

# Configuração da página
st.set_page_config(page_title="Redshift vs Idade do Universo", layout="wide")
st.title("Evolução Temporal: Redshift x Idade do Universo ⏳")

st.markdown("""
Esta ferramenta calcula a relação entre a idade do universo (em bilhões de anos - Gyr) e o redshift ($z$) utilizando as equações padrão da Cosmologia de Friedmann-Lemaître-Robertson-Walker (FLRW).
""")

# Painel de controle no menu lateral
with st.sidebar.form("form_idade_cosmologica"):
    st.header("Parâmetros Cosmológicos")
    H0 = st.slider("H0 (Constante de Hubble [km/s/Mpc]):", 50.0, 85.0, 67.4, 0.5)
    Omega_m = st.slider("Ωm (Densidade Total de Matéria):", 0.15, 0.45, 0.315, 0.005)
    
    calcular_botao = st.form_submit_button("Gerar Gráfico de Evolução")

# Constantes físicas
H0_s = H0 * 1000.0 / (3.085677581e22) # H0 em s^-1
sec_por_ano = 365.25 * 24 * 3600
anos_por_gyr = 1e9

# Função do inverso da taxa de expansão E(z)
def inv_E_z(z, Om):
    Ode = 1.0 - Om # Energia Escura assumida plana (Lambda)
    return 1.0 / ((1.0 + z) * np.sqrt(Om * (1.0 + z)**3 + Ode))

@st.cache_data
def calcular_idade_redshift(H0_val, Om_val):
    H0_s_local = H0_val * 1000.0 / (3.085677581e22)
    z_array = np.linspace(0, 20, 500)
    idades = []
    
    for z in z_array:
        # Integração numérica do tempo cosmic a partir do redshift z até infinito
        integral, _ = quad(inv_E_z, z, np.inf, args=(Om_val,))
        tempo_segundos = integral / H0_s_local
        tempo_gyr = tempo_segundos / (sec_por_ano * anos_por_gyr)
        idades.append(tempo_gyr)
        
    return z_array, np.array(idades)

# Executa o cálculo
z_vals, idade_vals = calcular_idade_redshift(H0, Omega_m)

# Plota o gráfico
fig, ax = plt.subplots(figsize=(10, 5))
plt.style.use('dark_background')

ax.plot(z_vals, idade_vals, color='#38bdf8', linewidth=2.5, label='Modelo FLRW ($\Lambda$CDM)')

ax.set_xlabel('Redshift ($z$)', fontsize=12)
ax.set_ylabel('Idade do Universo (Gyr)', fontsize=12)
ax.set_title('Relação Idade do Universo x Redshift', fontsize=14)

ax.grid(color='#334155', linestyle='-', linewidth=0.5, alpha=0.5)
ax.legend(loc='upper right')

st.pyplot(fig)

# Informação complementar na tela
st.info(f"💡 **Idade atual estimada do Universo ($z=0$):** {idade_vals[0]:.2f} bilhões de anos.")