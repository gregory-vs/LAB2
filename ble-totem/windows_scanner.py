"""
Scanner BLE (Windows) para capturar Service Data e encaminhar ao totem no WSL.
"""

from __future__ import annotations

import asyncio
import json
from collections.abc import Mapping
from datetime import datetime, timezone
from urllib import error, request

from bleak import BleakScanner


SERVICE_UUID = "12345678-1234-1234-1234-1234567890ab"
RSSI_ENTER_THRESHOLD = -75
RSSI_EXIT_THRESHOLD = -80
PRESENCE_TIMEOUT_SECONDS = 5
TOTEM_INGEST_URL = "http://127.0.0.1:8000/ingest"

LAST_SEEN: dict[str, datetime] = {}
LAST_RSSI: dict[str, int] = {}
IN_RANGE: dict[str, bool] = {}
EVENT_QUEUE: asyncio.Queue[dict[str, str | int]] = asyncio.Queue(maxsize=500)


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _update_range_state(beacon_key: str, in_range: bool, rssi: int, reason: str) -> None:
    previous = IN_RANGE.get(beacon_key)
    IN_RANGE[beacon_key] = in_range

    if previous is None or previous != in_range:
        state_text = "NO RAIO" if in_range else "FORA DO RAIO"
        print(
            f"[{_iso_now()}] Beacon {beacon_key}: {state_text} "
            f"(RSSI={rssi} dBm, motivo={reason})"
        )


def _enqueue_event(event: dict[str, str | int]) -> None:
    try:
        EVENT_QUEUE.put_nowait(event)
    except asyncio.QueueFull:
        print(f"[{_iso_now()}] Fila cheia, evento descartado: beacon={event['beacon_id']}")


def _post_event_sync(url: str, event: Mapping[str, str | int]) -> tuple[int, str]:
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


def _detection_callback(device, advertisement_data) -> None:
    service_data = advertisement_data.service_data or {}
    if SERVICE_UUID not in service_data:
        return

    payload = service_data[SERVICE_UUID]
    beacon_key = device.address or "<unknown-address>"
    rssi = advertisement_data.rssi
    LAST_SEEN[beacon_key] = datetime.now(timezone.utc)
    LAST_RSSI[beacon_key] = rssi

    was_in_range = IN_RANGE.get(beacon_key, False)
    if was_in_range:
        in_range = rssi >= RSSI_EXIT_THRESHOLD
    else:
        in_range = rssi >= RSSI_ENTER_THRESHOLD

    _update_range_state(beacon_key, in_range, rssi, reason=f"service_data={payload.hex()}")
    _enqueue_event(
        {
            "beacon_id": beacon_key,
            "service_uuid": SERVICE_UUID,
            "payload_hex": payload.hex(),
            "rssi": rssi,
            "timestamp": _iso_now(),
        }
    )


async def _presence_watchdog() -> None:
    while True:
        now = datetime.now(timezone.utc)
        for beacon_key, last_seen in list(LAST_SEEN.items()):
            age = (now - last_seen).total_seconds()
            if age >= PRESENCE_TIMEOUT_SECONDS and IN_RANGE.get(beacon_key, False):
                rssi = LAST_RSSI.get(beacon_key, -999)
                _update_range_state(
                    beacon_key,
                    False,
                    rssi,
                    reason=f"timeout>{PRESENCE_TIMEOUT_SECONDS}s",
                )
        await asyncio.sleep(1)


async def _sender_worker() -> None:
    while True:
        event = await EVENT_QUEUE.get()
        try:
            status_code, _ = await asyncio.to_thread(_post_event_sync, TOTEM_INGEST_URL, event)
            if 200 <= status_code < 300:
                print(
                    f"[{_iso_now()}] Enviado ao totem: beacon={event['beacon_id']} "
                    f"rssi={event['rssi']} status_http={status_code}"
                )
            else:
                print(
                    f"[{_iso_now()}] Falha ao enviar ao totem: beacon={event['beacon_id']} "
                    f"status_http={status_code}"
                )
        except (error.URLError, TimeoutError) as exc:
            print(f"[{_iso_now()}] Totem indisponível em {TOTEM_INGEST_URL}: {exc}")
        finally:
            EVENT_QUEUE.task_done()


async def main() -> None:
    scanner = BleakScanner(detection_callback=_detection_callback)
    await scanner.start()
    print(
        "Scanner BLE iniciado. "
        f"ENTER>={RSSI_ENTER_THRESHOLD} dBm, "
        f"EXIT>={RSSI_EXIT_THRESHOLD} dBm, "
        f"timeout={PRESENCE_TIMEOUT_SECONDS}s, "
        f"totem={TOTEM_INGEST_URL}. "
        "Pressione Ctrl+C para parar."
    )
    watchdog = asyncio.create_task(_presence_watchdog())
    sender = asyncio.create_task(_sender_worker())
    try:
        while True:
            await asyncio.sleep(1)
    finally:
        watchdog.cancel()
        sender.cancel()
        await scanner.stop()


if __name__ == "__main__":
    asyncio.run(main())
