import streamlit as st

# Configura a aba do navegador
st.set_page_config(
    page_title="Portal de Simulações - Ricardo Albrecht",
    page_icon="🌌",
    layout="centered"
)

# Título da página
st.title("Portão de Simulações")
st.write("Desenvolvido pelo **Ricardo Albrecht**")

st.divider() # Cria uma linha de separação

# Mensagem de boas-vindas
st.markdown("""

#👈 **Abra o menu lateral (setinha no canto superior esquerdo)** para escolher e navegar entre os simuladores disponíveis.

---
**Atualmente disponível no menu:**
#- **1. Espectro CMB:** Simulador termodinâmico da Radiação Cósmica de Fundo (Cosmologia).
""")