@echo off
echo Sincronizando com o GitHub e atualizando o Streamlit...
git pull origin main --rebase
git add .
git commit -m "Atualizacao automatica do projeto CMB"
git push origin main
echo.
echo Tudo pronto! O site ja esta sendo atualizado.
pause