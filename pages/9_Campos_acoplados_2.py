import streamlit as st
import numpy as np
from scipy.integrate import solve_ivp
import plotly.graph_objects as go

st.set_page_config(page_title="Troca de Energia e Dominância", layout="wide")

st.title("Troca de Energia e Dominância entre Campos Escalares")
st.markdown(r"""
Esta simulação ilustra a conversão dinâmica de energia entre o campo cíclico ($\varphi$) e o campo inflacionário ($\phi$), evidenciando como o amortecimento de Hubble ($3H$) dita qual componente domina o tecido cosmológico[cite: 1].
""")

# ==========================================
# CONTROLES INTERATIVOS NA BARRA LATERAL
# ==========================================
st.sidebar.header("Configurações do Sistema")
phi_0 = st.sidebar.slider("Inercia inicial $\\varphi(0)$", -2.0, 2.0, 1.2, 0.1)
psi_0 = st.sidebar.slider("Inercia inicial $\\phi(0)$", -2.0, 2.0, 0.2, 0.1)
b_val = st.sidebar.slider("Acoplamento cinético ($b$)", -0.4, 0.4, 0.15, 0.05)
fator_h = st.sidebar.slider("Fator de Fricção de Hubble ($3H$)", 0.2, 2.5, 1.0, 0.1)
t_max = st.slider("Tempo de Evolução", 10.0, 60.0, 25.0, 5.0)

# ==========================================
# MODELO FÍSICO E EDOs
# ==========================================
V0 = 1.0
omega = 1.2
m_psi = 1.0

def system_ode(t, y):
    phi, dphi, psi, dpsi, a = y
    rho_M = 0.05 / (a**3) if a > 0.01 else 5.0
    
    # Derivadas do potencial V_IC
    V_phi = V0 * omega * np.sin(omega * phi)
    V_psi = (m_psi**2) * psi
    
    den = 1.0 - (b_val**2) / 4.0
    if abs(den) < 1e-3: den = 1e-3

    # Densidade de energia total dos campos para o cálculo de H (Eq. 2 do artigo)
    V_total = V0 * (1 - np.cos(omega * phi)) + 0.5 * (m_psi**2) * (psi**2)
    rho_fields = 0.5 * (dphi**2) + 0.5 * (dpsi**2) + b_val * dphi * dpsi + V_total
    H = np.sqrt(max(1e-5, (rho_fields + rho_M) / 3.0))
    
    # EDOs com controle ajustável da fricção de Hubble
    term_phi = -3.0 * fator_h * H * dphi - (V_phi - 0.5 * b_val * V_psi) / den
    term_psi = -3.0 * fator_h * H * dpsi - (V_psi - 0.5 * b_val * V_phi) / den
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
# Energia do Campo Cíclico (Cinética + Potencial parcial + Acoplamento)
V_phi_arr = V0 * (1 - np.cos(omega * phi_arr))
E_phi = 0.5 * (dphi_arr**2) + V_phi_arr + 0.5 * b_val * dphi_arr * dpsi_arr

# Energia do Campo Inflacionário (Cinética + Potencial parcial + Acoplamento)
V_psi_arr = 0.5 * (m_psi**2) * (psi_arr**2)
E_psi = 0.5 * (dpsi_arr**2) + V_psi_arr + 0.5 * b_val * dphi_arr * dpsi_arr

E_total = np.abs(E_phi) + np.abs(E_psi) + 1e-9
frac_phi = np.abs(E_phi) / E_total
frac_psi = np.abs(E_psi) / E_total

# ==========================================
# RENDERIZAÇÃO DOS GRÁFICOS INTERATIVOS
# ==========================================
col1, col2 = st.columns(2)

with col1:
    st.subheader("Troca de Energia entre os Campos")
    fig_energy = go.Figure()
    fig_energy.add_trace(go.Scatter(x=t_arr, y=E_phi, mode='lines', name='Energia Campo Cíclico ($\\varphi$)', line=dict(color='#2563eb', width=2.5)))
    fig_energy.add_trace(go.Scatter(x=t_arr, y=E_psi, mode='lines', name='Energia Campo Inflacionário ($\\phi$)', line=dict(color='#dc2626', width=2.5)))
    fig_energy.update_layout(
        xaxis_title="Tempo Coordenado ($t$)",
        yaxis_title="Densidade de Energia",
        template="plotly_white",
        hovermode="x unified"
    )
    st.plotly_chart(fig_energy)

with col2:
    st.subheader("Dominância Relativa (Fração de Energia)")
    fig_dom = go.Figure()
    fig_dom.add_trace(go.Scatter(x=t_arr, y=frac_phi, mode='lines', name='Dominância $\\varphi$', stackgroup='one', line=dict(width=0.5), fillcolor='rgba(37, 99, 235, 0.6)'))
    fig_dom.add_trace(go.Scatter(x=t_arr, y=frac_psi, mode='lines', name='Dominância $\\phi$', stackgroup='one', line=dict(width=0.5), fillcolor='rgba(220, 38, 38, 0.6)'))
    fig_dom.update_layout(
        xaxis_title="Tempo Coordenado ($t$)",
        yaxis_title="Fração da Energia Total",
        yaxis=dict(range=[0, 1]),
        template="plotly_white",
        hovermode="x unified"
    )
    st.plotly_chart(fig_dom)

st.markdown("---")
st.markdown("""
**Análise Física do Comportamento:**
* **Transferência Energética:** O termo cruzado de acoplamento cinético ($b$) e as derivadas cruzadas do potencial $V_{IC}(\varphi, \phi)$ permitem que a energia oscile entre os modos, transferindo o ímpeto do movimento macroscópico cíclico para o gatilho inflacionário[cite: 1].
* **Papel da Fricção de Hubble ($3H$):** Aumentar o fator de atrito na barra lateral comprime o tempo de relaxação dos campos, estabilizando rapidamente o sistema e fazendo com que o componente inflacionário perca energia cinética mais depressa devido ao amortecimento da expansão cósmica[cite: 1].
""")