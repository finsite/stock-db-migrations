"""Handles writing to Postgres and InfluxDB, with optional dry-run mode."""

import os
from typing import Any
import psycopg2
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from app.config_shared import get_config_value
from app.utils.setup_logger import setup_logger

logger = setup_logger(__name__)
DRY_RUN = get_config_value("DRY_RUN", "false").lower() == "true"

# -------------------------------
# PostgreSQL Writer
# -------------------------------

def write_to_postgres(data: dict[str, Any]) -> None:
    """Write a single row to PostgreSQL or log it in dry-run mode."""
    if DRY_RUN:
        logger.info("🧪 [DRY-RUN] Would write to PostgreSQL: %s", data)
        return

    try:
        conn = psycopg2.connect(
            host=get_config_value("PG_WRITE_HOST", "localhost"),
            port=int(get_config_value("PG_WRITE_PORT", "5432")),
            dbname=get_config_value("PG_WRITE_DB", "postgres"),
            user=get_config_value("PG_WRITE_USER", "postgres"),
            password=get_config_value("PG_WRITE_PASSWORD", "postgres"),
        )
        with conn:
            with conn.cursor() as cur:
                # Example insert; adjust as needed
                cur.execute(
                    "INSERT INTO my_table (timestamp, value) VALUES (%s, %s)",
                    (data.get("timestamp"), data.get("value")),
                )
        logger.info("✅ Wrote row to PostgreSQL")
    except Exception as e:
        logger.exception("❌ Error writing to PostgreSQL: %s", e)
    finally:
        if 'conn' in locals():
            conn.close()

# -------------------------------
# InfluxDB Writer
# -------------------------------

def write_to_influx(data: dict[str, Any]) -> None:
    """Write a single row to InfluxDB or log it in dry-run mode."""
    if DRY_RUN:
        logger.info("🧪 [DRY-RUN] Would write to InfluxDB: %s", data)
        return

    try:
        bucket = get_config_value("INFLUX_BUCKET", "my_bucket")
        org = get_config_value("INFLUX_ORG", "my_org")
        token = get_config_value("INFLUX_TOKEN", "")
        url = get_config_value("INFLUX_URL", "http://localhost:8086")

        client = InfluxDBClient(url=url, token=token, org=org)
        write_api = client.write_api(write_options=SYNCHRONOUS)

        point = Point("my_measurement").tag("source", "migration")
        for key, value in data.items():
            if key == "timestamp":
                point.time(value, WritePrecision.NS)
            else:
                point.field(key, value)

        write_api.write(bucket=bucket, org=org, record=point)
        logger.info("✅ Wrote row to InfluxDB")

    except Exception as e:
        logger.exception("❌ Error writing to InfluxDB: %s", e)
