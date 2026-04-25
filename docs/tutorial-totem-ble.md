# Tutorial do Totem BLE (Windows + WSL + Python)

Este tutorial descreve como o projeto funciona hoje, como executar e como evoluir o MVP.

## 1. Visão geral da arquitetura

No cenário deste projeto, o ESP32 atua como **beacon BLE** e anuncia pacotes com **Service Data**.

O sistema foi dividido em 2 processos Python:

1. `windows_scanner.py` (executa no Windows): escuta anúncios BLE, filtra pelo `SERVICE_UUID` e envia cada evento para o totem via HTTP.
2. `wsl_totem.py` (executa no WSL/Linux): recebe eventos e mantém estado de presença (`online/offline`).

## 2. Estrutura dos arquivos

No diretório `ble-totem/`:

- `windows_scanner.py`: scanner BLE com `bleak`.
- `wsl_totem.py`: API com `FastAPI` e controle de presença.

## 3. Pré-requisitos

### Windows (scanner)

- Python 3.10+
- Bluetooth BLE habilitado no computador
- Pacotes:
  - `bleak`

### WSL/Linux (totem)

- Python 3.10+
- Pacotes:
  - `fastapi`
  - `uvicorn`

## 4. Configuração de ambiente

## 4.1. Windows (scanner)

No PowerShell/cmd, dentro da pasta do projeto:

```bash
python -m venv .venv-win
.venv-win\Scripts\activate
pip install bleak
```

## 4.2. WSL (totem)

No terminal WSL, dentro da pasta do projeto:

```bash
python3 -m venv .venv-wsl
source .venv-wsl/bin/activate
pip install fastapi uvicorn
```

## 5. Como executar

## 5.1. Subir o totem no WSL

Na pasta `ble-totem/`:

```bash
source .venv-wsl/bin/activate
uvicorn wsl_totem:app --host 0.0.0.0 --port 8000 --reload
```

Endpoints disponíveis:

- `POST /ingest`: recebe evento de beacon.
- `GET /status/{beacon_id}`: retorna presença do beacon.

Exemplo de teste manual:

```bash
curl -X POST http://127.0.0.1:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{"beacon_id":"esp32-01","service_uuid":"12345678-1234-5678-1234-56789abcdef0","payload_hex":"0100000001","rssi":-62,"timestamp":"2026-01-01T00:00:00Z"}'
```

Depois:

```bash
curl http://127.0.0.1:8000/status/esp32-01
```

## 5.2. Rodar scanner BLE no Windows

Na pasta `ble-totem/`:

```bash
.venv-win\Scripts\activate
python windows_scanner.py
```

Se encontrar anúncios com o UUID configurado, o scanner imprime mudanças de estado:

- `NO RAIO`: beacon considerado dentro do raio.
- `FORA DO RAIO`: beacon fora do raio (RSSI fraco ou timeout sem novos pacotes).
- Se o encaminhamento estiver ativado: `Enviado ao totem` / `Totem indisponível`.

## 5.3. Configurar o raio no scanner

No arquivo `windows_scanner.py`, ajuste estes parâmetros:

```python
RSSI_ENTER_THRESHOLD = -75
RSSI_EXIT_THRESHOLD = -80
PRESENCE_TIMEOUT_SECONDS = 5
ENABLE_TOTEM_FORWARDING = False
TOTEM_INGEST_URL = "http://127.0.0.1:8000/ingest"
```

Como interpretar:

- `RSSI_ENTER_THRESHOLD`: valor mínimo para entrar no raio.
- `RSSI_EXIT_THRESHOLD`: valor para sair do raio (histerese para evitar oscilação).
- `PRESENCE_TIMEOUT_SECONDS`: se não chegar novo pacote nesse tempo, marca fora do raio.
- `ENABLE_TOTEM_FORWARDING`: `False` para modo local (somente terminal do Windows), `True` para enviar ao totem.
- `TOTEM_INGEST_URL`: URL HTTP do totem no WSL (usado apenas quando forwarding está `True`).

Exemplo prático:

- Mais sensível (raio maior): `-80 / -85`.
- Mais restrito (raio menor): `-70 / -75`.

## 6. Como o sistema funciona

1. O ESP32 anuncia pacotes BLE com `Service Data`.
2. O scanner no Windows captura os anúncios.
3. O scanner filtra por `SERVICE_UUID`.
4. O scanner envia cada evento para `POST /ingest` no totem.
5. O totem imprime `[INGEST]` no terminal para confirmar recebimento.
6. O totem mantém o último horário por `beacon_id`.
7. Se o último evento tiver menos de 5 segundos, status `online`; caso contrário, `offline`.

## 7. Configuração do UUID

No arquivo `windows_scanner.py`, ajuste:

```python
SERVICE_UUID = "12345678-1234-5678-1234-56789abcdef0"
```

Esse valor deve ser o mesmo UUID de serviço anunciado no ESP32.

## 8. Formato de payload (recomendado para evoluir)

Para padronizar parse entre ESP32 e totem, use algo como:

- `ver` (1 byte)
- `beacon_id` (4 bytes)
- `tipo` (1 byte)
- `valor` (2 bytes)

Exemplo de payload: `01 00 00 00 01 02 00 64`

## 9. Confirmação de recebimento do sinal

Com os dois processos rodando:

1. No terminal do scanner (Windows), você deve ver `Enviado ao totem`.
2. No terminal do totem (WSL), você deve ver `[INGEST] beacon=...`.

Se aparecer `Totem indisponível`, verifique host/porta em `TOTEM_INGEST_URL` e se o `uvicorn` está ativo.

## 10. Solução de problemas comuns

- Não detecta beacon:
  - confirme Bluetooth ligado no Windows;
  - confirme que o ESP32 está anunciando;
  - confirme UUID correto.
- API não responde:
  - verifique `uvicorn` ativo na porta 8000;
  - teste com `curl` local no WSL.
- Status sempre offline:
  - confirme que `/ingest` está sendo chamado com o `beacon_id` esperado.
