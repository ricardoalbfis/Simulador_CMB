import streamlit as st
import numpy as np
import camb
import plotly.graph_objects as go

# Configuração da página
st.set_page_config(page_title="Simulador CMB", layout="wide")
st.title("Espectro de Potência da CMB (Interativo)")

# Controles no menu lateral com slider de H0 estendido até 1000
with st.sidebar.form("controles_cosmologicos"):
    st.header("Parâmetros Cosmológicos")
    H0 = st.slider("H0 (Constante de Hubble):", 0.0, 1000.0, 67.4, 1.0)
    ombh2 = st.slider("Ωb h² (Densidade de Bárions):", 0.010, 0.040, 0.0224, 0.001)
    omch2 = st.slider("Ωc h² (Matéria Escura):", 0.050, 0.250, 0.120, 0.005)
    omk = st.slider("Ωk (Curvatura):", -0.05, 0.05, 0.0, 0.01)
    ns = st.slider("ns (Índice Espectral):", 0.85, 1.10, 0.965, 0.01)
    As_mult = st.slider("Amplitude (Multiplicador):", 0.5, 1.5, 1.0, 0.05)
    escala_log = st.checkbox("Escala Logarítmica no Eixo X", value=True)
    
    # O botão que impede o servidor de sobrecarregar
    calcular = st.form_submit_button("Calcular Gráfico")

# Função base com cache e lmax=1500 (mais leve para o servidor)
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

# Construção do gráfico interativo com Plotly (permite zoom, pan e hover com os valores exatos)
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=ls_base[2:1501], 
    y=cl_base[2:1501], 
    mode='lines', 
    name='ΛCDM (Referência)',
    line=dict(color='#94a3b8', width=2, dash='dash')
))

fig.add_trace(go.Scatter(
    x=ls_base[2:1501], 
    y=cl_custom[2:1501], 
    mode='lines', 
    name='Modelo Modificado',
    line=dict(color='#ef4444', width=2.5)
))

fig.update_layout(
    title="Espectro de Potência Angular do CMB",
    xaxis_title="Multipolo (ℓ)",
    yaxis_title="D_ℓ^TT [μK²]",
    xaxis=dict(type="log" if escala_log else "linear", range=[2, 1500]),
    yaxis=dict(range=[0, 7500]),
    template="plotly_dark",
    hovermode="x unified",
    legend=dict(x=0.75, y=0.95)
)

st.plotly_chart(fig, use_container_width=True)