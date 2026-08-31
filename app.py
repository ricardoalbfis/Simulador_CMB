import streamlit as st
import ast
from pathlib import Path

# ==========================================
# CABEÇALHO
# ==========================================
st.title("Simulações")
st.markdown("**Prof. Ricardo Albrecht**")
st.divider()

st.markdown("Atualmente disponível no menu:")

# ==========================================
# LEITURA AUTOMÁTICA DA PASTA 'PAGES'
# ==========================================
pasta_pages = Path("pages")

# Verifica se a pasta pages existe no seu projeto
if pasta_pages.exists():
    
    # Busca todos os arquivos .py dentro da pasta e os coloca em ordem alfabética/numérica
    arquivos_py = sorted(pasta_pages.glob("*.py"))
    
    for arquivo in arquivos_py:
        # 1. FORMATAR O TÍTULO
        # Pega o nome do arquivo (ex: "01_Paradoxo_dos_Gemeos")
        nome_base = arquivo.stem 
        partes = nome_base.split("_", 1)
        
        # Se começar com número (ex: 01_), remove o número. Depois troca "_" por espaço.
        if len(partes) > 1 and partes[0].isdigit():
            titulo = partes[1].replace("_", " ")
        else:
            titulo = nome_base.replace("_", " ")
            
        # Deixa a primeira letra de cada palavra em maiúscula (opcional)
        # titulo = titulo.title() 
        
        # 2. EXTRAIR A DESCRIÇÃO (DOCSTRING)
        descricao = "Simulação interativa." # Texto padrão caso o arquivo não tenha docstring
        
        try:
            with open(arquivo, "r", encoding="utf-8") as f:
                codigo_fonte = f.read()
                
                # O  módulo 'ast' analisa o código Python e consegue fisgar a """docstring""" do topo
                modulo = ast.parse(codigo_fonte)
                doc = ast.get_docstring(modulo)
                
                if doc:
                    # Pega apenas a primeira frase/linha da docstring para o índice não ficar gigante
                    descricao = doc.strip().split('\n')[0]
        except Exception:
            # Ignora erros de leitura (ex: se o código de alguma página estiver quebrado)
            pass 
            
        # 3. EXIBIR O ITEM NA TELA
        st.markdown(f"- **{titulo}**: {descricao}")

else:
    st.info("A pasta 'pages' não foi encontrada. Crie uma pasta chamada 'pages' e coloque suas simulações lá dentro.")