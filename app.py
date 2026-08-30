import streamlit as st

# Configura a aba do navegador
st.set_page_config(
    page_title="Portal de Simulações - Prof. Ricardo",
    page_icon="🌌",
    layout="centered"
)

# Título da página
st.title("Simulações")
st.write("**Prof. Ricardo Albrecht**")

st.divider() # Cria uma linha de separação

# Mensagem de boas-vindas
st.markdown("""
**Atualmente disponível no menu:**
- **1. Espectro CMB:** Simulador termodinâmico da Radiação Cósmica de Fundo (Cosmologia).
""")