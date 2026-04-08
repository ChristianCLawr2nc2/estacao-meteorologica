import os

# Serial / Arduino
PORTA_SERIAL = os.getenv('PORTA_SERIAL', 'COM3')   # Windows: COM3 | Linux: /dev/ttyUSB0
BAUD_RATE    = int(os.getenv('BAUD_RATE', 9600))

# API
API_URL = os.getenv('API_URL', 'http://localhost:5000/leituras')

# Flask
FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'true').lower() == 'true'
FLASK_PORT  = int(os.getenv('FLASK_PORT', 5000))

# Simulador (usado quando não há Arduino físico)
INTERVALO_SIMULACAO = int(os.getenv('INTERVALO_SIMULACAO', 5))  # segundos
