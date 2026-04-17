"""
Scanner BLE (Windows) para capturar Service Data e encaminhar ao totem no WSL.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone

from bleak import BleakScanner


SERVICE_UUID = "12345678-1234-1234-1234-1234567890ab"
RSSI_ENTER_THRESHOLD = -75
RSSI_EXIT_THRESHOLD = -80
PRESENCE_TIMEOUT_SECONDS = 5

LAST_SEEN: dict[str, datetime] = {}
LAST_RSSI: dict[str, int] = {}
IN_RANGE: dict[str, bool] = {}


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


async def main() -> None:
    scanner = BleakScanner(detection_callback=_detection_callback)
    await scanner.start()
    print(
        "Scanner BLE iniciado. "
        f"ENTER>={RSSI_ENTER_THRESHOLD} dBm, "
        f"EXIT>={RSSI_EXIT_THRESHOLD} dBm, "
        f"timeout={PRESENCE_TIMEOUT_SECONDS}s. "
        "Pressione Ctrl+C para parar."
    )
    watchdog = asyncio.create_task(_presence_watchdog())
    try:
        while True:
            await asyncio.sleep(1)
    finally:
        watchdog.cancel()
        await scanner.stop()


if __name__ == "__main__":
    asyncio.run(main())
