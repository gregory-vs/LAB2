CREATE INDEX IF NOT EXISTS idx_beacon_eventos_totem_beacon_created_at
    ON beacon_eventos (totem_id, beacon_id, created_at DESC);
