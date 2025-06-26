# import sqlite3
# from datetime import datetime
# from dateutil.relativedelta import relativedelta
# from supabase import create_client

# supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# def conexao():
#     conn = sqlite3.connect('data/financas.db')
#     return conn

# conn = conexao()
# cursor = conn.cursor()
# cursor.execute('''
# CREATE TABLE IF NOT EXISTS usuarios (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     usuario TEXT UNIQUE,
#     senha BLOB
# )
# ''')
# conn.commit()

# def criar_usuario(usuario, senha_hash):
#     conn = conexao()
#     cursor = conn.cursor()
#     try:
#         cursor.execute('INSERT INTO usuarios (usuario, senha) VALUES (?, ?)', (usuario, senha_hash))
#         conn.commit()
#         return True
#     except sqlite3.IntegrityError:
#         return False

# def buscar_usuario(usuario):
#     conn = conexao()
#     cursor = conn.cursor()
#     cursor.execute('SELECT senha FROM usuarios WHERE usuario = ?', (usuario,))
#     return cursor.fetchone()

# def criar_tabela_transacoes():
#     conn = conexao()
#     cursor = conn.cursor()
#     cursor.execute('''
#     CREATE TABLE IF NOT EXISTS transacoes (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         usuario TEXT,
#         tipo TEXT,
#         descricao TEXT,
#         valor REAL,
#         data TEXT
#     )
#     ''')
#     conn.commit()



# def adicionar_transacao(usuario, tipo, descricao, valor, data):
#     conn = conexao()
#     cursor = conn.cursor()
#     cursor.execute('''
#         INSERT INTO transacoes (usuario, tipo, descricao, valor, data)
#         VALUES (?, ?, ?, ?, ?)
#     ''', (usuario, tipo, descricao, valor, data))
#     conn.commit()

# def filtro_valido(valor):
#     return valor and valor not in ("Todos", "Selecione...")

# def listar_transacoes(usuario, tipo="Todos", data_ini=None, data_fim=None, mes=None, ano=None):
# #def listar_transacoes(usuario, tipo="Todos", data_ini=None, data_fim=None):
#     conn = conexao()
#     cursor = conn.cursor()
#     query = "SELECT id, tipo, descricao, valor, data FROM transacoes WHERE usuario = ?"
#     params = [usuario]

#     if data_ini:
#         try:
#             # Garante que o formato esteja correto
#             datetime.strptime(data_ini, "%Y-%m-%d")
#             data_ini += " 00:00:00"
#         except ValueError:
#             pass
#         query += " AND data >= ?"
#         params.append(data_ini)

#     if data_fim:
#         try:
#             datetime.strptime(data_fim, "%Y-%m-%d")
#             data_fim += " 23:59:59"
#         except ValueError:
#             pass
#         query += " AND data <= ?"
#         params.append(data_fim)   

#     if filtro_valido(tipo):
#         query += " AND tipo = ?"
#         params.append(tipo)

#     if filtro_valido(mes):
#         query += " AND strftime('%m', data) = ?"
#         params.append(mes)

#     if filtro_valido(ano):
#         query += " AND strftime('%Y', data) = ?"
#         params.append(ano)

#     query += " ORDER BY data DESC"
#     cursor.execute(query, params)
#     dados = cursor.fetchall()
#     conn.close()
#     return dados

# def calcular_saldo(usuario):
#     conn = conexao()
#     cursor = conn.cursor()
#     cursor.execute('SELECT tipo, valor FROM transacoes WHERE usuario = ?', (usuario,))
#     total = 0
#     for tipo, valor in cursor.fetchall():
#         total += valor if tipo == "Receita" else -valor
#     return total

# def obter_resumo_por_tipo(usuario, tipo="Todos", data_ini=None, data_fim=None, mes=None, ano=None):
#     conn = conexao()
#     cursor = conn.cursor()

#     query = '''
#         SELECT tipo, SUM(valor)
#         FROM transacoes
#         WHERE usuario = ?
#     '''
#     params = [usuario]

#     if tipo and tipo != "Selecione..." and tipo != "Todos":
#         query += " AND tipo = ?"
#         params.append(tipo)

#     if data_ini:
#         query += " AND data >= ?"
#         params.append(data_ini + " 00:00:00")

#     if data_fim:
#         query += " AND data <= ?"
#         params.append(data_fim + " 23:59:59")

#     if mes and mes != "Selecione...":
#         query += " AND strftime('%m', data) = ?"
#         params.append(mes)

#     if ano and ano != "Selecione...":
#         query += " AND strftime('%Y', data) = ?"
#         params.append(ano)

#     query += " GROUP BY tipo"
#     cursor.execute(query, params)
#     resultado = cursor.fetchall()
#     conn.close()
#     return resultado

# def obter_resumo_mensal(usuario, tipo="Todos", data_ini=None, data_fim=None, mes=None, ano=None):
#     conn = conexao()
#     cursor = conn.cursor()

#     query = '''
#         SELECT strftime('%Y-%m', data) as mes, tipo, SUM(valor)
#         FROM transacoes
#         WHERE usuario = ?
#     '''
#     params = [usuario]

#     if tipo and tipo not in ["Todos", "Selecione..."]:
#         query += " AND tipo = ?"
#         params.append(tipo)

#     if data_ini:
#         query += " AND data >= ?"
#         params.append(data_ini + " 00:00:00")

#     if data_fim:
#         query += " AND data <= ?"
#         params.append(data_fim + " 23:59:59")

#     if mes and mes != "Selecione...":
#         query += " AND strftime('%m', data) = ?"
#         params.append(mes)

#     if ano and ano != "Selecione...":
#         query += " AND strftime('%Y', data) = ?"
#         params.append(ano)

#     query += " GROUP BY mes, tipo ORDER BY mes ASC"
#     cursor.execute(query, params)
#     resultado = cursor.fetchall()
#     conn.close()
#     return resultado

# def remover_transacao_por_id(trans_id):
#     conn = conexao()
#     cursor = conn.cursor()
#     cursor.execute('DELETE FROM transacoes WHERE id = ?', (trans_id,))
#     conn.commit()
#     conn.close()

# def remover_transacao_por_descricao(descricao, usuario):
#     conn = conexao()
#     cursor = conn.cursor()
#     cursor.execute("DELETE FROM transacoes WHERE descricao=? AND usuario=?", (descricao, usuario))
#     conn.commit()
#     conn.close()

# def obter_anos_disponiveis(usuario):
#     conn = conexao()
#     cursor = conn.cursor()
#     cursor.execute('''
#         SELECT DISTINCT strftime('%Y', data) FROM transacoes
#         WHERE usuario = ?
#         ORDER BY 1 DESC
#     ''', (usuario,))

#     anos = [row[0] for row in cursor.fetchall()]
#     conn.close()
#     return anos

# def adicionar_transacao_parcelada(usuario, tipo, descricao, valor_total, data_inicial, parcelas):
#     conn = conexao()
#     cursor = conn.cursor()

#     valor_parcela = round(valor_total / parcelas, 2)

#     for i in range(parcelas):
#         data_parcela = (datetime.strptime(data_inicial, "%Y-%m-%d %H:%M") + relativedelta(months=i)).strftime("%Y-%m-%d %H:%M:%S")
#         descricao_parcela = f"{descricao} ({i+1}/{parcelas})"

#         cursor.execute('''
#             INSERT INTO transacoes (usuario, tipo, descricao, valor, data)
#             VALUES (?, ?, ?, ?, ?)
#         ''', (usuario, tipo, descricao_parcela, valor_parcela, data_parcela))

#     conn.commit()
#     conn.close()

# def listar_transacoes_para_exportar(usuario, tipo="Todos", data_ini=None, data_fim=None, mes=None, ano=None):
#     conn = conexao()
#     cursor = conn.cursor()

#     query = "SELECT tipo, descricao, valor, data FROM transacoes WHERE usuario = ?"
#     params = [usuario]

#     if tipo and tipo not in ("Todos", "Selecione..."):
#         query += " AND tipo = ?"
#         params.append(tipo)

#     if data_ini:
#         query += " AND data >= ?"
#         params.append(data_ini + " 00:00:00")

#     if data_fim:
#         query += " AND data <= ?"
#         params.append(data_fim + " 23:59:59")

#     if mes and mes != "Selecione...":
#         query += " AND strftime('%m', data) = ?"
#         params.append(mes)

#     if ano and ano != "Selecione...":
#         query += " AND strftime('%Y', data) = ?"
#         params.append(ano)

#     query += " ORDER BY data DESC"
#     cursor.execute(query, params)
#     resultado = cursor.fetchall()
#     conn.close()
#     return resultado

from supabase import create_client
from datetime import datetime
from dateutil.relativedelta import relativedelta
from dateutil import parser
import streamlit as st
import os
from dotenv import load_dotenv
load_dotenv()

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

print("SUPABASE_URL:", SUPABASE_URL)
print("SUPABASE_KEY:", SUPABASE_KEY)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def criar_usuario(usuario, senha_hash):
    try:
        supabase.table("usuarios").insert({"usuario": usuario, "senha": senha_hash}).execute()
        return True
    except Exception:
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
    query = supabase.table("transacoes").select("id, tipo, descricao, valor, data").eq("usuario", usuario)

    if filtro_valido(tipo):
        query = query.eq("tipo", tipo)
    if data_ini:
        query = query.gte("data", data_ini + " 00:00:00")
    if data_fim:
        query = query.lte("data", data_fim + " 23:59:59")
    if filtro_valido(mes):
        query = query.filter("extract(month from data) = ", mes)
    if filtro_valido(ano):
        query = query.filter("extract(year from data) = ", ano)

    return query.order("data", desc=False).execute().data

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
        dt = datetime.strptime(t["data"], "%Y-%m-%dT%H:%M:%S.%fZ")
        #dt = parser.parse(t["data"])
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
        dt = datetime.strptime(t["data"], "%Y-%m-%dT%H:%M:%S.%fZ")
        #dt = parser.parse(t["data"])
        anos.add(dt.strftime("%Y"))
    return sorted(anos, reverse=True)

def listar_transacoes_para_exportar(usuario, tipo="Todos", data_ini=None, data_fim=None, mes=None, ano=None):
    return listar_transacoes(usuario, tipo, data_ini, data_fim, mes, ano)
