import streamlit as st

# Configura a aba do navegador
st.set_page_config(
    page_title="Portal de Simulações - Ricardo Albrecht",
    page_icon="🌌",
    layout="centered"
)

# Título da página
st.title("Bem-vindo ao Portal de Simulações Interativas! 🚀")
st.write("Desenvolvido pelo **Prof. Ricardo Albrecht**")

st.divider() # Cria uma linha de separação

# Mensagem de boas-vindas
st.markdown("""
Este portal foi criado para reunir simulações que nos ajudam a visualizar e interagir com conceitos complexos da Física e da Matemática.

Seja você das turmas de ensino médio da **EEB Eng Annes Gualberto** ou da engenharia na **UniSENAI**, sinta-se à vontade para explorar os modelos!

👈 **Abra o menu lateral (setinha no canto superior esquerdo)** para escolher e navegar entre os simuladores disponíveis.

---
**Atualmente disponível no menu:**
- **1. Espectro CMB:** Simulador termodinâmico da Radiação Cósmica de Fundo (Cosmologia).
""")