"""
Scanner BLE (Windows) com salvamento de eventos no PostgreSQL/Azure.
"""

from __future__ import annotations

import asyncio
import json
import os
from collections.abc import Mapping
from datetime import datetime, timezone
from urllib import error, request

from bleak import BleakScanner
from dotenv import load_dotenv
from sqlalchemy import create_engine, text


# =========================================================
# CONFIGURAÇÕES
# =========================================================

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL não encontrada no .env")

engine = create_engine(DATABASE_URL)

TOTEM_ID = "TOTEM_01"

RSSI_RANGE_THRESHOLD = -75

PRESENCE_TIMEOUT_SECONDS = 15

ENABLE_TOTEM_FORWARDING = False

TOTEM_INGEST_URL = "http://127.0.0.1:8000/ingest"

# =========================================================
# LISTA DE BEACONS PERMITIDOS (WHITELIST)
# =========================================================
# Coloque os UUIDs dos seus carrinhos aqui ou no arquivo .env separados por vírgula.
# Exemplo no .env: ALLOWED_BEACONS=12345678-1234-1234-1234-1234567890ab,abcdef12-3456-7890-abcd-ef1234567890
ALLOWED_BEACONS_STR = os.getenv(
    "ALLOWED_BEACONS", 
    "12345678-1234-1234-1234-1234567890ab,12345678-1234-1234-1234-4444444444ab"
)

# Converte a string em um Set (conjunto) para busca ultra-rápida, ignorando espaços e padronizando para minúsculo
ALLOWED_BEACONS: set[str] = {b.strip().lower() for b in ALLOWED_BEACONS_STR.split(",") if b.strip()}


# =========================================================
# MEMÓRIA LOCAL E ARRAY DE ESTADO
# =========================================================

LAST_SEEN: dict[str, datetime] = {}

LAST_RSSI: dict[str, int] = {}

IN_RANGE_HISTORY: dict[str, list[bool]] = {}

# ARRAY (Set) para armazenar os carrinhos atualmente confirmados no raio
CARTS_IN_RANGE: set[str] = set()

EVENT_QUEUE: asyncio.Queue[dict[str, str | int]] = asyncio.Queue(maxsize=500)


# =========================================================
# UTILITÁRIOS
# =========================================================

def _unix_now() -> int:
    """Retorna o timestamp atual no formato UNIX (inteiro)."""
    return int(datetime.now(timezone.utc).timestamp())


# =========================================================
# BANCO DE DADOS E FILA
# =========================================================

def salvar_evento(
    beacon_id: str,
    rssi: int,
    status: str,
) -> None:
    """
    Salva evento BLE no PostgreSQL. Roda em thread separada para não travar.
    """

    query = text("""
        INSERT INTO beacon_eventos (
            totem_id,
            beacon_id,
            rssi,
            timestamp,
            status
        )
        VALUES (
            :totem_id,
            :beacon_id,
            :rssi,
            :timestamp,
            :status
        )
    """)

    try:
        with engine.begin() as conn:
            conn.execute(
                query,
                {
                    "totem_id": TOTEM_ID,
                    "beacon_id": beacon_id,
                    "rssi": rssi,
                    "timestamp": _unix_now(),
                    "status": status,
                },
            )

        print(
            f"[{_unix_now()}] Evento salvo no banco | "
            f"totem={TOTEM_ID} beacon={beacon_id} rssi={rssi} status={status}"
        )

    except Exception as exc:
        print(f"[ERRO BANCO] {exc}")


def _enqueue_event(event: dict[str, str | int]) -> None:
    if not ENABLE_TOTEM_FORWARDING:
        return

    try:
        EVENT_QUEUE.put_nowait(event)
    except asyncio.QueueFull:
        print(f"[{_unix_now()}] Fila cheia, evento descartado: beacon={event['beacon_id']}")


def _post_event_sync(
    url: str,
    event: Mapping[str, str | int],
) -> tuple[int, str]:

    body = json.dumps(event).encode("utf-8")
    req = request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with request.urlopen(req, timeout=2) as response:
        status_code = response.getcode()
        response_body = response.read().decode("utf-8", errors="replace")

    return status_code, response_body


# =========================================================
# CONTROLE DE PRESENÇA (ARRAY E HISTÓRICO)
# =========================================================

def _update_range_state(
    beacon_key: str,
    in_range: bool,
    rssi: int,
    reason: str,
) -> None:
    """
    Atualiza o array e dispara o salvamento. 
    É síncrona para blindar o array contra Race Conditions!
    """
    if beacon_key not in IN_RANGE_HISTORY:
        IN_RANGE_HISTORY[beacon_key] = []

    # Adiciona a leitura atual e mantém apenas as últimas 5
    IN_RANGE_HISTORY[beacon_key].append(in_range)
    IN_RANGE_HISTORY[beacon_key] = IN_RANGE_HISTORY[beacon_key][-5:]

    historico = IN_RANGE_HISTORY[beacon_key]

    # Verifica as condições
    entregue_confirmado = len(historico) == 5 and all(historico)
    retirado_confirmado = len(historico) >= 4 and not any(historico[-4:])

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if entregue_confirmado:
        # Só executa se o carrinho AINDA NÃO estiver no array
        if beacon_key not in CARTS_IN_RANGE:
            CARTS_IN_RANGE.add(beacon_key) # Adiciona instantaneamente
            print(f"[{_unix_now()}] Beacon {beacon_key}: ADICIONADO AO ARRAY (ENTREGUE) | Motivo: {reason}")
            
            # Manda o salvamento para o fundo (thread)
            if loop:
                loop.run_in_executor(None, salvar_evento, beacon_key, rssi, "ENTREGUE")
            
            _enqueue_event({
                "beacon_id": beacon_key,
                "rssi": rssi,
                "timestamp": _unix_now(),
                "status": "ENTREGUE"
            })

    elif retirado_confirmado:
        # Só executa se o carrinho ESTIVER no array
        if beacon_key in CARTS_IN_RANGE:
            CARTS_IN_RANGE.remove(beacon_key) # Remove instantaneamente
            print(f"[{_unix_now()}] Beacon {beacon_key}: REMOVIDO DO ARRAY (RETIRADO) | Motivo: {reason}")
            
            # Manda o salvamento para o fundo (thread)
            if loop:
                loop.run_in_executor(None, salvar_evento, beacon_key, rssi, "RETIRADO")
            
            _enqueue_event({
                "beacon_id": beacon_key,
                "rssi": rssi,
                "timestamp": _unix_now(),
                "status": "RETIRADO"
            })


# =========================================================
# CALLBACK BLE
# =========================================================

def _detection_callback(device, advertisement_data) -> None:
    # Captura o UUID de forma robusta
    uuids = advertisement_data.service_uuids
    if not uuids and advertisement_data.service_data:
        uuids = list(advertisement_data.service_data.keys())
        
    if not uuids:
        return

    beacon_key = str(uuids[0]).lower()

    # ==========================================
    # VERIFICAÇÃO DA WHITELIST
    # ==========================================
    # Se a lista de permitidos estiver configurada e o dispositivo 
    # não estiver nela, ignoramos silenciosamente.
    if ALLOWED_BEACONS and beacon_key not in ALLOWED_BEACONS:
        return

    rssi = advertisement_data.rssi

    LAST_SEEN[beacon_key] = datetime.now(timezone.utc)
    LAST_RSSI[beacon_key] = rssi

    in_range = rssi >= RSSI_RANGE_THRESHOLD
    
    # Chama a verificação do array
    _update_range_state(
        beacon_key,
        in_range,
        rssi,
        reason="leitura_ble",
    )


# =========================================================
# WATCHDOG DE PRESENÇA
# =========================================================

async def _presence_watchdog() -> None:
    while True:
        now = datetime.now(timezone.utc)

        for beacon_key, last_seen in list(LAST_SEEN.items()):
            age = (now - last_seen).total_seconds()

            # Se ausente E ainda estiver no Array
            if age >= PRESENCE_TIMEOUT_SECONDS and beacon_key in CARTS_IN_RANGE:
                rssi = LAST_RSSI.get(beacon_key, -999)

                print(f"[{_unix_now()}] Beacon {beacon_key}: TIMEOUT EXCEDIDO (>{PRESENCE_TIMEOUT_SECONDS}s)")
                
                # Remove do array
                CARTS_IN_RANGE.remove(beacon_key)
                IN_RANGE_HISTORY[beacon_key] = [False] * 5

                # Envia ao banco em uma thread separada
                loop = asyncio.get_running_loop()
                loop.run_in_executor(None, salvar_evento, beacon_key, rssi, "RETIRADO")

                _enqueue_event({
                    "beacon_id": beacon_key,
                    "rssi": rssi,
                    "timestamp": _unix_now(),
                    "status": "RETIRADO"
                })

        await asyncio.sleep(1)


# =========================================================
# WORKER HTTP
# =========================================================

async def _sender_worker() -> None:
    while True:
        event = await EVENT_QUEUE.get()
        try:
            status_code, _ = await asyncio.to_thread(_post_event_sync, TOTEM_INGEST_URL, event)
            if 200 <= status_code < 300:
                print(f"[{_unix_now()}] Enviado ao totem: beacon={event['beacon_id']} rssi={event['rssi']} status_http={status_code}")
            else:
                print(f"[{_unix_now()}] Falha ao enviar ao totem: beacon={event['beacon_id']} status_http={status_code}")
        except (error.URLError, TimeoutError) as exc:
            print(f"[{_unix_now()}] Totem indisponível em {TOTEM_INGEST_URL}: {exc}")
        finally:
            EVENT_QUEUE.task_done()


# =========================================================
# MAIN
# =========================================================

async def main() -> None:
    print("Iniciando varredura BLE... Aguardando adaptador.")
    
    scanner = BleakScanner(detection_callback=_detection_callback)
    await scanner.start()

    print(
        "Scanner BLE iniciado com sucesso! "
        f"RANGE>={RSSI_RANGE_THRESHOLD} dBm, "
        f"timeout={PRESENCE_TIMEOUT_SECONDS}s, "
        f"forwarding={'ON' if ENABLE_TOTEM_FORWARDING else 'OFF'}."
    )
    print(f"Filtro ativo: Rastreiando {len(ALLOWED_BEACONS)} carrinho(s).")

    watchdog = asyncio.create_task(_presence_watchdog())
    sender = None

    if ENABLE_TOTEM_FORWARDING:
        print(f"[{_unix_now()}] Encaminhando eventos para: {TOTEM_INGEST_URL}")
        sender = asyncio.create_task(_sender_worker())

    try:
        while True:
            await asyncio.sleep(1)
    finally:
        watchdog.cancel()
        if sender is not None:
            sender.cancel()
        await scanner.stop()

if __name__ == "__main__":
    asyncio.run(main())
