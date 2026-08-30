import streamlit as st
import numpy as np
from scipy.optimize import brentq
import matplotlib.pyplot as plt

# ==========================================
# CONFIGURAÇÃO INICIAL
# ==========================================
st.set_page_config(page_title="Foguete Relativístico", layout="wide")

st.title("Foguete Relativístico: Aceleração Própria vs. Coordenada")
st.markdown("""
Comparamos duas estratégias para uma viagem interestelar partindo e chegando em repouso:
1. **Estratégia 1 (Padrão):** Aceleração **própria** constante ($1g$). O foguete acelera metade do caminho e freia na outra metade.
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
# Fase de aceleração (v = g*t)
t_accel = v_alvo / a0
x_accel = 0.5 * a0 * t_accel**2

# Verifica se há espaço para atingir a velocidade de cruzeiro
if 2 * x_accel >= D:
    st.error("⚠️ A distância é muito curta para atingir essa velocidade com essa aceleração. Reduza a velocidade alvo ou aumente a distância.")
    st.stop()

x_cruise = D - (2 * x_accel)
t_cruise = x_cruise / v_alvo
t_total_2 = (2 * t_accel) + t_cruise

# Tempo próprio na aceleração coordenada: integral de sqrt(1 - (gt)^2) dt
tau_accel = (1 / (2 * a0)) * (np.arcsin(v_alvo) + v_alvo * np.sqrt(1 - v_alvo**2))
gamma_cruise = 1 / np.sqrt(1 - v_alvo**2)
tau_cruise = t_cruise / gamma_cruise
tau_total_2 = (2 * tau_accel) + tau_cruise

# Aceleração própria máxima sentida na Estratégia 2
a_propria_max = a0 * (gamma_cruise**3)
a_propria_max_g = a_propria_max / 1.0323 # Convertendo de volta para múltiplos de g

# ==========================================
# INTERFACE E RESULTADOS
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
    st.metric("Aceleração Máxima Sentida pela Tripulação", f"{a_propria_max_g:.1f} g", delta="Letal", delta_color="inverse")

st.markdown("---")
st.markdown("""
### A Lição: Por que a Estratégia 2 é impossível?
À primeira vista, a Estratégia 2 parece ser melhor: ela chega ao destino em menos tempo, tanto para os relógios da Terra quanto para os da nave! 
O absurdo se revela na **aceleração própria** ($a_{\text{própria}}$). Para que a aceleração coordenada ($a_{\text{coord}}$) permaneça constante à medida que a nave se aproxima da velocidade da luz, a força real exercida sobre a tripulação deve aumentar dramaticamente para compensar a inércia relativística. A relação no movimento retilíneo é:

$$ a_{\text{própria}} = \gamma^3 a_{\text{coord}} $$

Quando o foguete atinge $v = 0{,}9c$, o fator de Lorentz é $\gamma \approx 2{,}29$. Consequentemente, a tripulação seria esmagada contra os assentos com uma força equivalente a **$\approx 12g$**! Nenhuma tripulação humana sobrevive a uma aceleração dessas por meses seguidos. É por isso que, na literatura, a aceleração *própria* constante é o cenário realista.
""")

# ==========================================
# GRÁFICOS
# ==========================================
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# Gráfico 1: Velocidade vs Tempo Coordenado
t_grid_1 = np.linspace(0, t_meio_1, 200)
v_grid_1_ida = (a0 * t_grid_1) / np.sqrt(1 + (a0 * t_grid_1)**2)
t_plot_1 = np.concatenate([t_grid_1, t_grid_1 + t_meio_1])
v_plot_1 = np.concatenate([v_grid_1_ida, v_grid_1_ida[::-1]])
ax1.plot(t_plot_1, v_plot_1, label="Estratégia 1 (Própria Constante)", color="#4C72B0", lw=2)

t_grid_2_acc = np.linspace(0, t_accel, 100)
v_grid_2_acc = a0 * t_grid_2_acc
t_grid_2_cruise = np.linspace(t_accel, t_accel + t_cruise, 50)
v_grid_2_cruise = np.full_like(t_grid_2_cruise, v_alvo)
t_grid_2_dec = np.linspace(t_accel + t_cruise, t_total_2, 100)
v_grid_2_dec = v_alvo - a0 * (t_grid_2_dec - (t_accel + t_cruise))

t_plot_2 = np.concatenate([t_grid_2_acc, t_grid_2_cruise, t_grid_2_dec])
v_plot_2 = np.concatenate([v_grid_2_acc, v_grid_2_cruise, v_grid_2_dec])
ax1.plot(t_plot_2, v_plot_2, label="Estratégia 2 (Coord. Constante)", color="#B0413E", lw=2, ls="--")

ax1.set_xlabel("Tempo Coordenado $t$ (anos)")
ax1.set_ylabel("Velocidade $v(t)$")
ax1.set_title("Perfil de Velocidade")
ax1.legend()
ax1.grid(alpha=0.3)

# Gráfico 2: Aceleração Própria vs Tempo Coordenado
a_propria_1 = np.full_like(t_plot_1, 1.0) # Sempre 1g
ax2.plot(t_plot_1, a_propria_1, label="Estratégia 1", color="#4C72B0", lw=2)

a_propria_2_acc = 1.0 / (1 - v_grid_2_acc**2)**1.5
a_propria_2_cruise = np.zeros_like(t_grid_2_cruise)
a_propria_2_dec = 1.0 / (1 - v_grid_2_dec**2)**1.5
a_plot_2 = np.concatenate([a_propria_2_acc, a_propria_2_cruise, a_propria_2_dec])

ax2.plot(t_plot_2, a_plot_2, label="Estratégia 2", color="#B0413E", lw=2, ls="--")
ax2.axhline(12.08, color="red", alpha=0.3, ls=":", label="Limite Letal (~12g)")

ax2.set_xlabel("Tempo Coordenado $t$ (anos)")
ax2.set_ylabel("Aceleração Própria sentida ($g$)")
ax2.set_title("O Esmagamento da Tripulação")
ax2.set_yscale("log") # Escala logarítmica para ver o salto
ax2.legend()
ax2.grid(alpha=0.3)

st.pyplot(fig)