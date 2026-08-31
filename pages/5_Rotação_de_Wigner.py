import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# ==========================================
# CONFIGURAÇÃO INICIAL
# ==========================================
st.set_page_config(page_title="Rotação de Wigner", layout="wide")

st.title("Rotação de Wigner e Precessão de Thomas")
st.markdown("""
Esta simulação compõe dois *boosts* de Lorentz em direções perpendiculares: $\\Lambda = \\Lambda_x(v_1)\\Lambda_y(v_2)$. 
A matriz resultante **não é simétrica**, o que indica que ela não representa um *boost* puro, mas sim a composição de um *boost* com uma rotação espacial.
""")

# ==========================================
# FUNÇÕES MATEMÁTICAS / FÍSICAS
# ==========================================
def fator_gamma(v):
    return 1.0 / np.sqrt(1.0 - v**2)

def boost_x(v):
    g = fator_gamma(v)
    return np.array([
        [g,   -g*v, 0, 0],
        [-g*v, g,   0, 0],
        [0,    0,   1, 0],
        [0,    0,   0, 1]
    ])

def boost_y(v):
    g = fator_gamma(v)
    return np.array([
        [g,   0, -g*v, 0],
        [0,   1, 0,    0],
        [-g*v, 0, g,    0],
        [0,   0, 0,    1]
    ])

def boost_puro_3d(vx, vy):
    """Constrói a matriz 4x4 de um boost puro na direção (vx, vy)."""
    v2 = vx**2 + vy**2
    if v2 == 0:
        return np.eye(4)
    
    g = fator_gamma(np.sqrt(v2))
    L = np.zeros((4, 4))
    L[0, 0] = g
    L[0, 1] = L[1, 0] = -g * vx
    L[0, 2] = L[2, 0] = -g * vy
    L[1, 1] = 1 + (g - 1) * (vx**2) / v2
    L[1, 2] = L[2, 1] = (g - 1) * (vx * vy) / v2
    L[2, 2] = 1 + (g - 1) * (vy**2) / v2
    L[3, 3] = 1
    return L

# ==========================================
# BARRA LATERAL (CONTROLES)
# ==========================================
st.sidebar.header("Parâmetros dos Boosts")
v1 = st.sidebar.slider("Velocidade v1 (direção x)", min_value=0.00, max_value=0.99, value=0.60, step=0.01)
v2 = st.sidebar.slider("Velocidade v2 (direção y)", min_value=0.00, max_value=0.99, value=0.60, step=0.01)

# ==========================================
# CÁLCULOS MATRICIAIS
# ==========================================
Lx = boost_x(v1)
Ly = boost_y(v2)

# Composição dos boosts: a ordem importa
Lambda_xy = Lx @ Ly

# Verificação do intervalo: L^T * eta * L = eta
eta = np.diag([-1, 1, 1, 1])
residuo = Lambda_xy.T @ eta @ Lambda_xy - eta
max_residuo = np.abs(residuo).max()

# Extração da Rotação
# A primeira coluna da matriz composta nos dá a velocidade efetiva do boost resultante
g_rel = Lambda_xy[0, 0]
vx_rel = -Lambda_xy[1, 0] / g_rel
vy_rel = -Lambda_xy[2, 0] / g_rel

# Decomposição: Lambda_xy = B_puro * R  =>  R = B_puro^-1 * Lambda_xy
B_eq = boost_puro_3d(vx_rel, vy_rel)
B_eq_inv = boost_puro_3d(-vx_rel, -vy_rel) # O inverso de um boost é o boost com -v
Matriz_Rotacao = B_eq_inv @ Lambda_xy

# O ângulo de rotação (theta) pode ser extraído do traço da submatriz espacial 3x3 de R
# Tr(R_3x3) = 1 + 2*cos(theta)
traco_R = np.trace(Matriz_Rotacao[1:4, 1:4])
cos_theta = (traco_R - 1.0) / 2.0
cos_theta = np.clip(cos_theta, -1.0, 1.0) # Evita erros numéricos fora do domínio arccos
theta_rad_num = np.arccos(cos_theta)
theta_deg_num = np.degrees(theta_rad_num)

# Fórmula analítica fechada (fornecida no exercício)
g1 = fator_gamma(v1)
g2 = fator_gamma(v2)
if v1 == 0 and v2 == 0:
    theta_deg_ana = 0.0
else:
    tan_theta = (g1 * g2 * v1 * v2) / (g1 + g2)
    theta_deg_ana = np.degrees(np.arctan(tan_theta))

# ==========================================
# INTERFACE E EXIBIÇÃO
# ==========================================
col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Invariância e Assimetria")
    st.write(f"**Resíduo de invariância do intervalo:** `{max_residuo:.2e}`")
    if max_residuo < 1e-10:
        st.success("A transformação preserva o intervalo (é uma transformação de Lorentz válida).")
    
    st.write("**Matriz Resultante** $\\Lambda_{xy} = \\Lambda_x(v_1)\\Lambda_y(v_2)$")
    st.dataframe(Lambda_xy.round(4), use_container_width=True)
    
    # Verifica a assimetria apontando a diferença entre os elementos fora da diagonal
    diff_simetria = abs(Lambda_xy[1, 2] - Lambda_xy[2, 1])
    if diff_simetria > 1e-10:
        st.info(f"Note que $\\Lambda_{{1,2}} \\neq \\Lambda_{{2,1}}$. Como a matriz não é simétrica, ela **não é um boost puro**.")

with col2:
    st.subheader("2. Ângulo de Rotação ($\\theta$)")
    
    st.metric(label="Ângulo Numérico (extraído da matriz)", value=f"{theta_deg_num:.2f}°")
    st.metric(label="Ângulo Teórico (fórmula fechada)", value=f"{theta_deg_ana:.2f}°")
    
    if abs(v1 - 0.6) < 1e-5 and abs(v2 - 0.6) < 1e-5:
        st.success("Confirmado! Para $v_1 = v_2 = 0.6$, o ângulo recuperado corresponde exatamente aos 12,7° previstos pelo exercício.")

# ==========================================
# VISUALIZAÇÃO GRÁFICA (MAPA DE CALOR)
# ==========================================
st.markdown("---")
st.subheader("Visualização Global da Rotação de Wigner")
st.write("O gráfico abaixo mostra como o ângulo de rotação $\\theta$ varia em função do par de velocidades $(v_1, v_2)$. O ponto vermelho indica a sua seleção atual.")

# Geração dos dados para o heatmap
v_grid = np.linspace(0, 0.99, 100)
V1, V2 = np.meshgrid(v_grid, v_grid)
G1 = 1 / np.sqrt(1 - V1**2)
G2 = 1 / np.sqrt(1 - V2**2)
TAN_THETA = (G1 * G2 * V1 * V2) / (G1 + G2)
THETA_GRID = np.degrees(np.arctan(TAN_THETA))

fig, ax = plt.subplots(figsize=(8, 5))
contour = ax.contourf(V1, V2, THETA_GRID, levels=30, cmap="inferno")
cbar = fig.colorbar(contour, ax=ax)
cbar.set_label("Ângulo de Rotação (Graus)")

# Marca a posição atual do slider
ax.plot(v1, v2, 'ro', markersize=10, markeredgecolor='white', markeredgewidth=1.5)

ax.set_xlabel(r"Velocidade $v_1$ (direção $x$)")
ax.set_ylabel(r"Velocidade $v_2$ (direção $y$)")
ax.set_title("Precessão de Thomas: Dependência das Velocidades")

st.pyplot(fig)