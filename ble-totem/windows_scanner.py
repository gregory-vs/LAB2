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

SERVICE_UUID = "12345678-1234-1234-1234-1234567890ab"

RSSI_RANGE_THRESHOLD = -75

PRESENCE_TIMEOUT_SECONDS = 15

ENABLE_TOTEM_FORWARDING = False

TOTEM_INGEST_URL = "http://127.0.0.1:8000/ingest"


# =========================================================
# MEMÓRIA LOCAL
# =========================================================

LAST_SEEN: dict[str, datetime] = {}

LAST_RSSI: dict[str, int] = {}

IN_RANGE: dict[str, list[bool]] = {}

EVENT_QUEUE: asyncio.Queue[dict[str, str | int]] = asyncio.Queue(maxsize=500)


# =========================================================
# UTILITÁRIOS
# =========================================================

def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


# =========================================================
# BANCO DE DADOS
# =========================================================

def salvar_evento(
    beacon_id: str,
    rssi: int,
    payload_hex: str,
) -> None:
    """
    Salva evento BLE no PostgreSQL.
    """

    query = text("""
        INSERT INTO beacon_eventos (
            totem_id,
            beacon_id,
            rssi,
            payload_hex,
            timestamp
        )
        VALUES (
            :totem_id,
            :beacon_id,
            :rssi,
            :payload_hex,
            :timestamp
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
                    "payload_hex": payload_hex,
                    "timestamp": datetime.now(timezone.utc),
                },
            )

        print(
            f"[{_iso_now()}] Evento salvo no banco | "
            f"totem={TOTEM_ID} beacon={beacon_id} rssi={rssi}"
        )

    except Exception as exc:
        print(f"[ERRO BANCO] {exc}")


# =========================================================
# CONTROLE DE PRESENÇA
# =========================================================

def _update_range_state(
    beacon_key: str,
    in_range: bool,
    rssi: int,
    reason: str,
) -> None:

    if beacon_key not in IN_RANGE:
        IN_RANGE[beacon_key] = []

    IN_RANGE[beacon_key].append(in_range)

    # mantém últimos 5 estados
    IN_RANGE[beacon_key] = IN_RANGE[beacon_key][-5:]

    historico = IN_RANGE[beacon_key]

    if in_range:
        state_text = "NO RAIO"
    else:
        state_text = "FORA DO RAIO"

    print(
        f"[{_iso_now()}] "
        f"Beacon {beacon_key}: {state_text} "
        f"(RSSI={rssi} dBm, motivo={reason})"
    )

    ultimos_5 = historico[-5:]

    todos_iguais = (
        len(ultimos_5) == 5
        and all(valor == ultimos_5[0] for valor in ultimos_5)
    )

    print(f"Histórico {beacon_key}: {ultimos_5}")
    print(f"Últimos 5 iguais? {todos_iguais}")

    if todos_iguais:
        if ultimos_5[0] is True:
            print(f"Beacon {beacon_key}: DEVOLUÇÃO CONFIRMADA")
        else:
            print(f"Beacon {beacon_key}: RETIRADA/SAÍDA CONFIRMADA")


# =========================================================
# FILA DE EVENTOS
# =========================================================

def _enqueue_event(event: dict[str, str | int]) -> None:

    if not ENABLE_TOTEM_FORWARDING:
        return

    try:
        EVENT_QUEUE.put_nowait(event)

    except asyncio.QueueFull:
        print(
            f"[{_iso_now()}] "
            f"Fila cheia, evento descartado: "
            f"beacon={event['beacon_id']}"
        )


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
        response_body = response.read().decode(
            "utf-8",
            errors="replace",
        )

    return status_code, response_body


# =========================================================
# CALLBACK BLE
# =========================================================

def _detection_callback(device, advertisement_data) -> None:

    service_data = advertisement_data.service_data or {}

    if SERVICE_UUID not in service_data:
        return

    payload = service_data[SERVICE_UUID]

    beacon_key = device.address or "<unknown-address>"

    rssi = advertisement_data.rssi

    payload_hex = payload.hex()

    LAST_SEEN[beacon_key] = datetime.now(timezone.utc)

    LAST_RSSI[beacon_key] = rssi

    in_range = rssi >= RSSI_RANGE_THRESHOLD

    _update_range_state(
        beacon_key,
        in_range,
        rssi,
        reason=f"service_data={payload_hex}",
    )

    # ==========================================
    # SALVA NO BANCO
    # ==========================================

    salvar_evento(
        beacon_id=beacon_key,
        rssi=rssi,
        payload_hex=payload_hex,
    )

    # ==========================================
    # ENCAMINHAMENTO OPCIONAL
    # ==========================================

    _enqueue_event(
        {
            "beacon_id": beacon_key,
            "service_uuid": SERVICE_UUID,
            "payload_hex": payload_hex,
            "rssi": rssi,
            "timestamp": _iso_now(),
        }
    )


# =========================================================
# WATCHDOG DE PRESENÇA
# =========================================================

async def _presence_watchdog() -> None:

    while True:

        now = datetime.now(timezone.utc)

        for beacon_key, last_seen in list(LAST_SEEN.items()):

            age = (now - last_seen).total_seconds()

            if (
                age >= PRESENCE_TIMEOUT_SECONDS
                and IN_RANGE.get(beacon_key, False)
            ):

                rssi = LAST_RSSI.get(beacon_key, -999)

                _update_range_state(
                    beacon_key,
                    False,
                    rssi,
                    reason=f"timeout>{PRESENCE_TIMEOUT_SECONDS}s",
                )

        await asyncio.sleep(1)


# =========================================================
# WORKER HTTP
# =========================================================

async def _sender_worker() -> None:

    while True:

        event = await EVENT_QUEUE.get()

        try:

            status_code, _ = await asyncio.to_thread(
                _post_event_sync,
                TOTEM_INGEST_URL,
                event,
            )

            if 200 <= status_code < 300:

                print(
                    f"[{_iso_now()}] "
                    f"Enviado ao totem: "
                    f"beacon={event['beacon_id']} "
                    f"rssi={event['rssi']} "
                    f"status_http={status_code}"
                )

            else:

                print(
                    f"[{_iso_now()}] "
                    f"Falha ao enviar ao totem: "
                    f"beacon={event['beacon_id']} "
                    f"status_http={status_code}"
                )

        except (error.URLError, TimeoutError) as exc:

            print(
                f"[{_iso_now()}] "
                f"Totem indisponível em "
                f"{TOTEM_INGEST_URL}: {exc}"
            )

        finally:
            EVENT_QUEUE.task_done()


# =========================================================
# MAIN
# =========================================================

async def main() -> None:

    scanner = BleakScanner(
        detection_callback=_detection_callback
    )

    await scanner.start()

    print(
        "Scanner BLE iniciado. "
        f"RANGE>={RSSI_RANGE_THRESHOLD} dBm, "
        f"timeout={PRESENCE_TIMEOUT_SECONDS}s, "
        f"forwarding={'ON' if ENABLE_TOTEM_FORWARDING else 'OFF'}."
    )

    watchdog = asyncio.create_task(
        _presence_watchdog()
    )

    sender = None

    if ENABLE_TOTEM_FORWARDING:

        print(
            f"[{_iso_now()}] "
            f"Encaminhando eventos para: "
            f"{TOTEM_INGEST_URL}"
        )

        sender = asyncio.create_task(
            _sender_worker()
        )

    try:

        while True:
            await asyncio.sleep(1)

    finally:

        watchdog.cancel()

        if sender is not None:
            sender.cancel()

        await scanner.stop()


# =========================================================
# ENTRYPOINT
# =========================================================

if __name__ == "__main__":
    asyncio.run(main())