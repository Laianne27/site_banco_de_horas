import gspread
import streamlit as st
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta
import pandas as pd

# Defina o escopo
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Carregue suas credenciais
creds = ServiceAccountCredentials.from_json_keyfile_name("C:\Users\Cliente\Downloads\site-cq-moinho-727d76d37cc2.json", scope)

# Autorize o cliente gspread
gc = gspread.authorize(creds)

# Defina a planilha correta para gravar os registros de ponto
planilha_bd_moinho = gc.open("BD_CQ_MOINHO_SITE").sheet1  # Abra a primeira aba da planilha correta

# Acesse a planilha com os colaboradores
planilha_colaboradores = gc.open("Colaboradores").sheet1
banco_horas_aba = gc.open("Colaboradores").worksheet("Banco Atual")

# Carregar os dados da planilha em um DataFrame
dados_colaboradores = planilha_colaboradores.get_all_records()
df_colaboradores = pd.DataFrame(dados_colaboradores)

dados_pontos = planilha_bd_moinho.get_all_records()
df_pontos = pd.DataFrame(dados_pontos)

# Função para registrar ponto
def registrar_ponto(nome, entrada, saida, data):
    try:
        planilha_bd_moinho.append_row([nome, data.strftime("%d/%m/%Y"), entrada.strftime("%H:%M"), saida.strftime("%H:%M")])
        st.success("Ponto registrado com sucesso!")
        atualizar_banco_horas(nome, entrada, saida, data)
    except Exception as e:
        st.error(f"Erro ao registrar ponto: {e}")

# Função para atualizar o banco de horas
def atualizar_banco_horas(nome, entrada, saida, data):
    df_banco_horas = banco_horas_aba.get_all_records()
    df_banco_horas = pd.DataFrame(df_banco_horas)

    if nome in df_banco_horas['Nome'].values:
        saldo_atual = df_banco_horas.loc[df_banco_horas['Nome'] == nome, 'Banco de Horas'].values[0]
        saldo_atual_timedelta = pd.to_timedelta(saldo_atual)
    else:
        saldo_atual_timedelta = pd.Timedelta(0)

    horas_trabalhadas = (saida - entrada).total_seconds() / 3600
    horas_trabalhadas_timedelta = pd.to_timedelta(horas_trabalhadas, unit='h')

    novo_saldo_timedelta = saldo_atual_timedelta + horas_trabalhadas_timedelta
    novo_saldo = str(novo_saldo_timedelta)

    df_banco_horas.loc[df_banco_horas['Nome'] == nome, 'Banco de Horas'] = novo_saldo
    banco_horas_aba.update("A2", df_banco_horas.values.tolist())

# Função para calcular saldo de horas
def calcular_saldo_horas(nome):
    registros = planilha_colaboradores.get_all_records()
    entradas = []
    saidas = []

    for registro in registros:
        if registro['Nome'] == nome:
            if 'Entrada' in registro:
                entradas.append(datetime.strptime(f"{registro['Data']} {registro['Entrada']}", "%d/%m/%Y %H:%M"))
            if 'Saída' in registro:
                saidas.append(datetime.strptime(f"{registro['Data']} {registro['Saída']}", "%d/%m/%Y %H:%M"))

    saldo_horas = timedelta()
    for entrada, saida in zip(entradas, saidas):
        saldo_horas += (saida - entrada)

    return saldo_horas

# Página de Registro de Ponto
def pagina_registro_ponto():
    st.title("Sistema de Registro de Ponto")

    nome = st.selectbox("Selecione seu nome:", df_colaboradores['Nome'].unique())

    colaborador_info = df_colaboradores[df_colaboradores['Nome'] == nome].iloc[0]
    turno = colaborador_info['Turno']
    horario_entrada = colaborador_info['Horário de Entrada']
    horario_saida = colaborador_info['Horário de Saída']

    st.write(f"Turno: {turno}")

    entrada_str = st.text_input("Hora de Entrada (HH:MM):", value=horario_entrada)
    saida_str = st.text_input("Hora de Saída (HH:MM):", value=horario_saida)

    data_formatada = st.date_input("Data:", datetime.today(), format="DD/MM/YYYY")

    try:
        entrada = datetime.strptime(f"{data_formatada} {entrada_str}", "%Y-%m-%d %H:%M")
        saida = datetime.strptime(f"{data_formatada} {saida_str}", "%Y-%m-%d %H:%M")

        if st.button("Registrar Ponto"):
            registrar_ponto(nome, entrada, saida, data_formatada)

    except ValueError as e:
        st.error(f"Erro: {e}. Por favor, insira horários válidos no formato 'HH:MM'.")

# Página de Consulta e Correção de Ponto
def pagina_consulta_correcao():
    st.title("Consulta e Correção de Ponto")

    nome_consulta = st.selectbox("Selecione seu nome para consulta:", df_pontos['Nome'].unique())

    df_colaborador = df_pontos[df_pontos['Nome'] == nome_consulta]

    st.subheader(f"Últimas Batidas de Ponto de {nome_consulta}")
    if not df_colaborador.empty:
        st.dataframe(df_colaborador[['Data', 'Entrada', 'Saída']])
        
        index = st.number_input("Selecione o número da batida para corrigir:", min_value=0, max_value=len(df_colaborador)-1, step=1)
        batida_selecionada = df_colaborador.iloc[index]

        st.write("Entrada Atual:", batida_selecionada['Entrada'])
        st.write("Saída Atual:", batida_selecionada['Saída'])
        st.write("Data Atual:", batida_selecionada['Data'])

        nova_entrada = st.text_input("Corrija a Hora de Entrada (HH:MM):", batida_selecionada['Entrada'])
        nova_saida = st.text_input("Corrija a Hora de Saída (HH:MM):", batida_selecionada['Saída'])
        nova_data = st.date_input("Corrija a Data:", value=datetime.strptime(batida_selecionada['Data'], "%d/%m/%Y"))

        if st.button("Salvar Alterações"):
            atualizar_ponto(batida_selecionada.name, nova_entrada, nova_saida, nova_data.strftime("%d/%m/%Y"))
    else:
        st.write("Nenhuma batida de ponto encontrada.")

# Função principal para navegação
def main():
    pagina = st.sidebar.selectbox("Navegar para", ["Registro de Ponto", "Consulta e Correção de Ponto"])

    if pagina == "Registro de Ponto":
        pagina_registro_ponto()
    elif pagina == "Consulta e Correção de Ponto":
        pagina_consulta_correcao()

if __name__ == "__main__":
    main()
