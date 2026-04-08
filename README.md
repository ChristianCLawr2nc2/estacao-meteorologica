# 🌦 Estação Meteorológica IoT

**Engenharia de Computação — Módulo 5 | Automação de Processos e Sistemas**  
**Inteli — Instituto de Tecnologia e Liderança**

Sistema completo de IoT para coleta, armazenamento e visualização de dados meteorológicos (temperatura, umidade e pressão atmosférica), construído com Python, Flask, SQLite e interface web responsiva.

---

## 📐 Decisão de Arquitetura

A arquitetura proposta no enunciado é:

```
Arduino → Serial USB → serial_reader.py → POST → API Flask → SQLite → Interface Web
```

### O que foi implementado de forma diferente

| Componente | Proposta original | Nossa decisão |
|---|---|---|
| Arduino físico | DHT11 + BMP180 real | **Modo simulação** via `serial_reader.py` e `populate_db.py` |
| Leitura serial | `pyserial` conectado à porta COM/ttyUSB | Simulador Python que gera valores realistas sem hardware |
| Banco de dados | Populado em tempo real | Pré-populado com **50 leituras** de exemplo via script |
| Restante | — | Implementado conforme especificado |

**Justificativa:** o desenvolvimento foi realizado em ambiente sem acesso a hardware físico (Arduino/ESP32 + sensores). O simulador `serial_reader.py` (modo `MODE=simular`) gera dados com variação senoidal realista, reproduzindo o comportamento de temperatura e umidade ao longo do dia. Quando o hardware estiver disponível, basta definir `MODE=serial` e configurar a porta em `config.py`.

O sketch `arduino/estacao.ino` também possui `#define SIMULAR true` para testes sem sensores reais.

---

## 🗂 Estrutura do Projeto

```
estacao_meteorologica/
├── populate_db.py           # Script para popular o banco com leituras de exemplo
├── src/
│   ├── app.py               # Aplicação Flask principal (rotas e lógica HTTP)
│   ├── database.py          # Funções de acesso ao SQLite (CRUD + estatísticas)
│   ├── serial_reader.py     # Leitura serial / simulador de dados
│   ├── schema.sql           # DDL de criação das tabelas
│   ├── config.py            # Variáveis de configuração centralizadas
│   ├── dados.db             # Banco SQLite (gerado automaticamente)
│   ├── static/
│   │   ├── css/style.css    # Estilos (tema dark industrial)
│   │   └── js/main.js       # Lógica de interface e auto-refresh
│   ├── templates/
│   │   ├── base.html        # Layout base com navbar
│   │   ├── index.html       # Dashboard com gráfico e cards
│   │   ├── historico.html   # Tabela paginada de leituras
│   │   ├── editar.html      # Formulário de edição
│   │   ├── detalhe.html     # Detalhe de uma leitura
│   │   └── 404.html         # Página de erro
│   └── arduino/
│       └── estacao.ino      # Sketch Arduino (suporta modo simulação)
```

---

## ⚙️ Instalação

### Pré-requisitos

- Python 3.10 ou superior
- pip

### 1. Clone o repositório

```bash
git clone <URL_DO_REPOSITORIO>
cd estacao_meteorologica
```

### 2. Crie e ative o ambiente virtual

```bash
python -m venv venv

# Linux / macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Instale as dependências

```bash
pip install flask pyserial
```

### 4. Popule o banco com dados de exemplo

```bash
python populate_db.py
```

> Isso cria `src/dados.db` com **50 leituras** distribuídas nas últimas 24 horas.  
> Pule este passo se já houver um `dados.db` fornecido.

---

## ▶️ Execução

### Terminal 1 — Servidor Flask

```bash
cd src
python app.py
```

O servidor sobe em `http://localhost:5000`.

### Terminal 2 — Simulador de dados (opcional)

```bash
cd src
python serial_reader.py
```

Envia uma nova leitura a cada 5 segundos para a API.  
Para usar o Arduino físico, defina a variável de ambiente antes de executar:

```bash
# Linux/macOS
MODE=serial PORTA_SERIAL=/dev/ttyUSB0 python serial_reader.py

# Windows
set MODE=serial
set PORTA_SERIAL=COM3
python serial_reader.py
```

---

## 🌐 Rotas da API

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/` | Dashboard — últimas 10 leituras + gráfico |
| `GET` | `/leituras` | Histórico com paginação (`?pagina=1&por_pagina=20`) |
| `GET` | `/leituras?formato=json` | Histórico em JSON |
| `POST` | `/leituras` | Cria nova leitura (corpo JSON) |
| `GET` | `/leituras/<id>` | Detalhe de uma leitura (HTML) |
| `GET` | `/leituras/<id>?formato=json` | Detalhe em JSON |
| `GET` | `/leituras/<id>/editar` | Formulário de edição |
| `PUT` | `/leituras/<id>` | Atualiza uma leitura (JSON) |
| `DELETE` | `/leituras/<id>` | Remove uma leitura |
| `GET` | `/api/estatisticas` | Média, mín e máx (parâmetro `?horas=24`) |
| `GET` | `/api/grafico` | Dados para o gráfico temporal |

### Exemplos com curl

```bash
# Criar leitura
curl -X POST http://localhost:5000/leituras \
  -H "Content-Type: application/json" \
  -d '{"temperatura": 27.5, "umidade": 68.0, "pressao": 1012.3}'

# Listar em JSON
curl http://localhost:5000/leituras?formato=json

# Atualizar
curl -X PUT http://localhost:5000/leituras/5 \
  -H "Content-Type: application/json" \
  -d '{"temperatura": 26.1}'

# Deletar
curl -X DELETE http://localhost:5000/leituras/5

# Estatísticas das últimas 6h
curl http://localhost:5000/api/estatisticas?horas=6
```

---

## 🗄 Esquema do Banco de Dados

```sql
CREATE TABLE IF NOT EXISTS leituras (
    id          INTEGER  PRIMARY KEY AUTOINCREMENT,
    temperatura REAL     NOT NULL,
    umidade     REAL     NOT NULL,
    pressao     REAL,                              -- opcional
    localizacao TEXT     DEFAULT 'Lab IoT - Inteli',
    timestamp   DATETIME DEFAULT (datetime('now','localtime'))
);
```

**WAL mode** habilitado para suportar escrita simultânea do Flask e do simulador serial sem travar o banco.

---

## 📦 Dependências

| Pacote | Uso |
|---|---|
| `flask` | Servidor web e API REST |
| `pyserial` | Leitura da porta serial do Arduino |
| `sqlite3` | Persistência (nativa do Python) |
| `Chart.js 4.4` | Gráfico de variação temporal (CDN) |

---

## ✅ Critérios de Avaliação

| Critério | Status |
|---|---|
| Comunicação Arduino → Serial → API | ✅ Simulado via `serial_reader.py` |
| API REST completa (todos endpoints) | ✅ GET, POST, PUT, DELETE + estatísticas |
| Banco de dados — schema + CRUD | ✅ SQLite com WAL, 50 leituras de exemplo |
| Interface Web — painel, histórico, edição | ✅ Dashboard + tabela paginada + formulário |
| Gráfico de variação temporal | ✅ Chart.js com temperatura, umidade e pressão |
| README com instruções | ✅ Este arquivo |
| Organização e boas práticas | ✅ Módulos separados, config centralizada, tratamento de erros |
