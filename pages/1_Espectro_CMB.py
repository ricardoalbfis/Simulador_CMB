import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import camb
import pandas as pd

# Configuração da página
st.set_page_config(page_title="Simulador CMB", layout="wide")
st.title("Espectro de Potência da CMB")

# Controles no menu lateral com slider de H0 estendido até 1000
with st.sidebar.form("controles_cosmologicos"):
    st.header("Parâmetros Cosmológicos")
    H0 = st.slider("H0 (Constante de Hubble):", 0.0, 1000.0, 67.4, 1.0)
    ombh2 = st.slider("Ωb h² (Densidade de Bárions):", 0.010, 0.040, 0.0224, 0.001)
    omch2 = st.slider("Ωc h² (Matéria Escura):", 0.050, 0.250, 0.120, 0.005)
    omk = st.slider("Ωk (Curvatura):", -0.05, 0.05, 0.0, 0.01)
    ns = st.slider("ns (Índice Espectral):", 0.85, 1.10, 0.965, 0.01)
    As_mult = st.slider("Amplitude (Multiplicador):", 0.5, 1.5, 1.0, 0.05)
    escala_log = st.checkbox("Escala Logarítmica", value=True)
    
    calcular = st.form_submit_button("Calcular Gráfico")

# Função base com cache e lmax=1500
@st.cache_data
def modelo_base():
    pars_base = camb.CAMBparams()
    pars_base.set_cosmology(H0=67.4, ombh2=0.0224, omch2=0.120, omk=0.0, tau=0.0544)
    pars_base.InitPower.set_params(As=2.1e-9, ns=0.965)
    pars_base.set_for_lmax(1500, lens_potential_accuracy=0)
    resultados = camb.get_results(pars_base)
    cl = resultados.get_cmb_power_spectra(pars_base, CMB_unit='muK')['total'][:, 0]
    ls = np.arange(cl.shape[0])
    return ls, cl

ls_base, cl_base = modelo_base()

# Calcula o modelo interativo
pars = camb.CAMBparams()
pars.set_cosmology(H0=H0, ombh2=ombh2, omch2=omch2, omk=omk, tau=0.0544)
pars.InitPower.set_params(As=2.1e-9 * As_mult, ns=ns)
pars.set_for_lmax(1500, lens_potential_accuracy=0)
resultados = camb.get_results(pars)
cl_custom = resultados.get_cmb_power_spectra(pars, CMB_unit='muK')['total'][:, 0]

# Desenha o gráfico com Matplotlib
fig, ax = plt.subplots(figsize=(10, 5))
plt.style.use('dark_background')

ax.plot(ls_base[2:1501], cl_base[2:1501], color='#94a3b8', linestyle='--', linewidth=2, label='ΛCDM')
ax.plot(ls_base[2:1501], cl_custom[2:1501], color='#ef4444', linewidth=2.5, label='Modelo Modificado')

ax.set_xlabel(r'Multipolo $\ell$', fontsize=12)
ax.set_ylabel(r'$\ell(\ell+1)C_\ell / 2\pi \quad [\mu K^2]$', fontsize=12)

if escala_log:
    ax.set_xscale('log')

ax.set_xlim(2, 1500)
ax.set_ylim(0, 7500)
ax.grid(color='#334155', linestyle='-', linewidth=0.5, alpha=0.5)
ax.legend(loc='upper right')

st.pyplot(fig)

# Tabela com valores para multipolos e escalas angulares de referência
st.subheader("Valores para Multipolos e Escalas Angulares de Referência")
multipolos_exemplo = [2, 10, 50, 100, 220, 500, 1000]
dados_tabela = []

for l in multipolos_exemplo:
    if l < len(ls_base):
        theta = 180.0 / l
        val_base = cl_base[l]
        val_custom = cl_custom[l]
        dados_tabela.append({
            "Multipolo (ℓ)": l,
            "Escala Angular (°)": round(theta, 3),
            "ΛCDM (μK²)": round(val_base, 2),
            "Modelo Modificado (μK²)": round(val_custom, 2)
        })

df_tabela = pd.DataFrame(dados_tabela)
st.table(df_tabela)