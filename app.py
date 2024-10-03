
import gspread
import streamlit as st
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta

# Autenticação
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("site-cq-moinho-83dfb808e013.json", scope)
client = gspread.authorize(creds)

# Abrir a planilha
planilha = client.open("BD_CQ_MOINHO_SITE").sheet1

# Dicionário de colaboradores e turnos
colaboradores = {
    "Laianne": {"turno": "Manhã", "entrada": "08:00", "saida": "17:00"},
    "Legolas": {"turno": "Tarde", "entrada": "14:00", "saida": "22:00"},
    "Anna": {"turno": "Noite", "entrada": "22:00", "saida": "06:00"}
}

# Função para registrar o ponto
def registrar_ponto(nome, entrada, saida, tipo):
    agora = datetime.now()
    data = agora.strftime("%Y-%m-%d")
    planilha.append_row([nome, data, entrada, saida])
    st.success("Ponto registrado com sucesso!")

# Função para calcular o saldo de horas
def calcular_saldo_horas(nome):
    registros = planilha.get_all_records()
    entradas = []
    saidas = []

    for registro in registros:
        if registro['Nome'] == nome:
            if registro['Tipo'] == "Entrada":
                entradas.append(datetime.strptime(f"{registro['Data']} {registro['Hora']}", "%Y-%m-%d %H:%M:%S"))
            elif registro['Tipo'] == "Saída":
                saidas.append(datetime.strptime(f"{registro['Data']} {registro['Hora']}", "%Y-%m-%d %H:%M:%S"))

    saldo_horas = timedelta()
    for entrada, saida in zip(entradas, saidas):
        saldo_horas += (saida - entrada)

    return saldo_horas

# Interface do usuário
st.title("Sistema de Registro de Ponto")

# Seleção do colaborador
nome = st.selectbox("Selecione seu nome:", list(colaboradores.keys()))

# Pegar o turno e os horários predefinidos do colaborador
if nome:
    turno = colaboradores[nome]["turno"]
    horario_entrada = colaboradores[nome]["entrada"]
    horario_saida = colaboradores[nome]["saida"]

    st.write(f"Turno: {turno}")

    # Preencher os horários automaticamente, mas permitir que sejam editados
    entrada = st.text_input("Horário de Entrada:", horario_entrada)
    saida = st.text_input("Horário de Saída:", horario_saida)

# Botão único para registrar ponto
if st.button("Registrar Ponto"):
    registrar_ponto(nome, entrada, saida, "Ponto registrado")

if st.button("Ver Saldo de Horas"):
    saldo = calcular_saldo_horas(nome)
    st.write(f"Saldo de horas de {nome}: {saldo}")
