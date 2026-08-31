import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe

# ==========================================
# CONFIGURAÇÃO INICIAL E ESTILOS
# ==========================================
st.set_page_config(page_title="Horizonte de Rindler", layout="wide")

# Estilo visual baseado na apostila
plt.rcParams.update({
    "font.family": "serif",
    "mathtext.fontset": "cm",
    "font.size": 12,
    "axes.linewidth": 0.9,
})
HALO = [pe.withStroke(linewidth=3.0, foreground="white")]

st.title("O Horizonte de Rindler")
st.markdown("""
Esta simulação ilustra um observador com **aceleração própria constante** $a_0$. 
Sua linha de mundo descreve uma hipérbole no espaço-tempo: $x^2 - t^2 = 1/a_0^2$.
Um fóton é disparado no instante $t=0$ a partir de uma posição $x_0$ rumo ao observador. Será que a luz sempre o alcança?
""")

# ==========================================
# BARRA LATERAL (CONTROLES)
# ==========================================
st.sidebar.header("Parâmetros do Sistema")

a0 = st.sidebar.slider(
    "Aceleração própria (a₀)", 
    min_value=0.5, max_value=3.0, value=1.0, step=0.1,
    help="Define a curvatura da hipérbole. Quanto maior a aceleração, mais próxima a trajetória fica da origem."
)

x0 = st.sidebar.slider(
    "Posição de emissão do fóton (x₀)", 
    min_value=-2.0, max_value=2.0, value=0.5, step=0.1,
    help="Posição de onde o fóton é disparado em t=0."
)

# ==========================================
# CÁLCULOS FÍSICOS
# ==========================================
# Posição do horizonte (onde a assíntota cruza o eixo x) é sempre 0 na origem,
# mas a distância crítica para o fóton é 1/a0.
distancia_critica = 1 / a0

# Cálculo do encontro baseado na fórmula deduzida no exercício
if x0 > 0 and x0 < distancia_critica:
    t_enc = (1/a0**2 - x0**2) / (2 * x0)
    x_enc = x0 + t_enc
    encontro_ocorre = True
    status_msg = "O fóton alcança o observador acelerado."
    status_cor = "success"
elif x0 == 0:
    encontro_ocorre = False
    status_msg = "Caso crítico: O fóton persegue o observador para sempre (t → ∞) paralelamente à assíntota."
    status_cor = "warning"
elif x0 >= distancia_critica:
    # Se o fóton for emitido de uma posição x0 >= 1/a0, ele não precisaria "alcançar" a assíntota, 
    # ele já intercepta a trajetória, mas a fórmula do exercício foca no fóton vindo de trás.
    # Fisicamente, se x0 > 1/a0, o fóton cruza a hipérbole, mas vamos tratar o domínio clássico x0 < 1/a0.
    t_enc = (1/a0**2 - x0**2) / (2 * x0)
    if t_enc < 0:
        t_enc = -t_enc # Interseção no passado, irrelevante para t>0
    x_enc = x0 + t_enc
    encontro_ocorre = True
    status_msg = "O fóton é emitido à frente do horizonte e intercepta a nave."
    status_cor = "info"
else: # x0 < 0
    encontro_ocorre = False
    status_msg = "O fóton foi emitido além do horizonte (x₀ < 0). Ele nunca alcançará o observador."
    status_cor = "error"

# ==========================================
# INTERFACE PRINCIPAL
# ==========================================
col1, col2 = st.columns([1, 1.5])

with col1:
    st.subheader("Análise Analítica")
    st.markdown(f"**Posição do horizonte de eventos (Assíntota):** $x = t$")
    st.markdown(f"**Distância crítica ($1/a_0$):** `{distancia_critica:.2f}`")
    
    if encontro_ocorre and x0 > 0:
        st.markdown(f"**Tempo de encontro ($t$):** `{t_enc:.2f}`")
        st.markdown(f"**Posição de encontro ($x$):** `{x_enc:.2f}`")
    else:
        st.markdown("**Tempo de encontro ($t$):** $\\infty$")
    
    # Exibe a mensagem de status com a cor apropriada
    if status_cor == "success":
        st.success(status_msg)
    elif status_cor == "warning":
        st.warning(status_msg)
    elif status_cor == "info":
        st.info(status_msg)
    else:
        st.error(status_msg)

    st.markdown("---")
    st.markdown("### A Matemática")
    st.latex(r"x_{obs}^2 - t^2 = \frac{1}{a_0^2}")
    st.latex(r"x_{f\acute{o}ton} = x_0 + t")
    st.markdown("Igualando as posições para o encontro:")
    st.latex(r"t = \frac{1/a_0^2 - x_0^2}{2x_0}")

with col2:
    # Geração do Gráfico
    fig, ax = plt.subplots(figsize=(6, 6))
    
    # Configuração dos eixos (estilo novo_eixo)
    limite = 5.0
    ax.set_xlim(-1.0, limite)
    ax.set_ylim(-1.0, limite)
    ax.set_aspect("equal")
    ax.axhline(0, color="black", lw=0.6, zorder=1)
    ax.axvline(0, color="black", lw=0.6, zorder=1)
    ax.set_xlabel(r"$x$ (Espaço)")
    ax.set_ylabel(r"$t$ (Tempo Coordinado)")
    
    # 1. Cone de luz (Assíntotas)
    t_vals = np.linspace(-1, limite, 100)
    ax.plot(t_vals, t_vals, color="0.15", lw=1.4, ls="--", label="Cone de Luz (Assíntota / Horizonte)")
    
    # 2. Observador Acelerado (Hipérbole)
    # x = sqrt(t^2 + 1/a0^2)
    x_obs = np.sqrt(t_vals**2 + 1/a0**2)
    ax.plot(x_obs, t_vals, color="#4C72B0", lw=2, label="Observador Acelerado")
    
    # 3. Fóton
    t_foton = np.linspace(0, limite, 100)
    x_foton = x0 + t_foton
    ax.plot(x_foton, t_foton, color="#C08A1E", lw=2, label="Fóton")
    ax.plot([x0], [0], "o", color="#C08A1E", ms=6, zorder=5)
    ax.annotate(r"$x_0$", (x0, 0), textcoords="offset points", xytext=(0, -15), ha='center', path_effects=HALO)
    
    # Marca o encontro, se houver e estiver dentro dos limites do gráfico
    if encontro_ocorre and x0 > 0 and t_enc <= limite:
        ax.plot([x_enc], [t_enc], "o", color="#B0413E", ms=7, zorder=5)
        ax.annotate(r"Encontro", (x_enc, t_enc), textcoords="offset points", xytext=(-10, 10), ha='right', path_effects=HALO)
    
    # Preenchimento visual para a região inalcançável (Além do horizonte)
    x_preenchimento = np.linspace(-1, limite, 100)
    ax.fill_betweenx(t_vals, -1, t_vals, color="#DD8452", alpha=0.10, lw=0)
    ax.text(1.5, 3.5, "Dentro do\nHorizonte", ha="center", fontsize=10, color="0.4", path_effects=HALO)
    ax.text(-0.2, 1.5, "Além do\nHorizonte", ha="center", fontsize=10, color="#B0413E", path_effects=HALO)

    ax.legend(loc="lower right", fontsize=9, frameon=True)
    ax.set_title("Diagrama de Espaço-Tempo: Horizonte de Rindler")
    
    fig.tight_layout()
    st.pyplot(fig)