import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import camb

# Configuração da página do site
st.set_page_config(page_title="Simulador CMB", layout="wide")
st.title("Espectro de Potência da Radiação Cósmica de Fundo (CMB)")

# Cria os controles na barra lateral
st.sidebar.header("Parâmetros Cosmológicos")
H0 = st.sidebar.slider("H0 (Constante de Hubble):", 50.0, 85.0, 67.4, 0.5)
ombh2 = st.sidebar.slider("Ωb h² (Densidade de Bárions):", 0.010, 0.040, 0.0224, 0.001)
omch2 = st.sidebar.slider("Ωc h² (Matéria Escura):", 0.050, 0.250, 0.120, 0.005)
omk = st.sidebar.slider("Ωk (Curvatura):", -0.05, 0.05, 0.0, 0.01)
ns = st.sidebar.slider("ns (Índice Espectral):", 0.85, 1.10, 0.965, 0.01)
As_mult = st.sidebar.slider("Amplitude (Multiplicador):", 0.5, 1.5, 1.0, 0.05)
escala_log = st.sidebar.checkbox("Escala Logarítmica", value=True)

# Função com 'cache' para não calcular o modelo base toda hora
@st.cache_data
def modelo_base():
    pars_base = camb.CAMBparams()
    pars_base.set_cosmology(H0=67.4, ombh2=0.0224, omch2=0.120, omk=0.0)
    pars_base.InitPower.set_params(As=2.1e-9, ns=0.965)
    pars_base.set_for_lmax(2500, lens_potential_accuracy=0)
    resultados = camb.get_results(pars_base)
    cl = resultados.get_cmb_power_spectra(pars_base, CMB_unit='muK')['total'][:, 0]
    ls = np.arange(cl.shape[0])
    return ls, cl

ls_base, cl_base = modelo_base()

# Calcula o modelo com as escolhas do usuário
pars = camb.CAMBparams()
pars.set_cosmology(H0=H0, ombh2=ombh2, omch2=omch2, omk=omk)
pars.InitPower.set_params(As=2.1e-9 * As_mult, ns=ns)
pars.set_for_lmax(2500, lens_potential_accuracy=0)
resultados = camb.get_results(pars)
cl_custom = resultados.get_cmb_power_spectra(pars, CMB_unit='muK')['total'][:, 0]

# Desenha o gráfico
fig, ax = plt.subplots(figsize=(10, 5))
plt.style.use('dark_background')

ax.plot(ls_base[2:2501], cl_base[2:2501], color='#94a3b8', linestyle='--', linewidth=2, label='ΛCDM (Planck 2018)')
ax.plot(ls_base[2:2501], cl_custom[2:2501], color='#ef4444', linewidth=2.5, label='Modelo Modificado')

ax.set_xlabel(r'Multipolo $\ell$', fontsize=12)
ax.set_ylabel(r'$\ell(\ell+1)C_\ell / 2\pi \quad [\mu K^2]$', fontsize=12)

if escala_log:
    ax.set_xscale('log')

ax.set_xlim(2, 2500)
ax.set_ylim(0, 7500)
ax.grid(color='#334155', linestyle='-', linewidth=0.5, alpha=0.5)
ax.legend(loc='upper right')

# Envia o gráfico pronto para o site
st.pyplot(fig)