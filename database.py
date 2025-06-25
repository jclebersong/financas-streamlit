import sqlite3
from datetime import datetime
from dateutil.relativedelta import relativedelta



def conexao():
    conn = sqlite3.connect('data/financas.db')
    return conn

conn = conexao()
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario TEXT UNIQUE,
    senha BLOB
)
''')
conn.commit()

def criar_usuario(usuario, senha_hash):
    conn = conexao()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO usuarios (usuario, senha) VALUES (?, ?)', (usuario, senha_hash))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def buscar_usuario(usuario):
    conn = conexao()
    cursor = conn.cursor()
    cursor.execute('SELECT senha FROM usuarios WHERE usuario = ?', (usuario,))
    return cursor.fetchone()

def criar_tabela_transacoes():
    conn = conexao()
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS transacoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT,
        tipo TEXT,
        descricao TEXT,
        valor REAL,
        data TEXT
    )
    ''')
    conn.commit()

def adicionar_transacao(usuario, tipo, descricao, valor, data):
    conn = conexao()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO transacoes (usuario, tipo, descricao, valor, data)
        VALUES (?, ?, ?, ?, ?)
    ''', (usuario, tipo, descricao, valor, data))
    conn.commit()

def filtro_valido(valor):
    return valor and valor not in ("Todos", "Selecione...")

def listar_transacoes(usuario, tipo="Todos", data_ini=None, data_fim=None, mes=None, ano=None):
#def listar_transacoes(usuario, tipo="Todos", data_ini=None, data_fim=None):
    conn = conexao()
    cursor = conn.cursor()
    query = "SELECT id, tipo, descricao, valor, data FROM transacoes WHERE usuario = ?"
    params = [usuario]

    if data_ini:
        try:
            # Garante que o formato esteja correto
            datetime.strptime(data_ini, "%Y-%m-%d")
            data_ini += " 00:00:00"
        except ValueError:
            pass
        query += " AND data >= ?"
        params.append(data_ini)

    if data_fim:
        try:
            datetime.strptime(data_fim, "%Y-%m-%d")
            data_fim += " 23:59:59"
        except ValueError:
            pass
        query += " AND data <= ?"
        params.append(data_fim)   

    if filtro_valido(tipo):
        query += " AND tipo = ?"
        params.append(tipo)

    if filtro_valido(mes):
        query += " AND strftime('%m', data) = ?"
        params.append(mes)

    if filtro_valido(ano):
        query += " AND strftime('%Y', data) = ?"
        params.append(ano)

    query += " ORDER BY data DESC"
    cursor.execute(query, params)
    dados = cursor.fetchall()
    conn.close()
    return dados

def calcular_saldo(usuario):
    conn = conexao()
    cursor = conn.cursor()
    cursor.execute('SELECT tipo, valor FROM transacoes WHERE usuario = ?', (usuario,))
    total = 0
    for tipo, valor in cursor.fetchall():
        total += valor if tipo == "Receita" else -valor
    return total

def obter_resumo_por_tipo(usuario, tipo="Todos", data_ini=None, data_fim=None, mes=None, ano=None):
    conn = conexao()
    cursor = conn.cursor()

    query = '''
        SELECT tipo, SUM(valor)
        FROM transacoes
        WHERE usuario = ?
    '''
    params = [usuario]

    if tipo and tipo != "Selecione..." and tipo != "Todos":
        query += " AND tipo = ?"
        params.append(tipo)

    if data_ini:
        query += " AND data >= ?"
        params.append(data_ini + " 00:00:00")

    if data_fim:
        query += " AND data <= ?"
        params.append(data_fim + " 23:59:59")

    if mes and mes != "Selecione...":
        query += " AND strftime('%m', data) = ?"
        params.append(mes)

    if ano and ano != "Selecione...":
        query += " AND strftime('%Y', data) = ?"
        params.append(ano)

    query += " GROUP BY tipo"
    cursor.execute(query, params)
    resultado = cursor.fetchall()
    conn.close()
    return resultado

def obter_resumo_mensal(usuario, tipo="Todos", data_ini=None, data_fim=None, mes=None, ano=None):
    conn = conexao()
    cursor = conn.cursor()

    query = '''
        SELECT strftime('%Y-%m', data) as mes, tipo, SUM(valor)
        FROM transacoes
        WHERE usuario = ?
    '''
    params = [usuario]

    if tipo and tipo not in ["Todos", "Selecione..."]:
        query += " AND tipo = ?"
        params.append(tipo)

    if data_ini:
        query += " AND data >= ?"
        params.append(data_ini + " 00:00:00")

    if data_fim:
        query += " AND data <= ?"
        params.append(data_fim + " 23:59:59")

    if mes and mes != "Selecione...":
        query += " AND strftime('%m', data) = ?"
        params.append(mes)

    if ano and ano != "Selecione...":
        query += " AND strftime('%Y', data) = ?"
        params.append(ano)

    query += " GROUP BY mes, tipo ORDER BY mes ASC"
    cursor.execute(query, params)
    resultado = cursor.fetchall()
    conn.close()
    return resultado

def remover_transacao_por_id(trans_id):
    conn = conexao()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM transacoes WHERE id = ?', (trans_id,))
    conn.commit()
    conn.close()

def remover_transacao_por_descricao(descricao, usuario):
    conn = conexao()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transacoes WHERE descricao=? AND usuario=?", (descricao, usuario))
    conn.commit()
    conn.close()

def obter_anos_disponiveis(usuario):
    conn = conexao()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT DISTINCT strftime('%Y', data) FROM transacoes
        WHERE usuario = ?
        ORDER BY 1 DESC
    ''', (usuario,))

    anos = [row[0] for row in cursor.fetchall()]
    conn.close()
    return anos

def adicionar_transacao_parcelada(usuario, tipo, descricao, valor_total, data_inicial, parcelas):
    conn = conexao()
    cursor = conn.cursor()

    valor_parcela = round(valor_total / parcelas, 2)

    for i in range(parcelas):
        data_parcela = (datetime.strptime(data_inicial, "%Y-%m-%d %H:%M") + relativedelta(months=i)).strftime("%Y-%m-%d %H:%M:%S")
        descricao_parcela = f"{descricao} ({i+1}/{parcelas})"

        cursor.execute('''
            INSERT INTO transacoes (usuario, tipo, descricao, valor, data)
            VALUES (?, ?, ?, ?, ?)
        ''', (usuario, tipo, descricao_parcela, valor_parcela, data_parcela))

    conn.commit()
    conn.close()

def listar_transacoes_para_exportar(usuario, tipo="Todos", data_ini=None, data_fim=None, mes=None, ano=None):
    conn = conexao()
    cursor = conn.cursor()

    query = "SELECT tipo, descricao, valor, data FROM transacoes WHERE usuario = ?"
    params = [usuario]

    if tipo and tipo not in ("Todos", "Selecione..."):
        query += " AND tipo = ?"
        params.append(tipo)

    if data_ini:
        query += " AND data >= ?"
        params.append(data_ini + " 00:00:00")

    if data_fim:
        query += " AND data <= ?"
        params.append(data_fim + " 23:59:59")

    if mes and mes != "Selecione...":
        query += " AND strftime('%m', data) = ?"
        params.append(mes)

    if ano and ano != "Selecione...":
        query += " AND strftime('%Y', data) = ?"
        params.append(ano)

    query += " ORDER BY data DESC"
    cursor.execute(query, params)
    resultado = cursor.fetchall()
    conn.close()
    return resultado