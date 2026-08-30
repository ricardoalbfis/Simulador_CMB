import streamlit as st
import numpy as np
from scipy.integrate import quad, cumulative_trapezoid
import matplotlib.pyplot as plt

# Configuração inicial da página
st.set_page_config(page_title="Paradoxo dos Gêmeos", layout="centered")

st.title("Paradoxo dos Gêmeos: Perfis de Velocidade")
st.markdown("""
Esta simulação compara como diferentes perfis de aceleração e velocidade afetam o **tempo próprio acumulado** (envelhecimento) de um viajante relativístico. 
O tempo próprio $\\tau$ é obtido integrando $\\sqrt{1 - v(t)^2}$.
""")

# ==========================================
# BARRA LATERAL (Controles Interativos)
# ==========================================
st.sidebar.header("Parâmetros da Viagem")

T = st.sidebar.slider(
    "Tempo coordenado total (T)", 
    min_value=1.0, max_value=50.0, value=10.0, step=1.0,
    help="Tempo total medido pelo gêmeo que fica na Terra."
)

v0 = st.sidebar.slider(
    "Velocidade máxima (v0)", 
    min_value=0.0, # <-- Opção 0 adicionada aqui
    max_value=0.999999999, 
    value=0.80, 
    step=0.000000001,
    format="%.9f",
    help="Fração da velocidade da luz (c=1). Você pode clicar no número acima da barra para digitar valores extremos (ex: 0.999999999 ou 0.0)."
)

# ==========================================
# FUNÇÕES DE VELOCIDADE
# ==========================================
def v_constante(t):
    return float(v0) if np.isscalar(t) else np.full_like(t, v0, dtype=float)

def v_seno(t):
    return v0 * np.sin(np.pi * t / T)

def v_seno_quadrado(t):
    return v0 * np.sin(np.pi * t / T)**2

def v_trapezio(t):
    t_mod = np.atleast_1d(t)
    res = np.zeros_like(t_mod, dtype=float)
    
    dt1 = T / 4.0
    dt2 = 3.0 * T / 4.0
    
    mask1 = (t_mod >= 0) & (t_mod < dt1)
    mask2 = (t_mod >= dt1) & (t_mod <= dt2)
    mask3 = (t_mod > dt2) & (t_mod <= T)
    
    res[mask1] = v0 * (t_mod[mask1] / dt1)
    res[mask2] = v0
    res[mask3] = v0 * ((T - t_mod[mask3]) / (T - dt2))
    
    return res[0] if np.isscalar(t) else res

def v_onda_quadrada(t):
    k = 4.0
    return v0 * np.tanh(k * np.sin(np.pi * t / T)) / np.tanh(k)

# Dicionário mapeando os nomes para as funções
todos_perfis = {
    "Velocidade Constante (Clássico)": v_constante,
    "Senoide": v_seno,
    "Senoide ao quadrado": v_seno_quadrado,
    "Trapezoide": v_trapezio,
    "Onda quadrada suavizada": v_onda_quadrada,
}

# ==========================================
# SELEÇÃO DE PERFIS
# ==========================================
st.sidebar.markdown("---")
st.sidebar.header("Perfis para Comparação")
perfis_selecionados = st.sidebar.multiselect(
    "Escolha os perfis de velocidade que deseja visualizar:",
    options=list(todos_perfis.keys()),
    default=list(todos_perfis.keys())
)

# ==========================================
# CÁLCULOS E GRÁFICOS
# ==========================================
if not perfis_selecionados:
    st.warning("👈 Por favor, selecione pelo menos um perfil de velocidade na barra lateral.")
else:
    resultados = []
    t_grid = np.linspace(0, T, 1000)

    # Cálculo da integral (tempo próprio) para cada perfil selecionado
    for nome in perfis_selecionados:
        func = todos_perfis[nome]
        
        def integrando(t):
            return np.sqrt(1.0 - func(t)**2)
        
        tau_total, _ = quad(integrando, 0.0, T)
        resultados.append((nome, tau_total, func))

    # Ordena do que menos envelhece (menor tau) para o que mais envelhece
    resultados.sort(key=lambda x: x[1])

    # Exibição dos resultados textuais
    st.subheader("Resultados do Tempo Próprio ($\\tau$)")
    st.markdown("Ordenados do perfil que **menos envelhece** para o que **mais envelhece**:")
    
    for i, (nome, tau, _) in enumerate(resultados, 1):
        st.write(f"**{i}. {nome}**: $\\tau = {tau:.6f}$")

    # Geração dos gráficos
    st.subheader("Visualização Gráfica")
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 7), sharex=True)

    for nome, tau, func in resultados:
        v_vals = func(t_grid)
        integrando_grid = np.sqrt(1.0 - v_vals**2)
        tau_acumulado = cumulative_trapezoid(integrando_grid, t_grid, initial=0.0)
        
        ax1.plot(t_grid, v_vals, label=nome)
        ax2.plot(t_grid, tau_acumulado, label=f"{nome} ($\\tau$={tau:.2f})")

    # Configuração do Eixo 1 (Velocidade)
    ax1.set_ylabel(r"Velocidade $v(t)$")
    ax1.axhline(0, color="0.6", lw=0.6)
    ax1.legend(fontsize=9, frameon=False, loc="upper right")
    ax1.grid(True, alpha=0.3)

    # Configuração do Eixo 2 (Tempo Próprio)
    ax2.plot(t_grid, t_grid, color="0.4", ls="--", label=r"$t$ (gêmeo na Terra)")
    ax2.set_xlabel(r"Tempo coordenado $t$")
    ax2.set_ylabel(r"Tempo próprio acumulado $\tau$")
    ax2.legend(fontsize=9, frameon=False, loc="upper left")
    ax2.grid(True, alpha=0.3)

    fig.tight_layout()
    
    # Renderiza o gráfico no Streamlit
    st.pyplot(fig)