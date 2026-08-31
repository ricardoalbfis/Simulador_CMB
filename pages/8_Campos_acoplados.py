import streamlit as st
import numpy as np
from scipy.integrate import solve_ivp
import plotly.graph_objects as go

st.set_page_config(page_title="Dinâmica de Campos Escalares - Cosmologia Cíclica", layout="wide")

st.title("Evolução Dinâmica dos Campos Escalares ($-\\varphi$ e $\\phi$)")
st.markdown("""
Simulação baseada no acoplamento entre o campo cíclico ($\\varphi$) e o campo inflacionário ($\\phi$) conforme descrito por Kanabar et al. (2026).
""")

# ==========================================
# BARRA LATERAL DE CONTROLES
# ==========================================
st.sidebar.header("Parâmetros da Simulação")
phi_0 = st.sidebar.slider("Valor inicial $\\varphi(0)$", -2.0, 2.0, 1.0, 0.1)
psi_0 = st.sidebar.slider("Valor inicial $\\phi(0)$", -2.0, 2.0, 0.5, 0.1)
b_val = st.sidebar.slider("Acoplamento cinético $b$", -0.5, 0.5, 0.1, 0.05)
t_max = st.sidebar.slider("Tempo máximo de integração", 10.0, 100.0, 30.0, 5.0)

# ==========================================
# MODELO FÍSICO E EQUAÇÕES DIFERENCIAIS
# ==========================================
# Potencial toy model combinando comportamento cíclico e inflacionário:
# V_IC(phi, psi) = V_0 * (1 - cos(omega * phi)) + 0.5 * m^2 * psi^2
V0 = 1.0
omega = 1.5
m_psi = 1.0

def potential_derivatives(phi, psi):
    # Derivadas parciais do potencial V_IC em relação a phi e psi
    V_phi = V0 * omega * np.sin(omega * phi)
    V_psi = (m_psi**2) * psi
    return V_phi, V_psi

def system_ode(t, y):
    # y = [phi, dphi_dt, psi, dpsi_dt, a]
    phi, dphi, psi, dpsi, a = y
    
    # Taxa de expansão H = da/dt / a (aproximação com densidade de radiação/matéria decrescente)
    rho_M = 0.1 / (a**3) if a > 0.01 else 10.0
    V_phi, V_psi = potential_derivatives(phi, psi)
    
    # Termo de acoplamento cinético (1 - b^2/4)
    den = 1.0 - (b_val**2) / 4.0
    if abs(den) < 1e-3:
        den = 1e-3

    # Energia total aproximada para o cálculo de H via Friedmann (Eq. 2)
    V_total = V0 * (1 - np.cos(omega * phi)) + 0.5 * (m_psi**2) * (psi**2)
    rho_fields = 0.5 * (dphi**2) + 0.5 * (dpsi**2) + b_val * dphi * dpsi + V_total
    H = np.sqrt(max(1e-5, (rho_fields + rho_M) / 3.0))
    
    # Equações de movimento acopladas (Eq. 4 do artigo)
    # (1 - b^2/4) \ddot{\varphi} + 3H(1 - b^2/4)\dot{\varphi} + V_{,\varphi} - (b/2)V_{,\psi} = ...
    term_phi = -3.0 * H * dphi - (V_phi - 0.5 * b_val * V_psi) / den
    term_psi = -3.0 * H * dpsi - (V_psi - 0.5 * b_val * V_phi) / den
    
    da_dt = H * a
    
    return [dphi, term_phi, dpsi, term_psi, da_dt]

# Condições iniciais: [phi, dphi, psi, dpsi, a]
y0 = [phi_0, 0.0, psi_0, 0.0, 1.0]
t_eval = np.linspace(0, t_max, 500)

sol = solve_ivp(system_ode, [0, t_max], y0, t_eval=t_eval, method='RK45')

# ==========================================
# VISUALIZAÇÃO GRÁFICA
# ==========================================
col1, col2 = st.columns(2)

with col1:
    st.subheader("Evolução Temporal dos Campos")
    fig_time = go.Figure()
    fig_time.add_trace(go.Scatter(x=sol.t, y=sol.y[0], mode='lines', name='Campo Cíclico $\\varphi(t)$', line=dict(color='blue', width=2)))
    fig_time.add_trace(go.Scatter(x=sol.t, y=sol.y[2], mode='lines', name='Campo Inflacionário $\\phi(t)$', line=dict(color='orange', width=2)))
    fig_time.update_layout(xaxis_title="Tempo ($t$)", yaxis_title="Amplitudes", template="plotly_white")
    st.plotly_chart(fig_time, use_container_width=True)

with col2:
    st.subheader("Trajetória no Espaço de Fases")
    fig_phase = go.Figure()
    fig_phase.add_trace(go.Scatter(x=sol.y[0], y=sol.y[2], mode='lines+markers', name='Trajetória $(\\varphi, \\phi)$',
                                   line=dict(color='purple', width=2), marker=dict(size=4, color=sol.t, colorscale='Virvid', showscale=True)))
    fig_phase.update_layout(xaxis_title="Campo Cíclico $\\varphi$", yaxis_title="Campo Inflacionário $\\phi$", template="plotly_white")
    st.plotly_chart(fig_phase, use_container_width=True)

st.markdown("---")
st.markdown("### Formulação Matemática Aplicada")
st.latex(r"\left(1-\frac{b^2}{4}\right)\ddot{\varphi} + 3H\left(1-\frac{b^2}{4}\right)\dot{\varphi} + V_{IC,\varphi} - \frac{b}{2}V_{IC,\phi} = \frac{1}{2}b\beta^3(\phi)\beta_{,\phi}\rho_M")
st.latex(r"\left(1-\frac{b^2}{4}\right)\ddot{\phi} + 3H\left(1-\frac{b^2}{4}\right)\dot{\phi} + V_{IC,\phi} - \frac{b}{2}V_{IC,\varphi} = -\beta^3(\phi)\beta_{,\phi}\rho_M")