"""
app.py — Servidor Flask da Estação Meteorológica IoT
Módulo 5 | Engenharia de Computação | Inteli
"""

from flask import Flask, request, jsonify, render_template, redirect, url_for, abort
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from database import (
    init_db, inserir_leitura, listar_leituras, contar_leituras,
    buscar_leitura, atualizar_leitura, deletar_leitura,
    estatisticas, leituras_para_grafico
)
from config import FLASK_DEBUG, FLASK_PORT

app = Flask(__name__)

# ─── Inicialização ──────────────────────────────────────────────────────────

@app.before_request
def _setup():
    """Garante que o banco existe antes de qualquer requisição."""
    pass  # init_db() é chamado no __main__


# ─── Painel Principal ───────────────────────────────────────────────────────

@app.route('/')
def index():
    """GET / — Painel principal com as últimas 10 leituras e estatísticas."""
    leituras = listar_leituras(limite=10)
    stats    = estatisticas(horas=24)
    grafico  = leituras_para_grafico(limite=30)
    return render_template('index.html', leituras=leituras, stats=stats, grafico=grafico)


# ─── CRUD de Leituras ───────────────────────────────────────────────────────

@app.route('/leituras', methods=['GET'])
def listar():
    """GET /leituras — Histórico completo com paginação."""
    try:
        pagina = int(request.args.get('pagina', 1))
        por_pagina = int(request.args.get('por_pagina', 20))
    except ValueError:
        pagina, por_pagina = 1, 20

    pagina = max(1, pagina)
    offset = (pagina - 1) * por_pagina
    leituras = listar_leituras(limite=por_pagina, offset=offset)
    total    = contar_leituras()
    total_paginas = max(1, -(-total // por_pagina))  # teto

    # Suporte a resposta JSON
    if request.args.get('formato') == 'json' or request.is_json:
        return jsonify({
            'leituras': leituras,
            'pagina': pagina,
            'total': total,
            'total_paginas': total_paginas
        })

    return render_template('historico.html',
                           leituras=leituras,
                           pagina=pagina,
                           total=total,
                           total_paginas=total_paginas,
                           por_pagina=por_pagina)


@app.route('/leituras', methods=['POST'])
def criar():
    """POST /leituras — Recebe JSON do Arduino/simulador e persiste no banco."""
    dados = request.get_json(silent=True)
    if not dados:
        return jsonify({'erro': 'JSON inválido ou ausente'}), 400

    temp = dados.get('temperatura')
    umid = dados.get('umidade')

    if temp is None or umid is None:
        return jsonify({'erro': 'Campos obrigatórios: temperatura, umidade'}), 422

    try:
        temp = float(temp)
        umid = float(umid)
    except (TypeError, ValueError):
        return jsonify({'erro': 'temperatura e umidade devem ser números'}), 422

    pressao    = dados.get('pressao')
    localizacao = dados.get('localizacao', 'Lab IoT - Inteli')

    novo_id = inserir_leitura(temp, umid, pressao, localizacao)
    return jsonify({'id': novo_id, 'status': 'criado'}), 201


@app.route('/leituras/<int:id>', methods=['GET'])
def detalhe(id):
    """GET /leituras/<id> — Exibe uma leitura específica."""
    leitura = buscar_leitura(id)
    if not leitura:
        if request.args.get('formato') == 'json':
            return jsonify({'erro': 'Leitura não encontrada'}), 404
        abort(404)

    if request.args.get('formato') == 'json':
        return jsonify(leitura)

    return render_template('detalhe.html', leitura=leitura)


@app.route('/leituras/<int:id>/editar', methods=['GET'])
def editar_form(id):
    """GET /leituras/<id>/editar — Formulário de edição pré-preenchido."""
    leitura = buscar_leitura(id)
    if not leitura:
        abort(404)
    return render_template('editar.html', leitura=leitura)


@app.route('/leituras/<int:id>', methods=['PUT', 'POST'])
def atualizar(id):
    """
    PUT /leituras/<id> — Atualiza campos de uma leitura.
    Aceita JSON (PUT) ou form data com _method=PUT (POST do HTML).
    """
    # Suporte a method override via form (_method=PUT)
    method_override = request.form.get('_method', '').upper()

    if request.is_json:
        dados = request.get_json(silent=True) or {}
    else:
        dados = {
            'temperatura': request.form.get('temperatura'),
            'umidade':     request.form.get('umidade'),
            'pressao':     request.form.get('pressao') or None,
            'localizacao': request.form.get('localizacao'),
        }
        dados = {k: v for k, v in dados.items() if v is not None}

    if not dados:
        if request.is_json:
            return jsonify({'erro': 'Nenhum campo para atualizar'}), 400
        return redirect(url_for('editar_form', id=id))

    # Converte tipos
    for campo in ('temperatura', 'umidade', 'pressao'):
        if campo in dados and dados[campo] is not None:
            try:
                dados[campo] = float(dados[campo])
            except (TypeError, ValueError):
                if request.is_json:
                    return jsonify({'erro': f'{campo} deve ser um número'}), 422

    ok = atualizar_leitura(id, dados)
    if not ok:
        if request.is_json:
            return jsonify({'erro': 'Leitura não encontrada'}), 404
        abort(404)

    if request.is_json:
        return jsonify({'status': 'atualizado', 'id': id})

    return redirect(url_for('listar'))


@app.route('/leituras/<int:id>/deletar', methods=['POST'])
def deletar_form(id):
    """POST /leituras/<id>/deletar — Remove via formulário HTML."""
    ok = deletar_leitura(id)
    if not ok:
        abort(404)
    return redirect(url_for('listar'))


@app.route('/leituras/<int:id>', methods=['DELETE'])
def deletar(id):
    """DELETE /leituras/<id> — Remove via API REST."""
    ok = deletar_leitura(id)
    if not ok:
        return jsonify({'erro': 'Leitura não encontrada'}), 404
    return jsonify({'status': 'deletado', 'id': id})


# ─── Estatísticas ───────────────────────────────────────────────────────────

@app.route('/api/estatisticas', methods=['GET'])
def stats():
    """GET /api/estatisticas — Média, mín e máx do período (padrão: 24h)."""
    try:
        horas = int(request.args.get('horas', 24))
    except ValueError:
        horas = 24
    dados = estatisticas(horas=horas)
    return jsonify(dados)


@app.route('/api/grafico', methods=['GET'])
def grafico_dados():
    """GET /api/grafico — Dados para o gráfico temporal."""
    try:
        limite = int(request.args.get('limite', 50))
    except ValueError:
        limite = 50
    dados = leituras_para_grafico(limite=limite)
    return jsonify(dados)


# ─── Erro handlers ──────────────────────────────────────────────────────────

@app.errorhandler(404)
def nao_encontrado(e):
    if request.is_json or request.path.startswith('/api/'):
        return jsonify({'erro': 'Recurso não encontrado'}), 404
    return render_template('404.html'), 404


# ─── Ponto de entrada ───────────────────────────────────────────────────────

if __name__ == '__main__':
    init_db()
    print(f"[FLASK] Servidor iniciando na porta {FLASK_PORT}...")
    app.run(debug=FLASK_DEBUG, port=FLASK_PORT)
