import streamlit as st
import numpy as np
from scipy.integrate import solve_ivp
import plotly.graph_objects as go

st.set_page_config(page_title="Fases de H e Troca de Energia", layout="wide")

st.title("Dinâmica de Campos com $H$ Negativo, Zero e Positivo")
st.markdown(r"""
Simulação da evolução dos campos e da troca energética permitindo alternar o sinal do parâmetro de Hubble ($H$), simulando contração ($H < 0$), o ponto de inflexão (*bounce*, $H = 0$) e a expansão cósmica ($H > 0$)[cite: 1].
""")

# ==========================================
# CONTROLES INTERATIVOS NA BARRA LATERAL
# ==========================================
st.sidebar.header("Parâmetros do Sistema")
phi_0 = st.sidebar.slider("Inércia inicial $\\varphi(0)$", -2.0, 2.0, 1.0, 0.1)
psi_0 = st.sidebar.slider("Inércia inicial $\\phi(0)$", -2.0, 2.0, 0.5, 0.1)
b_val = st.sidebar.slider("Acoplamento cinético ($b$)", -0.4, 0.4, 0.1, 0.05)

# Slider permitindo valores negativos, zero e positivos para H
h_modo = st.sidebar.slider("Modulação direta ou Fator de $H$", -2.0, 2.0, 1.0, 0.1, 
                           help="Negativo = Contração, Zero = Bounce, Positivo = Expansão")
t_max = st.slider("Tempo de Evolução", 10.0, 60.0, 30.0, 5.0)

# ==========================================
# MODELO FÍSICO E EDOs
# ==========================================
V0 = 1.0
omega = 1.2
m_psi = 1.0

def system_ode(t, y):
    phi, dphi, psi, dpsi, a = y
    rho_M = 0.05 / (a**3) if a > 0.01 else 5.0
    
    V_phi = V0 * omega * np.sin(omega * phi)
    V_psi = (m_psi**2) * psi
    
    den = 1.0 - (b_val**2) / 4.0
    if abs(den) < 1e-3: den = 1e-3

    V_total = V0 * (1 - np.cos(omega * phi)) + 0.5 * (m_psi**2) * (psi**2)
    rho_fields = 0.5 * (dphi**2) + 0.5 * (dpsi**2) + b_val * dphi * dpsi + V_total
    
    # Parâmetro de Hubble modulado pelo slider (permitindo H negativo, 0 ou positivo)
    H_base = np.sqrt(max(1e-5, (rho_fields + rho_M) / 3.0))
    H = H_base * h_modo
    
    # EDOs acopladas com fricção de Hubble ajustável em sinal e magnitude
    term_phi = -3.0 * H * dphi - (V_phi - 0.5 * b_val * V_psi) / den
    term_psi = -3.0 * H * dpsi - (V_psi - 0.5 * b_val * V_phi) / den
    da_dt = H * a
    
    return [dphi, term_phi, dpsi, term_psi, da_dt]

y0 = [phi_0, 0.0, psi_0, 0.0, 1.0]
t_eval = np.linspace(0, t_max, 600)
sol = solve_ivp(system_ode, [0, t_max], y0, t_eval=t_eval, method='RK45')

t_arr = sol.t
phi_arr, dphi_arr, psi_arr, dpsi_arr, a_arr = sol.y

# ==========================================
# CÁLCULO DAS ENERGIAS DOS CAMPOS
# ==========================================
V_phi_arr = V0 * (1 - np.cos(omega * phi_arr))
E_phi = 0.5 * (dphi_arr**2) + V_phi_arr + 0.5 * b_val * dphi_arr * dpsi_arr

V_psi_arr = 0.5 * (m_psi**2) * (psi_arr**2)
E_psi = 0.5 * (dpsi_arr**2) + V_psi_arr + 0.5 * b_val * dphi_arr * dpsi_arr

E_total = np.abs(E_phi) + np.abs(E_psi) + 1e-9
frac_phi = np.abs(E_phi) / E_total
frac_psi = np.abs(E_psi) / E_total

# ==========================================
# RENDERIZAÇÃO DOS GRÁFICOS
# ==========================================
col1, col2 = st.columns(2)

with col1:
    st.subheader("Troca de Energia entre os Campos")
    fig_energy = go.Figure()
    fig_energy.add_trace(go.Scatter(x=t_arr, y=E_phi, mode='lines', name='Energia $\\varphi$', line=dict(color='#2563eb', width=2.5)))
    fig_energy.add_trace(go.Scatter(x=t_arr, y=E_psi, mode='lines', name='Energia $\\phi$', line=dict(color='#dc2626', width=2.5)))
    fig_energy.update_layout(xaxis_title="Tempo ($t$)", yaxis_title="Energia", template="plotly_white", hovermode="x unified")
    st.plotly_chart(fig_energy, use_container_width=True)

with col2:
    st.subheader("Dominância Relativa")
    fig_dom = go.Figure()
    fig_dom.add_trace(go.Scatter(x=t_arr, y=frac_phi, mode='lines', name='Dominância $\\varphi$', stackgroup='one', fillcolor='rgba(37, 99, 235, 0.6)'))
    fig_dom.add_trace(go.Scatter(x=t_arr, y=frac_psi, mode='lines', name='Dominância $\\phi$', stackgroup='one', fillcolor='rgba(220, 38, 38, 0.6)'))
    fig_dom.update_layout(xaxis_title="Tempo ($t$)", yaxis_title="Fração", yaxis=dict(range=[0, 1]), template="plotly_white", hovermode="x unified")
    st.plotly_chart(fig_dom, use_container_width=True)