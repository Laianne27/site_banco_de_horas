import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime

# Configurando o layout da página como "wide" para usar toda a largura da tela
st.set_page_config(layout="wide")

st.title("Registro de Batidas de Ponto")

colaborador = st.text_input("Nome do Colaborador")
data = st.date_input("Data", datetime.date.today())
hora_entrada = st.time_input("Horário de Entrada")
hora_saida = st.time_input("Horário de Saída")
pausa = st.time_input("Pausa")

if st.button("Registrar"):
    # Adiciona os dados na planilha
    sheet.append_row([colaborador, str(data), str(hora_entrada), str(hora_saida), str(pausa)])
    st.success("Batida registrada com sucesso!")



# Menu lateral para selecionar a página
st.sidebar.title('Navegação')
