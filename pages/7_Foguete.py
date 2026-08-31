import streamlit as st
import numpy as np
from scipy.optimize import brentq
import plotly.graph_objects as go

# ==========================================
# CONFIGURAÇÃO INICIAL
# ==========================================
st.set_page_config(page_title="Foguete Relativístico", layout="wide")

st.title("Foguete Relativístico: Aceleração Própria vs. Coordenada")
st.markdown(r"""
Comparamos duas estratégias para uma viagem interestelar partindo e chegando em repouso:
1. **Estratégia 1 (Padrão de Ficção Científica Realista):** Aceleração **própria** constante ($1g$). O foguete acelera metade do caminho e freia na outra metade.
2. **Estratégia 2 (A armadilha):** Aceleração **coordenada** constante ($1g$ visto da Terra) até atingir uma velocidade de cruzeiro $v_{alvo}$, mantendo-a, e depois freando com $-1g$.
""")

# ==========================================
# BARRA LATERAL (CONTROLES)
# ==========================================
st.sidebar.header("Parâmetros da Viagem")
D = st.sidebar.number_input("Distância do Destino (anos-luz)", min_value=1.0, value=4.2465, step=0.1, help="Proxima Centauri = 4.2465")
v_alvo = st.sidebar.slider("Velocidade de Cruzeiro Estratégia 2 (v/c)", min_value=0.1, max_value=0.99, value=0.90, step=0.01)

# Aceleração de 1g em anos-luz/ano^2 (c=1 ano-luz/ano)
a0 = 1.0323

# ==========================================
# CÁLCULOS: ESTRATÉGIA 1 (ACELERAÇÃO PRÓPRIA CONSTANTE)
# ==========================================
def meio_percurso(tau):
    return (1 / a0) * (np.cosh(a0 * tau) - 1) - (D / 2)

tau_meio_1 = brentq(meio_percurso, 1e-3, 50)
tau_total_1 = 2 * tau_meio_1
t_meio_1 = (1 / a0) * np.sinh(a0 * tau_meio_1)
t_total_1 = 2 * t_meio_1
v_max_1 = np.tanh(a0 * tau_meio_1)

# ==========================================
# CÁLCULOS: ESTRATÉGIA 2 (ACELERAÇÃO COORDENADA CONSTANTE)
# ==========================================
t_accel = v_alvo / a0
x_accel = 0.5 * a0 * t_accel**2

if 2 * x_accel >= D:
    st.error("⚠️ A distância é muito curta para atingir essa velocidade com essa aceleração. Reduza a velocidade alvo ou aumente a distância.")
    st.stop()

x_cruise = D - (2 * x_accel)
t_cruise = x_cruise / v_alvo
t_total_2 = (2 * t_accel) + t_cruise

tau_accel = (1 / (2 * a0)) * (np.arcsin(v_alvo) + v_alvo * np.sqrt(1 - v_alvo**2))
gamma_cruise = 1 / np.sqrt(1 - v_alvo**2)
tau_cruise = t_cruise / gamma_cruise
tau_total_2 = (2 * tau_accel) + tau_cruise

a_propria_max = a0 * (gamma_cruise**3)
a_propria_max_g = a_propria_max / 1.0323

# ==========================================
# INTERFACE E RESULTADOS (MÉTRICAS)
# ==========================================
col1, col2 = st.columns(2)

with col1:
    st.subheader("Estratégia 1: Aceleração Própria")
    st.write("A tripulação sente exatamente $1g$ o tempo todo.")
    st.metric("Tempo Coordenado (Terra)", f"{t_total_1:.2f} anos")
    st.metric("Tempo Próprio (Nave)", f"{tau_total_1:.2f} anos")
    st.metric("Velocidade Máxima Atingida", f"{v_max_1:.3f} c")

with col2:
    st.subheader("Estratégia 2: Aceleração Coordenada")
    st.write(f"Visto da Terra, a aceleração é $1g$ até $v={v_alvo}c$.")
    st.metric("Tempo Coordenado (Terra)", f"{t_total_2:.2f} anos", delta=f"{t_total_2 - t_total_1:.2f} anos", delta_color="inverse")
    st.metric("Tempo Próprio (Nave)", f"{tau_total_2:.2f} anos", delta=f"{tau_total_2 - tau_total_1:.2f} anos", delta_color="inverse")
    st.metric("Aceleração Máxima (Nave)", f"{a_propria_max_g:.1f} g", delta="Letal se > 3g", delta_color="inverse")

# ==========================================
# GERAÇÃO DOS DADOS PARA OS GRÁFICOS
# ==========================================
t_grid_1 = np.linspace(0, t_meio_1, 200)
v_grid_1_ida = (a0 * t_grid_1) / np.sqrt(1 + (a0 * t_grid_1)**2)
t_plot_1 = np.concatenate([t_grid_1, t_grid_1 + t_meio_1])
v_plot_1 = np.concatenate([v_grid_1_ida, v_grid_1_ida[::-1]])
a_propria_1 = np.full_like(t_plot_1, 1.0)

t_grid_2_acc = np.linspace(0, t_accel, 100)
v_grid_2_acc = a0 * t_grid_2_acc
t_grid_2_cruise = np.linspace(t_accel, t_accel + t_cruise, 50)
v_grid_2_cruise = np.full_like(t_grid_2_cruise, v_alvo)
t_grid_2_dec = np.linspace(t_accel + t_cruise, t_total_2, 100)
v_grid_2_dec = v_alvo - a0 * (t_grid_2_dec - (t_accel + t_cruise))

t_plot_2 = np.concatenate([t_grid_2_acc, t_grid_2_cruise, t_grid_2_dec])
v_plot_2 = np.concatenate([v_grid_2_acc, v_grid_2_cruise, v_grid_2_dec])

a_propria_2_acc = 1.0 / (1 - v_grid_2_acc**2)**1.5
a_propria_2_cruise = np.zeros_like(t_grid_2_cruise)
a_propria_2_dec = 1.0 / (1 - v_grid_2_dec**2)**1.5
a_plot_2 = np.concatenate([a_propria_2_acc, a_propria_2_cruise, a_propria_2_dec])

# ==========================================
# GRÁFICOS INTERATIVOS COM PLOTLY
# ==========================================
st.markdown("---")
st.subheader("Análise Interativa do Voo")
st.write("Passe o mouse sobre as curvas para inspecionar os valores exatos de velocidade e força G em cada instante da viagem.")

tab1, tab2 = st.tabs(["Perfil de Velocidade", "O Esmagamento (Aceleração Própria)"])

with tab1:
    fig_v = go.Figure()
    fig_v.add_trace(go.Scatter(x=t_plot_1, y=v_plot_1, mode='lines', name='Estratégia 1 (1g Próprio)', line=dict(color='#4C72B0', width=3)))
    fig_v.add_trace(go.Scatter(x=t_plot_2, y=v_plot_2, mode='lines', name='Estratégia 2 (1g Coord.)', line=dict(color='#B0413E', width=3, dash='dash')))
    
    fig_v.update_layout(
        title="Evolução da Velocidade ao longo do Tempo Coordenado",
        xaxis_title="Tempo Coordenado (anos)",
        yaxis_title="Velocidade (v/c)",
        hovermode="x unified",
        template="plotly_white",
        legend=dict(yanchor="bottom", y=0.01, xanchor="right", x=0.99)
    )
    st.plotly_chart(fig_v, use_container_width=True)

with tab2:
    fig_a = go.Figure()
    fig_a.add_trace(go.Scatter(x=t_plot_1, y=a_propria_1, mode='lines', name='Estratégia 1 (Confortável)', line=dict(color='#4C72B0', width=3)))
    fig_a.add_trace(go.Scatter(x=t_plot_2, y=a_plot_2, mode='lines', name='Estratégia 2 (Letal)', line=dict(color='#B0413E', width=3, dash='dash')))
    
    # Linha de limite humano aproximado (ex: pilotos de caça suportam 9g por breves segundos, não meses)
    fig_a.add_hline(y=4.0, line_dash="dot", annotation_text="Limite sustentável humano", annotation_position="top left", line_color="red")
    
    fig_a.update_layout(
        title="Força G Sentida pela Tripulação (Escala Logarítmica)",
        xaxis_title="Tempo Coordenado (anos)",
        yaxis_title="Aceleração Própria (em g)",
        yaxis_type="log", # Fundamental para ver o salto gigante
        hovermode="x unified",
        template="plotly_white",
        legend=dict(yanchor="top", y=0.99, xanchor="right", x=0.99)
    )
    st.plotly_chart(fig_a, use_container_width=True)

# ==========================================
# CONCLUSÃO ANALÍTICA
# ==========================================
st.markdown(r"""
---
### A Matemática por trás da Armadilha
A relação relativística entre a aceleração vista da Terra ($a_{\text{coord}}$) e a sentida na nave ($a_{\text{própria}}$) no movimento retilíneo é dada por:

$$ a_{\text{própria}} = \gamma^3 a_{\text{coord}} $$

O fator de Lorentz, $\gamma = \frac{1}{\sqrt{1 - v^2}}$, cresce de forma assintótica. Quando forçamos a nave a manter um ganho de velocidade constante do ponto de vista de quem está de fora, estamos obrigando os motores a gerar uma força exponencialmente maior para vencer a inércia relativística crescente. O resultado é que os viajantes são prensados contra o chão da nave com uma força dezenas de vezes maior que a gravidade terrestre.
""")