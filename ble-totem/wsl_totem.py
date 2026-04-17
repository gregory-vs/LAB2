"""
Totem (WSL) para receber eventos BLE e manter status de presença.
"""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI(title="BLE Totem")
LAST_SEEN: dict[str, datetime] = {}
ONLINE_TIMEOUT_SECONDS = 5


class BeaconEvent(BaseModel):
    beacon_id: str
    service_uuid: str
    payload_hex: str
    rssi: int
    timestamp: str


@app.post("/ingest")
def ingest(event: BeaconEvent) -> dict[str, str]:
    LAST_SEEN[event.beacon_id] = datetime.now(timezone.utc)
    print(
        f"[INGEST] beacon={event.beacon_id} rssi={event.rssi} "
        f"uuid={event.service_uuid} payload={event.payload_hex}"
    )
    return {"status": "ok"}


@app.get("/status/{beacon_id}")
def status(beacon_id: str) -> dict[str, str | int]:
    now = datetime.now(timezone.utc)
    last = LAST_SEEN.get(beacon_id)
    if not last:
        return {"beacon_id": beacon_id, "state": "offline", "seconds_since_last": -1}

    age = int((now - last).total_seconds())
    state = "online" if age < ONLINE_TIMEOUT_SECONDS else "offline"
    return {"beacon_id": beacon_id, "state": state, "seconds_since_last": age}
