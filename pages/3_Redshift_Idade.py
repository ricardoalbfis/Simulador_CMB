import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import camb

# Configuração da página
st.set_page_config(page_title="Redshift vs Idade do Universo", layout="wide")
st.title("Evolução Temporal: Redshift x Idade do Universo ⏳")

st.markdown("""
Esta ferramenta utiliza o motor do **CAMB** para calcular como a idade do universo (em bilhões de anos - Gyr) evolui à medida que avançamos no redshift ($z$).
""")

# Painel de controle no menu lateral
with st.sidebar.form("form_idade_cosmologica"):
    st.header("Parâmetros Cosmológicos")
    H0 = st.slider("H0 (Constante de Hubble):", 50.0, 85.0, 67.4, 0.5)
    omch2 = st.slider("Ωc h² (Matéria Escura):", 0.050, 0.250, 0.120, 0.005)
    ombh2 = st.slider("Ωb h² (Bárions):", 0.010, 0.040, 0.0224, 0.001)
    
    calcular_botao = st.form_submit_button("Gerar Gráfico de Evolução")

# Função para calcular a história de expansão com cache
@st.cache_data
def calcular_historia(H0_val, omch2_val, ombh2_val):
    pars = camb.CAMBparams()
    pars.set_cosmology(H0=H0_val, ombh2=ombh2_val, omch2=omch2_val, omk=0.0, tau=0.0544)
    pars.InitPower.set_params(As=2.1e-9, ns=0.965)
    
    # Obtém a história de antecedentes (background)
    results = camb.get_background(pars)
    
    # Gera um vetor de redshifts de 0 até 20
    z_array = np.linspace(0, 20, 500)
    
    # Extrai a idade em cada redshift (retorna em anos, convertemos para Bilhões de Anos - Gyr)
    idades_gyr = np.array([results.age_at_z(z) for z in z_array])
    
    return z_array, idades_gyr

# Executa o cálculo com os valores escolhidos
z_vals, idade_vals = calcular_historia(H0, omch2, ombh2)

# Plota o gráfico
fig, ax = plt.subplots(figsize=(10, 5))
plt.style.use('dark_background')

ax.plot(z_vals, idade_vals, color='#38bdf8', linewidth=2.5, label='Modelo Atual')

ax.set_xlabel('Redshift ($z$)', fontsize=12)
ax.set_ylabel('Idade do Universo (Gyr)', fontsize=12)
ax.set_title('Relação Idade do Universo x Redshift', fontsize=14)

ax.grid(color='#334155', linestyle='-', linewidth=0.5, alpha=0.5)
ax.legend(loc='upper right')

st.pyplot(fig)

# Informação complementar na tela
st.info(f"💡 **Idade atual estimada do Universo ($z=0$):** {idade_vals[0]:.2f} bilhões de anos.")