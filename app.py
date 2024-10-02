import streamlit as st

# Configurando o layout da página como "wide" para usar toda a largura da tela
st.set_page_config(layout="wide")

st.title("Registro de Batidas de Ponto")

colaborador = st.text_input("Nome do Colaborador")
data = st.date_input("Data", datetime.date.today())
hora_entrada = st.time_input("Horário de Entrada")
hora_saida = st.time_input("Horário de Saída")
pausa = st.time_input("Pausa")




# Menu lateral para selecionar a página
st.sidebar.title('Navegação')
