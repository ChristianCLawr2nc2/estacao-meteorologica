import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'dados.db')
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), 'schema.sql')


def get_db_connection():
    """Retorna uma conexão configurada com row_factory e suporte a WAL para escrita concorrente."""
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.execute('PRAGMA journal_mode=WAL')
    conn.execute('PRAGMA busy_timeout=5000')
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Cria as tabelas se não existirem, executando o schema.sql."""
    conn = get_db_connection()
    with open(SCHEMA_PATH, 'r') as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()
    print("[DB] Banco de dados inicializado com sucesso.")


def inserir_leitura(temperatura, umidade, pressao=None, localizacao='Lab IoT - Inteli'):
    """Insere uma nova leitura no banco. Retorna o id gerado."""
    conn = get_db_connection()
    cursor = conn.execute(
        'INSERT INTO leituras (temperatura, umidade, pressao, localizacao) VALUES (?, ?, ?, ?)',
        (temperatura, umidade, pressao, localizacao)
    )
    conn.commit()
    novo_id = cursor.lastrowid
    conn.close()
    return novo_id


def listar_leituras(limite=50, offset=0):
    """Retorna leituras com paginação básica, ordenadas pela mais recente."""
    conn = get_db_connection()
    rows = conn.execute(
        'SELECT * FROM leituras ORDER BY timestamp DESC LIMIT ? OFFSET ?',
        (limite, offset)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def contar_leituras():
    """Retorna o total de leituras no banco."""
    conn = get_db_connection()
    total = conn.execute('SELECT COUNT(*) FROM leituras').fetchone()[0]
    conn.close()
    return total


def buscar_leitura(id):
    """Retorna uma leitura pelo id."""
    conn = get_db_connection()
    row = conn.execute('SELECT * FROM leituras WHERE id = ?', (id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def atualizar_leitura(id, dados):
    """Atualiza campos de uma leitura. Retorna True se encontrou e atualizou."""
    campos_permitidos = {'temperatura', 'umidade', 'pressao', 'localizacao'}
    campos = {k: v for k, v in dados.items() if k in campos_permitidos}
    if not campos:
        return False
    set_clause = ', '.join(f'{k} = ?' for k in campos)
    valores = list(campos.values()) + [id]
    conn = get_db_connection()
    cursor = conn.execute(f'UPDATE leituras SET {set_clause} WHERE id = ?', valores)
    conn.commit()
    atualizado = cursor.rowcount > 0
    conn.close()
    return atualizado


def deletar_leitura(id):
    """Remove uma leitura pelo id. Retorna True se encontrou e deletou."""
    conn = get_db_connection()
    cursor = conn.execute('DELETE FROM leituras WHERE id = ?', (id,))
    conn.commit()
    deletado = cursor.rowcount > 0
    conn.close()
    return deletado


def estatisticas(horas=24):
    """Retorna média, mínimo e máximo de temperatura, umidade e pressão das últimas N horas."""
    conn = get_db_connection()
    row = conn.execute('''
        SELECT
            ROUND(AVG(temperatura), 2) as temp_media,
            ROUND(MIN(temperatura), 2) as temp_min,
            ROUND(MAX(temperatura), 2) as temp_max,
            ROUND(AVG(umidade), 2)    as umid_media,
            ROUND(MIN(umidade), 2)    as umid_min,
            ROUND(MAX(umidade), 2)    as umid_max,
            ROUND(AVG(pressao), 2)    as pres_media,
            ROUND(MIN(pressao), 2)    as pres_min,
            ROUND(MAX(pressao), 2)    as pres_max,
            COUNT(*)                  as total
        FROM leituras
        WHERE timestamp >= datetime('now', 'localtime', ? || ' hours')
    ''', (f'-{horas}',)).fetchone()
    conn.close()
    return dict(row) if row else {}


def leituras_para_grafico(limite=50):
    """Retorna leituras ordenadas cronologicamente para o gráfico."""
    conn = get_db_connection()
    rows = conn.execute(
        'SELECT temperatura, umidade, pressao, timestamp FROM leituras ORDER BY timestamp DESC LIMIT ?',
        (limite,)
    ).fetchall()
    conn.close()
    dados = [dict(r) for r in rows]
    dados.reverse()
    return dados
