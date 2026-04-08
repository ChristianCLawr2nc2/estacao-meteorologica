"""
serial_reader.py
----------------
Lê dados do Arduino via porta serial e envia para a API Flask via POST.

MODO SIMULAÇÃO (padrão):
    Quando MODE=simular (ou sem Arduino físico conectado), gera leituras
    aleatórias realistas a cada INTERVALO_SIMULACAO segundos.

MODO SERIAL (Arduino físico):
    Define MODE=serial e ajuste PORTA_SERIAL em config.py ou via variável
    de ambiente.

Decisão arquitetural: optamos pelo modo simulação pois não dispomos de
hardware físico no momento de desenvolvimento. Ver README para detalhes.
"""

import json
import time
import random
import math
import requests
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from config import PORTA_SERIAL, BAUD_RATE, API_URL, INTERVALO_SIMULACAO

MODE = os.getenv('MODE', 'simular')  # 'simular' | 'serial'


# ──────────────────────────────────────────────
# Gerador de dados simulados
# ──────────────────────────────────────────────

def _gerar_leitura_simulada(tick: int) -> dict:
    """
    Gera valores realistas usando uma senoide com ruído gaussiano,
    simulando variação natural ao longo do dia.
    """
    hora_do_dia = (tick * INTERVALO_SIMULACAO / 3600) % 24
    # Temperatura oscila entre 18°C e 32°C ao longo do dia
    temp_base = 25 + 7 * math.sin((hora_do_dia - 6) * math.pi / 12)
    temperatura = round(temp_base + random.gauss(0, 0.5), 1)

    # Umidade inversamente relacionada à temperatura (típico)
    umid_base = 70 - 20 * math.sin((hora_do_dia - 6) * math.pi / 12)
    umidade = round(max(20, min(100, umid_base + random.gauss(0, 1.5))), 1)

    # Pressão atmosférica ao redor de 1013 hPa com pequena variação
    pressao = round(1013 + random.gauss(0, 2), 1)

    return {
        'temperatura': temperatura,
        'umidade': umidade,
        'pressao': pressao,
        'localizacao': 'Lab IoT - Inteli'
    }


def _enviar(dados: dict) -> None:
    """Envia os dados para a API via POST."""
    try:
        resp = requests.post(API_URL, json=dados, timeout=5)
        print(f"[SIMULADOR] Enviado: {dados} → HTTP {resp.status_code}")
    except requests.exceptions.ConnectionError:
        print("[SIMULADOR] AVISO: API não está disponível. Tentando novamente...")
    except Exception as e:
        print(f"[SIMULADOR] Erro ao enviar: {e}")


# ──────────────────────────────────────────────
# Modo serial (Arduino físico)
# ──────────────────────────────────────────────

def ler_serial() -> None:
    """Lê a porta serial do Arduino e encaminha os dados para a API."""
    try:
        import serial
    except ImportError:
        print("[SERIAL] pyserial não instalado. Execute: pip install pyserial")
        return

    print(f"[SERIAL] Conectando em {PORTA_SERIAL} @ {BAUD_RATE} baud...")
    try:
        with serial.Serial(PORTA_SERIAL, BAUD_RATE, timeout=2) as ser:
            print("[SERIAL] Conectado! Aguardando dados do Arduino...")
            while True:
                linha = ser.readline().decode('utf-8', errors='ignore').strip()
                if linha:
                    try:
                        dados = json.loads(linha)
                        _enviar(dados)
                    except json.JSONDecodeError:
                        print(f"[SERIAL] Linha inválida ignorada: {linha}")
                time.sleep(0.1)
    except Exception as e:
        print(f"[SERIAL] Erro de conexão: {e}")


# ──────────────────────────────────────────────
# Modo simulação
# ──────────────────────────────────────────────

def simular() -> None:
    """Gera e envia leituras simuladas indefinidamente."""
    print(f"[SIMULADOR] Iniciando simulação. Intervalo: {INTERVALO_SIMULACAO}s → {API_URL}")
    tick = 0
    while True:
        dados = _gerar_leitura_simulada(tick)
        _enviar(dados)
        tick += 1
        time.sleep(INTERVALO_SIMULACAO)


# ──────────────────────────────────────────────
# Ponto de entrada
# ──────────────────────────────────────────────

if __name__ == '__main__':
    if MODE == 'serial':
        ler_serial()
    else:
        simular()
