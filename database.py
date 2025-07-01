from supabase import create_client, Client
from datetime import datetime
from dateutil.relativedelta import relativedelta
from dateutil import parser
import streamlit as st
import os
from dotenv import load_dotenv
load_dotenv()

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def criar_usuario(usuario, senha_hash):
    if isinstance(senha_hash, bytes):
        senha_hash = senha_hash.decode("utf-8")
    try:
        resp = supabase.table("usuarios").insert({"usuario": usuario, "senha": senha_hash}).execute()
        print("Resposta do Supabase:", resp)
        return True
    except Exception as e:
        print("Erro ao inserir usuário:", e)
        return False

def buscar_usuario(usuario):
    result = supabase.table("usuarios").select("senha").eq("usuario", usuario).execute()
    if result.data:
        return (result.data[0]["senha"],)
    return None

def adicionar_transacao(usuario, tipo, descricao, valor, data):
    supabase.table("transacoes").insert({
        "usuario": usuario,
        "tipo": tipo,
        "descricao": descricao,
        "valor": valor,
        "data": data
    }).execute()

def adicionar_transacao_parcelada(usuario, tipo, descricao, valor_total, data_inicial, parcelas):
    valor_parcela = round(valor_total / parcelas, 2)
    for i in range(parcelas):
        data_parcela = (datetime.strptime(data_inicial, "%Y-%m-%d %H:%M") + relativedelta(months=i)).strftime("%Y-%m-%d %H:%M:%S")
        descricao_parcela = f"{descricao} ({i+1}/{parcelas})"
        adicionar_transacao(usuario, tipo, descricao_parcela, valor_parcela, data_parcela)

def filtro_valido(valor):
    return valor and valor not in ("Todos", "Selecione...")

def listar_transacoes(usuario, tipo="Todos", data_ini=None, data_fim=None, mes=None, ano=None):
    query = supabase.table("transacoes").select("*").eq("usuario", usuario)
    if tipo != "Todos":
        query = query.eq("tipo", tipo)
    if data_ini:
        query = query.gte("data", data_ini + " 00:00:00")
    if data_fim:
        query = query.lte("data", data_fim + " 23:59:59")
    # Não use filtro SQL para mês/ano aqui!
    resultado = query.execute().data

    # Agora filtre por mês/ano em Python
    from dateutil import parser
    if mes and mes != "Todos":
        resultado = [t for t in resultado if parser.parse(t["data"]).strftime("%m") == str(mes).zfill(2)]
    if ano and ano != "Todos":
        resultado = [t for t in resultado if parser.parse(t["data"]).strftime("%Y") == str(ano)]
    return resultado

def calcular_saldo(usuario):
    transacoes = listar_transacoes(usuario)
    total = 0
    for t in transacoes:
        valor = float(t["valor"])
        total += valor if t["tipo"] == "Receita" else -valor
    return total

def obter_resumo_por_tipo(usuario, tipo="Todos", data_ini=None, data_fim=None, mes=None, ano=None):
    transacoes = listar_transacoes(usuario, tipo, data_ini, data_fim, mes, ano)
    resumo = {}
    for t in transacoes:
        tipo = t["tipo"]
        resumo[tipo] = resumo.get(tipo, 0) + float(t["valor"])
    return list(resumo.items())

def obter_resumo_mensal(usuario, tipo="Todos", data_ini=None, data_fim=None, mes=None, ano=None):
    transacoes = listar_transacoes(usuario, tipo, data_ini, data_fim, mes, ano)
    resumo = {}
    for t in transacoes:
        #dt = datetime.strptime(t["data"], "%Y-%m-%dT%H:%M:%S.%fZ")
        dt = parser.parse(t["data"])
        mes_ano = dt.strftime("%Y-%m")
        chave = (mes_ano, t["tipo"])
        resumo[chave] = resumo.get(chave, 0) + float(t["valor"])
    return [(k[0], k[1], v) for k, v in resumo.items()]

def remover_transacao_por_id(trans_id):
    supabase.table("transacoes").delete().eq("id", trans_id).execute()

def remover_transacao_por_descricao(descricao, usuario):
    supabase.table("transacoes").delete().eq("descricao", descricao).eq("usuario", usuario).execute()

def obter_anos_disponiveis(usuario):
    transacoes = listar_transacoes(usuario)
    anos = set()
    for t in transacoes:
        #dt = datetime.strptime(t["data"], "%Y-%m-%dT%H:%M:%S.%fZ")
        dt = parser.parse(t["data"])
        anos.add(dt.strftime("%Y"))
    return sorted(anos, reverse=True)

def listar_transacoes_para_exportar(usuario, tipo="Todos", data_ini=None, data_fim=None, mes=None, ano=None):
    return listar_transacoes(usuario, tipo, data_ini, data_fim, mes, ano)
