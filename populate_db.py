"""
populate_db.py
--------------
Popula o banco de dados com 50 leituras simuladas distribuídas
nas últimas 24 horas, para demonstração e testes.

Decisão arquitetural: usamos dados mockados pois não dispomos
de hardware físico (Arduino/ESP32) no momento. Ver README.
"""

import sys
import os
import math
import random
import sqlite3
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from database import init_db, DB_PATH

def popular():
    init_db()
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.execute('PRAGMA journal_mode=WAL')

    agora = datetime.now()
    total = 50

    print(f"[POPULATE] Gerando {total} leituras mockadas...")

    for i in range(total):
        # Distribui leituras nas últimas 24h
        minutos_atras = int((total - i) * (24 * 60 / total))
        ts = agora - timedelta(minutes=minutos_atras)

        hora = ts.hour + ts.minute / 60.0

        # Temperatura: oscila entre 18°C e 33°C com padrão senoidal diário
        temp_base = 25 + 8 * math.sin((hora - 6) * math.pi / 12)
        temperatura = round(temp_base + random.gauss(0, 0.6), 1)
        temperatura = max(15.0, min(40.0, temperatura))

        # Umidade: inversamente proporcional à temperatura
        umid_base = 72 - 22 * math.sin((hora - 6) * math.pi / 12)
        umidade = round(umid_base + random.gauss(0, 1.8), 1)
        umidade = max(20.0, min(100.0, umidade))

        # Pressão: varia suavemente ao redor de 1013 hPa
        pressao = round(1013 + 5 * math.sin(hora * math.pi / 8) + random.gauss(0, 1.2), 1)

        localizacao = random.choice([
            'Lab IoT - Inteli',
            'Lab IoT - Inteli',
            'Lab IoT - Inteli',
            'Área Externa',
            'Sala de Servidores',
        ])

        ts_str = ts.strftime('%Y-%m-%d %H:%M:%S')

        conn.execute(
            'INSERT INTO leituras (temperatura, umidade, pressao, localizacao, timestamp) VALUES (?, ?, ?, ?, ?)',
            (temperatura, umidade, pressao, localizacao, ts_str)
        )

    conn.commit()
    count = conn.execute('SELECT COUNT(*) FROM leituras').fetchone()[0]
    conn.close()
    print(f"[POPULATE] ✓ {count} leituras no banco: {DB_PATH}")

if __name__ == '__main__':
    popular()
